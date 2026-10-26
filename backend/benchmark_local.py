"""Repeatable, offline BID OWL synthetic 10k-bid measurement.

No customer SQLite files, external APIs, installed fonts or network requests.
All source bid rows and assessments are generated in a TemporaryDirectory.
Results are timings, not a universal speed guarantee or product QA PASS.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
import time
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backup_recovery import prepare_recovery, restore_to_new_file
from bidowl import Bid, BidOwlStore, CompanyProfile, Requirement
from viewer import _latest_rows, open_database, query_bids, query_detail, query_favorites

SOURCE = "SYNTHETIC-PERF-ONLY"


def timed(name: str, task, results: dict):
    start = time.perf_counter()
    answer = task()
    results[name] = round((time.perf_counter() - start) * 1000, 2)
    return answer


def run_benchmark(*, records: int = 10000, assessed: int = 200,
                  measure_recovery: bool = False,
                  measure_viewer_baseline: bool = False) -> dict:
    if type(records) is not int or not 1 <= records <= 10000:
        raise ValueError("records must be an integer between 1 and 10000")
    if type(assessed) is not int or not 0 <= assessed <= records:
        raise ValueError("assessed must be an integer between 0 and records")
    if type(measure_recovery) is not bool:
        raise ValueError("measure_recovery must be a bool")
    if type(measure_viewer_baseline) is not bool:
        raise ValueError("measure_viewer_baseline must be a bool")
    now = datetime.now(timezone.utc)
    deadline = now + timedelta(days=30)
    data = [
        Bid(
            bid_no=f"BENCH-{i:05d}",
            title=f"합성 데이터 성능시험 - 용역 {i:05d}",
            agency="가상기관",
            category=("IT" if i % 2 == 0 else "교육"),
            bid_deadline=deadline,
            budget=1000000 + i,
            requirements=(Requirement(
                id="region-check", kind="region_any",
                value=["부산광역시"], source_text="가상 사업장 소재지 조건",
                source_locator="합성 데이터 1쪽",
            ),) if i < assessed else (),
            source_ref="SYNTHETIC; NOT A REAL TENDER",
            data_as_of=now,
            input_line=i + 2,
        ) for i in range(records)
    ]
    timings: dict[str, float] = {}
    with tempfile.TemporaryDirectory(prefix="bidowl-benchmark-only-") as scratch:
        db = Path(scratch) / "only-synthetic.sqlite3"
        with BidOwlStore(db) as store:
            imported = timed("import_bids_ms", lambda: store.import_bids(
                data, source_id=SOURCE), timings)
            if imported.inserted != records:
                raise AssertionError("Synthetic insert count mismatch")
            store.save_profile(CompanyProfile("bench-company", region="부산광역시"))
            def assess_subset():
                for i in range(assessed):
                    store.assess_and_record(
                        SOURCE, f"BENCH-{i:05d}", "bench-company")
            timed("assess_subset_ms", assess_subset, timings)
        with closing(open_database(db)) as conn:
            listing = timed("all_rows_page_1_ms", lambda: query_bids(
                conn, {"page": ["1"], "page_size": ["30"]}), timings)
            if listing["total"] != records or len(listing["items"]) != min(records, 30):
                raise AssertionError("Synthetic paginated query was incomplete")
            if measure_viewer_baseline:
                def legacy_full_scan_page():
                    # The P2-20 approach for a useful comparable baseline:
                    # parse all rows AND run historical assessment lookups
                    # before sorting and slicing the first 30.
                    rows = _latest_rows(conn)
                    categories = sorted({
                        str(row["category"]) for row in rows if row["category"]
                    })
                    rows.sort(key=lambda row: (
                        row["expired"], row["deadline"] or "",
                        row["source_id"], row["bid_no"],
                    ))
                    return {
                        "total": len(rows), "items": rows[:30],
                        "categories": categories,
                    }
                previous = timed(
                    "legacy_full_scan_page_1_ms", legacy_full_scan_page, timings,
                )
                if (previous["total"] != listing["total"]
                        or previous["categories"] != listing["categories"]
                        or previous["items"] != listing["items"]):
                    raise AssertionError("Fast viewer query changed historical page results")
            filtered = timed("filter_category_search_ms", lambda: query_bids(
                conn, {"category": ["IT"], "q": ["용역"], "page_size": ["30"]}), timings)
            if filtered["total"] != (records + 1) // 2:
                raise AssertionError("Synthetic category filter mismatch")
            detail = timed("single_bid_detail_ms", lambda: query_detail(
                conn, {"source_id": [SOURCE], "bid_no": ["BENCH-00000"],
                       "profile": ["bench-company"]}), timings)
            if detail["bid"]["bid_no"] != "BENCH-00000":
                raise AssertionError("Synthetic detail mismatch")
            favorite = timed("single_favorite_global_ms", lambda: query_favorites(conn, {
                "favorites": [[SOURCE, "BENCH-00000"]],
                "filters": {"page": "1", "page_size": "30"}
            }), timings)
            if favorite["total"] != 1:
                raise AssertionError("Synthetic favorite mismatch")
            with_failure = False
            try:
                conn.execute("DELETE FROM bids")
            except sqlite3.OperationalError:
                with_failure = True
            if not with_failure:
                raise AssertionError("Benchmark viewer allowed DB mutation")
        recovery_result = None
        if measure_recovery:
            snapshot = Path(scratch) / "perf-snapshot.sqlite3"
            restored = Path(scratch) / "perf-recovered.sqlite3"
            with BidOwlStore(db, must_exist=True) as store:
                timed("sqlite_backup_ms", lambda: store.backup_to(snapshot), timings)
            plan = timed(
                "recovery_validate_and_hash_ms",
                lambda: prepare_recovery(snapshot, restored), timings,
            )
            recovery_result = timed(
                "recovery_copy_verify_ms",
                lambda: restore_to_new_file(plan), timings,
            )
            if (recovery_result["record_counts"]["bids"] != records
                    or recovery_result["record_counts"]["assessments"] != assessed
                    or recovery_result["evidence_sha256"] != plan.evidence_sha256):
                raise AssertionError("Synthetic recovery benchmark evidence mismatch")
        return {
            "status": "SYNTHETIC_BENCH_COMPLETE",
            "records": records,
            "assessed": assessed,
            "db_size_bytes": db.stat().st_size,
            "recovery_verified": recovery_result is not None,
            "viewer_baseline_compared": measure_viewer_baseline,
            "recovery_evidence_sha256": (recovery_result["evidence_sha256"]
                                         if recovery_result is not None else None),
            "timings_ms": timings,
            "database_mutation_by_viewer": False,
            "disclaimer": (
                "Measured only when actually executed on the target PC. "
                "Synthetic local records only; not a customer performance guarantee. "
                "Single-process read-only query timings; browser/rendering excluded."
            ),
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL isolated synthetic 10k performance benchmark")
    parser.add_argument("--records", type=int, default=10000)
    parser.add_argument("--assessed", type=int, default=200)
    parser.add_argument("--compare-full-scan", action="store_true",
                        help="Also time and compare the legacy all-assessment full scan")
    parser.add_argument("--with-recovery", action="store_true",
                        help="Also measure consistent backup, evidence validation and safe restore")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run_benchmark(records=args.records, assessed=args.assessed,
                                              measure_recovery=args.with_recovery,
                                              measure_viewer_baseline=args.compare_full_scan),
                         ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, sqlite3.Error, AssertionError) as exc:
        print(json.dumps({"status": "SYNTHETIC_BENCH_FAILED", "reason": str(exc)},
                         ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
