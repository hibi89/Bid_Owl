"""P2-14 real local onboarding tests. Only synthetic fixtures and temp SQLite."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bidowl import BidOwlStore, CompanyProfile, CSVImportError
from import_local import (
    RESERVED_DEMO_SOURCE, _profile_from_fields,
    apply_import, main, plan_summary, prepare_import,
)

BACKEND = Path(__file__).resolve().parents[1]


class LocalImportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bidowl-import-test-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.csv = self.root / "incoming.csv"
        self.db = self.root / "company.sqlite3"
        original = (BACKEND / "fixtures" / "sample_bids.csv").read_bytes()
        self.csv.write_bytes(original.replace(b"DEMO_ONLY", b"SYNTHETIC_TEST")
                                   .replace(b"DEMO-", b"TEST-"))
        self.company = CompanyProfile(
            "test-company", region="부산광역시",
            categories=("IT용역",), licenses=("소프트웨어사업자",),
            staff_count=5,
        )

    def prepare(self, **overrides):
        params = {
            "csv_path": self.csv, "profile": self.company,
            "source_id": "LOCAL-TEST", "db_path": self.db,
        }
        params.update(overrides)
        return prepare_import(**params)

    def test_preview_validates_without_creating_database(self):
        before = self.csv.read_bytes()
        plan = self.prepare()
        summary = plan_summary(plan)
        self.assertEqual(summary["status"], "PREVIEW_NO_WRITE")
        self.assertEqual(summary["bid_count"], 2)
        self.assertFalse(summary["database_exists"])
        self.assertFalse(summary["backup_required"])
        self.assertEqual(summary["profile_action"], "CREATE")
        self.assertFalse(self.db.exists())
        self.assertEqual(self.csv.read_bytes(), before)

    def test_first_import_creates_db_profile_rule_assessments(self):
        result = apply_import(self.prepare())
        self.assertEqual(result["status"], "IMPORTED")
        self.assertEqual(result["import"]["inserted"], 2)
        self.assertEqual(result["import"]["revised"], 0)
        self.assertEqual(result["assessments_saved"], 2)
        self.assertIsNone(result["backup"])
        self.assertEqual(sum(result["eligibility_counts"].values()), 2)
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.get_profile("test-company"), self.company)
            self.assertEqual(store.db.execute("SELECT COUNT(*) FROM bids").fetchone()[0], 2)
            self.assertEqual(store.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2)
            self.assertGreater(store.db.execute(
                "SELECT COUNT(*) FROM rule_assessments").fetchone()[0], 0)

    def test_second_import_backs_up_original_before_reassessing(self):
        first = apply_import(self.prepare())
        self.assertIsNone(first["backup"])
        plan = self.prepare()
        summary = plan_summary(plan)
        self.assertTrue(summary["backup_required"])
        self.assertEqual(summary["profile_action"], "KEEP")
        second = apply_import(plan)
        self.assertEqual(second["import"]["inserted"], 0)
        self.assertEqual(second["import"]["unchanged"], 2)
        backup = Path(second["backup"])
        self.assertTrue(backup.is_file())
        self.assertNotEqual(backup.resolve(), self.db.resolve())
        with BidOwlStore(backup) as old:
            self.assertEqual(old.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2)
        with BidOwlStore(self.db) as current:
            self.assertEqual(current.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 4)
        self.assertEqual(self.csv.read_bytes().count(b"SYNTHETIC_TEST"), 2)

    def test_existing_profile_mismatch_fails_before_writes_or_backup(self):
        apply_import(self.prepare())
        before = self.db.stat().st_size
        changed = CompanyProfile("test-company", region="서울특별시")
        with self.assertRaisesRegex(ValueError, "Existing company profile differs"):
            self.prepare(profile=changed)
        self.assertEqual(self.db.stat().st_size, before)
        self.assertFalse((self.root / "backups").exists())

    def test_invalid_csv_fails_without_creating_database(self):
        self.csv.write_bytes(b"not a valid csv structure")
        with self.assertRaises(CSVImportError):
            self.prepare()
        self.assertFalse(self.db.exists())

    def test_packaged_demo_provenance_refused_before_any_writes(self):
        original = (BACKEND / "fixtures" / "sample_bids.csv").read_bytes()
        self.csv.write_bytes(original)
        with self.assertRaisesRegex(ValueError, "synthetic demo"):
            self.prepare()
        self.assertFalse(self.db.exists())
        self.csv.write_bytes(original.replace(b"DEMO_ONLY", b"SYNTHETIC_TEST"))
        with self.assertRaisesRegex(ValueError, "synthetic demo"):
            self.prepare()

    def test_synthetic_company_and_reserved_source_refused(self):
        with self.assertRaisesRegex(ValueError, "Synthetic demo company"):
            self.prepare(profile=CompanyProfile("SYNTHETIC-COMPANY"))
        with self.assertRaisesRegex(ValueError, "Reserved synthetic-demo"):
            self.prepare(source_id=RESERVED_DEMO_SOURCE)
        self.assertFalse(self.db.exists())

    def test_non_bidowl_existing_db_refused_readonly(self):
        self.db.write_bytes(b"SOMEONE_ELSES_EXISTING_FILE")
        with self.assertRaises((ValueError, OSError, Exception)):
            self.prepare()
        self.assertEqual(self.db.read_bytes(), b"SOMEONE_ELSES_EXISTING_FILE")
        self.assertFalse((self.root / "backups").exists())

    def test_csv_changed_after_preview_is_rejected(self):
        plan = self.prepare()
        self.csv.write_bytes(self.csv.read_bytes().replace(b"TEST-2027", b"EDIT-2027"))
        with self.assertRaisesRegex(ValueError, "CSV changed"):
            apply_import(plan)
        self.assertFalse(self.db.exists())

    def test_db_appearing_after_preview_is_rejected(self):
        plan = self.prepare()
        self.db.write_bytes(b"NEVER_OVERWRITE")
        with self.assertRaisesRegex(ValueError, "Database creation"):
            apply_import(plan)
        self.assertEqual(self.db.read_bytes(), b"NEVER_OVERWRITE")

    def test_profile_change_after_preview_is_rejected(self):
        apply_import(self.prepare())
        plan = self.prepare()
        with BidOwlStore(self.db) as store:
            store.save_profile(CompanyProfile("test-company", region="서울"), expected_version=1)
        with self.assertRaisesRegex(ValueError, "Existing company profile differs"):
            apply_import(plan)
        self.assertFalse((self.root / "backups").exists())

    def test_backup_kept_on_import_failure(self):
        apply_import(self.prepare())
        plan = self.prepare()
        with patch.object(BidOwlStore, "import_bids", side_effect=RuntimeError("synthetic failure")):
            with self.assertRaisesRegex(RuntimeError, "IMPORT_PARTIAL_OR_UNCERTAIN"):
                apply_import(plan)
        backups = list((self.root / "backups").glob("*.sqlite3"))
        self.assertEqual(len(backups), 1)
        with BidOwlStore(backups[0]) as restored:
            self.assertEqual(restored.db.execute(
                "SELECT COUNT(*) FROM assessments").fetchone()[0], 2)

    def test_profile_blank_fields_preserve_unknown_semantics(self):
        fields = {"profile_id": "test", "region": "", "categories": "",
                  "licenses": "", "staff_count": "", "experience_total_krw": ""}
        company = _profile_from_fields(fields)
        self.assertIsNone(company.region)
        self.assertIsNone(company.categories)
        self.assertIsNone(company.licenses)
        self.assertIsNone(company.staff_count)
        self.assertIsNone(company.experience_total_krw)
        fields["staff_count"] = "-1"
        with self.assertRaises(ValueError):
            _profile_from_fields(fields)

    def test_cli_defaults_to_nonwriting_preview(self):
        profile_file = self.root / "company.json"
        profile_file.write_text(json.dumps({
            "profile_id": self.company.profile_id, "region": self.company.region,
            "categories": self.company.categories, "licenses": self.company.licenses,
            "staff_count": self.company.staff_count,
        }, ensure_ascii=False), encoding="utf-8")
        arguments = ["--csv", str(self.csv), "--profile", str(profile_file),
                     "--source-id", "LOCAL-TEST", "--db", str(self.db)]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(arguments), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "PREVIEW_NO_WRITE")
        self.assertFalse(self.db.exists())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(arguments + ["--apply"]), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "IMPORTED")
        self.assertTrue(self.db.exists())

    def test_desktop_launcher_paths_and_no_http_write(self):
        root_cmd = (BACKEND.parent / "START_BID_OWL_IMPORT.cmd").read_text(encoding="utf-8")
        backend_cmd = (BACKEND / "START_IMPORT.cmd").read_text(encoding="utf-8")
        source = (BACKEND / "import_local.py").read_text(encoding="utf-8")
        self.assertIn(r"backend\START_IMPORT.cmd", root_cmd)
        self.assertIn("import_local.py", backend_cmd)
        self.assertIn("askyesno", source)
        self.assertIn("prepare_import", source)
        self.assertIn("apply_import", source)
        self.assertNotIn("do_POST", source)


if __name__ == "__main__":
    unittest.main()
