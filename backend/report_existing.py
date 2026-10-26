"""Export an existing BID OWL assessment to local XLSX/PDF without DB writes.

A saved assessment is immutable evidence. Re-export must not import CSV,
re-evaluate eligibility, advance versions, or contact any external service.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from bidowl.report import check_pdf_support, load_review_report, write_pdf, write_xlsx
from bidowl.store import _from_bid, default_database_path
from viewer import open_database


class SnapshotReader:
    """Only the two read operations needed by report.load_review_report."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def assessment(self, assessment_id: int):
        row = self.conn.execute("SELECT * FROM assessments WHERE id=?", (assessment_id,)).fetchone()
        if row is None:
            return None
        rules = tuple(self.conn.execute(
            "SELECT * FROM rule_assessments WHERE assessment_id=? ORDER BY position",
            (assessment_id,),
        ).fetchall())
        return row, rules

    def get_bid(self, source_id: str, bid_no: str, version: int):
        row = self.conn.execute(
            "SELECT payload FROM bid_versions WHERE source_id=? AND bid_no=? AND version=?",
            (source_id, bid_no, version),
        ).fetchone()
        return _from_bid(row["payload"]) if row is not None else None


def export_existing(
    *,
    db_path: str | Path,
    assessment_id: int,
    output_dir: str | Path,
    format: str = "both",
) -> dict:
    if type(assessment_id) is not int or assessment_id <= 0:
        raise ValueError("assessment_id must be a positive integer")
    if format not in {"xlsx", "pdf", "both"}:
        raise ValueError("format must be xlsx, pdf or both")
    # Validate optional PDF font/dependency before touching any report file.
    if format in {"pdf", "both"}:
        check_pdf_support()
    dest = Path(output_dir).expanduser().resolve()
    with closing(open_database(Path(db_path).expanduser().resolve())) as conn:
        report = load_review_report(SnapshotReader(conn), assessment_id)
        # Never overwrite an existing report; preflight both names first.
        names = [f"bidowl_review_{assessment_id:08d}.{ext}"
                 for ext in ("xlsx", "pdf") if format in (ext, "both")]
        for name in names:
            if (dest / name).exists():
                raise FileExistsError(f"Report already exists, choose another directory: {dest / name}")
        # Keep all DB reads complete before creating output directory or files.
    paths = []
    for ext in ("xlsx", "pdf"):
        if format in (ext, "both"):
            write = write_xlsx if ext == "xlsx" else write_pdf
            paths.append(str(write(report, dest / f"bidowl_review_{assessment_id:08d}.{ext}")))
    return {
        "status": "LOCAL_EXPORTED",
        "assessment_id": assessment_id,
        "profile_id": report.profile_id,
        "profile_version": report.profile_version,
        "bid_version": report.bid_version,
        "snapshot_status": report.status,
        "checked_at": report.checked_at,
        "files": paths,
        "notice": "Historical assessment snapshot; confirm current bid and company before participating.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL locally re-export saved assessment")
    parser.add_argument("--db", default=str(default_database_path()))
    parser.add_argument("--assessment-id", required=True, type=int)
    parser.add_argument("--output", required=True, help="Output directory for new, non-overwritten files")
    parser.add_argument("--format", default="both", choices=("xlsx", "pdf", "both"))
    args = parser.parse_args(argv)
    try:
        result = export_existing(
            db_path=args.db, assessment_id=args.assessment_id,
            output_dir=args.output, format=args.format,
        )
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, LookupError, KeyError, RuntimeError, sqlite3.Error) as exc:
        print(json.dumps({"status": "FAILED", "reason": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
