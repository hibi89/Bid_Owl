"""BASIC P2-29 saved assessment batch report replay tests (synthetic only)."""
from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile

from bidowl import Bid, BidOwlStore, CompanyProfile, Requirement
from report_batch import (
    export_batch, main, parse_assessment_ids, preview_batch,
)


class ReportBatchTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="bidowl-report-batch-")
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.db = self.root / "saved.sqlite3"
        self.dest = self.root / "reports"
        bids = [
            Bid(
                bid_no=f"LOCAL-{index}", title=f"합성 공고 {index}",
                agency="테스트 기관", category="IT",
                bid_deadline=datetime.now(timezone.utc) + timedelta(days=10),
                budget=1000 * index,
                requirements=(
                    Requirement("region", "region_any", ["부산"], "부산 소재", "p.2"),
                ),
                source_ref="SYNTHETIC_ONLY",
                data_as_of=datetime.now(timezone.utc), input_line=index + 1,
            )
            for index in (1, 2)
        ]
        with BidOwlStore(self.db) as store:
            store.import_bids(bids, source_id="LOCAL-TEST")
            store.save_profile(CompanyProfile("company", region="부산"))
            self.ids = tuple(
                store.assess_and_record("LOCAL-TEST", bid.bid_no, "company")[0]
                for bid in bids
            )
        self.options = dict(
            db_path=self.db, assessment_ids=self.ids,
            output_dir=self.dest, report_format="xlsx",
        )

    def test_preview_does_not_write_database_or_reports(self):
        previous = self.db.read_bytes()
        result = preview_batch(**self.options)
        self.assertEqual(result["status"], "PREVIEW_NO_WRITE")
        self.assertEqual(result["assessment_ids"], list(self.ids))
        self.assertEqual(result["files_planned"], 2)
        self.assertEqual(result["collisions"], [])
        self.assertFalse(self.dest.exists())
        self.assertEqual(self.db.read_bytes(), previous)

    def test_batch_writes_exact_saved_xlsx_and_never_new_assessments(self):
        result = export_batch(**self.options)
        self.assertEqual(result["status"], "REPORT_BATCH_EXPORTED")
        self.assertEqual(len(result["reports"]), 2)
        self.assertEqual({r["assessment_id"] for r in result["reports"]}, set(self.ids))
        for report in result["reports"]:
            path = Path(report["files"][0])
            self.assertTrue(path.is_file())
            with ZipFile(path) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn("xl/worksheets/sheet2.xml", archive.namelist())
        with BidOwlStore(self.db, must_exist=True) as store:
            self.assertEqual(
                store.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2
            )

    def test_collision_blocks_batch_without_overwriting_prior_files(self):
        exported = export_batch(**self.options)
        baseline = {
            path: Path(path).read_bytes()
            for report in exported["reports"] for path in report["files"]
        }
        preview = preview_batch(**self.options)
        self.assertEqual(len(preview["collisions"]), 2)
        with self.assertRaises(FileExistsError):
            export_batch(**self.options)
        for path, content in baseline.items():
            self.assertEqual(Path(path).read_bytes(), content)

    def test_missing_assessment_is_rejected_before_any_output(self):
        with self.assertRaises(LookupError):
            export_batch(**{
                **self.options, "assessment_ids": (self.ids[0], max(self.ids) + 10),
            })
        self.assertFalse(self.dest.exists())

    def test_partial_failure_keeps_first_file_and_db_evidence(self):
        from report_existing import export_existing as real_export
        before = self.db.read_bytes()
        calls = {"count": 0}

        def fail_second(**kwargs):
            calls["count"] += 1
            if calls["count"] == 2:
                raise RuntimeError("synthetic second report error")
            return real_export(**kwargs)

        with patch("report_batch.export_existing", side_effect=fail_second):
            result = export_batch(**self.options)
        self.assertEqual(result["status"], "REPORT_BATCH_PARTIAL")
        self.assertEqual(result["failed_assessment_id"], self.ids[1])
        self.assertEqual(len(result["reports"]), 1)
        self.assertTrue(Path(result["reports"][0]["files"][0]).is_file())
        self.assertEqual(self.db.read_bytes(), before)

    def test_pdf_unavailable_refuses_output_before_any_file_creation(self):
        with patch("report_batch.check_pdf_support",
                   side_effect=RuntimeError("NO_KOREAN_FONT")):
            with self.assertRaisesRegex(RuntimeError, "NO_KOREAN_FONT"):
                export_batch(**{**self.options, "report_format": "both"})
        self.assertFalse(self.dest.exists())

    def test_id_parser_rejects_untrusted_and_duplicate_values(self):
        self.assertEqual(parse_assessment_ids("1, 2"), (1, 2))
        for invalid in ("0", "-1", "+1", "1,1", "1,2,", "١", "1; DROP", "1.0", " "):
            with self.subTest(invalid=invalid), self.assertRaises(ValueError):
                parse_assessment_ids(invalid)
        with self.assertRaises(ValueError):
            parse_assessment_ids(",".join(str(i) for i in range(1, 202)))

    def test_cli_preview_defaults_to_no_write_and_apply_is_explicit(self):
        args = [
            "--db", str(self.db), "--assessment-ids",
            ",".join(map(str, self.ids)), "--output", str(self.dest),
        ]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(args), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PREVIEW_NO_WRITE")
        self.assertFalse(self.dest.exists())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(args + ["--apply"]), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "REPORT_BATCH_EXPORTED")


if __name__ == "__main__":
    unittest.main()
