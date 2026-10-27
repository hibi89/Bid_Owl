"""BID OWL BASIC: safely re-export multiple committed assessments, without re-import.

Preview is the default. --apply writes only new report files and never changes
SQLite or regenerates assessment snapshots. Can be used after partial export.
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

from bidowl.report import check_pdf_support
from report_existing import export_existing
from viewer import open_database

MAX_ASSESSMENTS = 200


def parse_assessment_ids(value: str) -> tuple[int, ...]:
    if not isinstance(value, str):
        raise ValueError("assessment IDs must be comma-separated decimal numbers")
    parts = value.split(",")
    if not 1 <= len(parts) <= MAX_ASSESSMENTS:
        raise ValueError(f"select 1 to {MAX_ASSESSMENTS} assessment IDs per batch")
    ids = []
    for part in parts:
        raw = part.strip()
        if not re.fullmatch(r"[1-9][0-9]{0,17}", raw, flags=re.ASCII):
            raise ValueError("assessment IDs must be positive, ASCII decimal numbers")
        ids.append(int(raw))
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate assessment IDs are not allowed")
    return tuple(ids)


def preview_batch(
    *, db_path: str | Path, assessment_ids: tuple[int, ...],
    output_dir: str | Path, report_format: str = "xlsx",
) -> dict:
    if (not assessment_ids or len(assessment_ids) > MAX_ASSESSMENTS
            or any(type(i) is not int or i <= 0 or i > 999999999999999999
                   for i in assessment_ids)
            or len(assessment_ids) != len(set(assessment_ids))):
        raise ValueError("assessment_ids must contain distinct positive integers")
    if report_format not in ("xlsx", "pdf", "both"):
        raise ValueError("report format must be xlsx, pdf or both")
    destination = Path(output_dir).expanduser().resolve()
    if destination.exists() and not destination.is_dir():
        raise ValueError("Report destination is not a directory")
    database = Path(db_path).expanduser().resolve()
    with closing(open_database(database)) as conn:
        placeholders = ",".join("?" for _ in assessment_ids)
        found = {int(row[0]) for row in conn.execute(
            f"SELECT id FROM assessments WHERE id IN ({placeholders})", assessment_ids
        )}
    missing = sorted(set(assessment_ids) - found)
    if missing:
        raise LookupError(f"Saved assessment IDs not found: {missing}")
    names = []
    for assessment_id in assessment_ids:
        for ext in ("xlsx", "pdf"):
            if report_format in (ext, "both"):
                names.append(destination / f"bidowl_review_{assessment_id:08d}.{ext}")
    collisions = [str(path) for path in names if path.exists()]
    return {
        "status": "PREVIEW_NO_WRITE",
        "database": str(database), "output_dir": str(destination),
        "assessment_ids": list(assessment_ids), "report_format": report_format,
        "files_planned": len(names), "collisions": collisions,
        "notice": "Saved historical snapshots only. Database and existing files are not modified.",
    }


def export_batch(
    *, db_path: str | Path, assessment_ids: tuple[int, ...],
    output_dir: str | Path, report_format: str = "xlsx",
) -> dict:
    preview = preview_batch(
        db_path=db_path, assessment_ids=assessment_ids,
        output_dir=output_dir, report_format=report_format,
    )
    if preview["collisions"]:
        raise FileExistsError(
            "Existing report files prevent this batch; choose a new folder or "
            f"select only missing IDs: {preview['collisions']}"
        )
    if report_format in ("pdf", "both"):
        check_pdf_support()  # Reject unavailable PDF support before any output.
    completed = []
    for assessment_id in assessment_ids:
        try:
            result = export_existing(
                db_path=preview["database"], assessment_id=assessment_id,
                output_dir=preview["output_dir"], format=report_format,
            )
        except (OSError, ValueError, LookupError, KeyError, RuntimeError,
                sqlite3.Error) as exc:
            return {
                **preview, "status": "REPORT_BATCH_PARTIAL",
                "reports": completed, "failed_assessment_id": assessment_id,
                "export_error_type": type(exc).__name__,
                "export_error": str(exc)[:500],
                "notice": "Earlier exported files are preserved. SQLite was not changed. "
                          "Choose a new folder and retry only missing IDs.",
            }
        completed.append({"assessment_id": assessment_id, "files": result["files"]})
    return {**preview, "status": "REPORT_BATCH_EXPORTED", "reports": completed}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Read-only saved-assessment batch report replay")
    parser.add_argument("--db", required=True, help="Existing BID OWL SQLite DB")
    parser.add_argument("--assessment-ids", required=True, help="Comma-separated saved IDs")
    parser.add_argument("--output", required=True, help="New output folder for reports")
    parser.add_argument("--format", choices=("xlsx", "pdf", "both"), default="xlsx")
    parser.add_argument("--apply", action="store_true", help="Write reports; preview is default")
    args = parser.parse_args(argv)
    try:
        ids = parse_assessment_ids(args.assessment_ids)
        options = dict(db_path=args.db, assessment_ids=ids,
                       output_dir=args.output, report_format=args.format)
        result = export_batch(**options) if args.apply else preview_batch(**options)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["status"] != "REPORT_BATCH_PARTIAL" else 2
    except (OSError, ValueError, LookupError, KeyError, RuntimeError, sqlite3.Error) as exc:
        print(json.dumps({"status": "REPORT_BATCH_FAILED", "error_type": type(exc).__name__,
                          "reason": str(exc)[:500]}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
