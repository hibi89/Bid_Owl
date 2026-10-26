"""BID OWL offline local import, screening and report command-line MVP."""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from bidowl import BidOwlStore, CompanyProfile, CSVImportError, parse_csv
from bidowl.engine_identity import engine_fingerprint
from bidowl.report import check_pdf_support, load_review_report, write_pdf, write_xlsx
from bidowl.schema import MAX_CSV_BYTES
from bidowl.store import default_database_path
from import_local import _check_source_id, _new_backup_path
from profile_workflow import load_profile_file
from viewer import open_database


def positive_local_path(path: str, label: str) -> Path:
    output = Path(path).expanduser().resolve()
    if not output.is_file():
        raise ValueError(f"{label} file missing: {output}")
    return output


def _preflight_existing_db(db_path: Path, company: CompanyProfile) -> tuple[bool, int]:
    """Never open a write-capable handle merely to inspect customer data."""
    if not db_path.exists():
        return False, 0
    with closing(open_database(db_path)) as reader:
        row = reader.execute(
            "SELECT latest_version FROM profiles WHERE profile_id=?",
            (company.profile_id,),
        ).fetchone()
        if row is None:
            return True, 0
        version = int(row["latest_version"])
        previous = reader.execute(
            "SELECT payload FROM profile_versions WHERE profile_id=? AND version=?",
            (company.profile_id, version),
        ).fetchone()
        if previous is None:
            raise ValueError("Saved profile history incomplete; refusing to write")
        if CompanyProfile.from_mapping(json.loads(previous["payload"])) != company:
            raise ValueError(
                "Existing company profile differs. Use profile_workflow.py "
                "with an expected version and a backup before editing."
            )
        return True, version


def execute(args: argparse.Namespace) -> dict:
    """Legacy CLI + reports, now with backup-first policy migration.

    The old CLI intentionally supports packaged synthetic demo fixtures, unlike
    the real-user GUI importer. It never silently overwrites a changed company
    profile, nor mutates an existing v1 DB before a consistent SQLite backup.
    """
    csv_path = positive_local_path(args.csv, "CSV")
    profile_path = positive_local_path(args.profile, "company profile")
    source_id = _check_source_id(args.source_id)
    if args.format not in {"xlsx", "pdf", "both"}:
        raise ValueError("Unsupported output format")
    if args.format in ("pdf", "both"):
        check_pdf_support()  # fail before DB/backup writes

    if csv_path.stat().st_size > MAX_CSV_BYTES:
        raise ValueError("CSV exceeds maximum 10 MiB")
    csv_bytes = csv_path.read_bytes()
    bids = parse_csv(csv_bytes).require_valid()  # validate ALL rows
    company = load_profile_file(profile_path)
    # Fail before DB writes if installation omitted eligibility source files.
    engine_fingerprint()
    db_path = Path(args.db).expanduser().resolve() if args.db else default_database_path()
    output = Path(args.output).expanduser().resolve()
    if output.exists() and not output.is_dir():
        raise ValueError("Report output path is not a directory")

    existing, previous_profile_version = _preflight_existing_db(db_path, company)
    if not existing:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        # Prevent another process's newly created DB being silently adopted.
        with db_path.open("xb"):
            pass

    backup = None
    mutated = False
    exported = []
    try:
        with BidOwlStore(db_path) as store:
            if existing:
                # Preserve the exact pre-write state, including on a future
                # provenance-metadata migration. Refuse silent backup overwrite.
                backup = store.backup_to(_new_backup_path(db_path))
                # Recheck for concurrent profile replacement after preflight.
                actual = store.get_profile(company.profile_id)
                actual_row = store.db.execute(
                    "SELECT latest_version FROM profiles WHERE profile_id=?",
                    (company.profile_id,),
                ).fetchone()
                if (actual != (company if previous_profile_version else None)
                        or (int(actual_row["latest_version"]) if actual_row else 0)
                        != previous_profile_version):
                    raise ValueError("Profile changed during CLI import; retry")
            # Only AFTER an existing database backup may its v1 metadata grow.
            mutated = True
            store.db.execute("""
                CREATE TABLE IF NOT EXISTS assessment_engine_provenance (
                    assessment_id INTEGER PRIMARY KEY,
                    engine_hash TEXT NOT NULL CHECK(length(engine_hash) = 64),
                    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
                )
            """)
            if previous_profile_version == 0:
                profile_version = store.save_profile(company, expected_version=0)
            else:
                profile_version = previous_profile_version

            result = store.import_csv(csv_bytes, source_id=source_id)
            output.mkdir(parents=True, exist_ok=True)
            for bid in bids:
                assessment_id, decision = store.assess_and_record(
                    source_id, bid.bid_no, company.profile_id,
                    expected_profile_version=profile_version,
                )
                report = load_review_report(store, assessment_id)
                stem = f"bidowl_review_{assessment_id:08d}"
                outputs = []
                for ext, func in (("xlsx", write_xlsx), ("pdf", write_pdf)):
                    if args.format in (ext, "both"):
                        destination = func(report, output / f"{stem}.{ext}")
                        outputs.append(str(destination))
                exported.append({
                    "bid_no": bid.bid_no,
                    "assessment_id": assessment_id,
                    "status": decision.status,
                    "expired": decision.is_expired,
                    "requires_human_review": decision.requires_human_review,
                    "files": outputs,
                })
    except BaseException as exc:
        if mutated:
            raise RuntimeError(
                "CLI_PARTIAL_OR_UNCERTAIN: data/report operation failed; "
                f"backup retained: {backup if backup else 'new DB (no previous contents)'}. "
                f"Cause: {type(exc).__name__}. Inspect saved reports and database."
            ) from exc
        raise
    return {
        "status": "LOCAL_COMPLETE",
        "source_id": source_id,
        "database": str(db_path),
        "backup": str(backup) if backup else None,
        "import": {
            "inserted": result.inserted,
            "revised": result.revised,
            "unchanged": result.unchanged,
        },
        "reports": exported,
        "disclaimer": "규칙 비교 참고용. 최종 판단은 담당자가 공고 원문 확인.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL offline CSV / eligibility / SQLite / PDF·Excel")
    parser.add_argument("--csv",required=True,help="UTF-8 bid CSV file")
    parser.add_argument("--profile",required=True,help="Company profile JSON file")
    parser.add_argument("--source-id",required=True,help="Stable source identifier, e.g. manual-import")
    parser.add_argument("--db",help="SQLite file path (default platform local app data)")
    parser.add_argument("--output",required=True,help="Local report output directory")
    parser.add_argument("--format",default="both",choices=["both","xlsx","pdf"])
    options = parser.parse_args(argv)
    try:
        print(json.dumps(execute(options),ensure_ascii=False,indent=2))
        return 0
    except (ValueError,KeyError,CSVImportError,RuntimeError,OSError,sqlite3.Error) as exc:
        if isinstance(exc,CSVImportError):
            problems=[{"code":p.code,"line":p.line,"field":p.field,"message":p.message} for p in exc.issues]
            print(json.dumps({"status":"INPUT_REJECTED","issues":problems},ensure_ascii=False),file=sys.stderr)
        else:
            print(json.dumps({"status":"FAILED","reason":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
