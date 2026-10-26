"""Legacy CLI safety regressions, using ONLY bundled synthetic fixtures."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

from bidowl import BidOwlStore
from bidowl.engine_identity import engine_fingerprint
from cli import execute


class LegacyCLISafetyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="bidowl-cli-safe-")
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        fixture = Path(__file__).resolve().parents[1] / "fixtures"
        self.csv = root / "sample.csv"
        self.csv.write_bytes((fixture / "sample_bids.csv").read_bytes())
        self.profile = root / "company.json"
        self.profile.write_bytes((fixture / "sample_profile.json").read_bytes())
        self.db = root / "customer-synthetic.sqlite3"
        self.output = root / "reports"

    def params(self):
        return Namespace(
            csv=str(self.csv), profile=str(self.profile),
            source_id="SYNTHETIC-CLI", db=str(self.db),
            output=str(self.output), format="xlsx"
        )

    def test_new_database_has_engine_provenance_and_no_backup(self):
        result = execute(self.params())
        self.assertIsNone(result["backup"])
        self.assertEqual(result["import"]["inserted"], 2)
        with BidOwlStore(self.db) as store:
            observed = tuple(row[0] for row in store.db.execute(
                "SELECT engine_hash FROM assessment_engine_provenance ORDER BY assessment_id"
            ))
            self.assertEqual(observed, (engine_fingerprint(),) * 2)

    def test_repeated_cli_import_backs_up_unmodified_prewrite_state(self):
        execute(self.params())
        repeated = execute(self.params())
        self.assertEqual(repeated["import"]["unchanged"], 2)
        backup = Path(repeated["backup"])
        self.assertTrue(backup.is_file())
        with BidOwlStore(backup) as saved:
            self.assertEqual(saved.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)
        with BidOwlStore(self.db) as current:
            self.assertEqual(current.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 4)

    def test_legacy_v1_table_migrates_only_after_backup(self):
        execute(self.params())
        with BidOwlStore(self.db) as store:
            store.db.execute("DROP TABLE assessment_engine_provenance")
        completed = execute(self.params())
        with BidOwlStore(completed["backup"]) as old:
            self.assertIsNone(old.db.execute(
                "SELECT name FROM sqlite_master "
                "WHERE name='assessment_engine_provenance'"
            ).fetchone())
            self.assertEqual(old.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)
        with BidOwlStore(self.db) as new:
            self.assertEqual(new.db.execute(
                "SELECT COUNT(*) FROM assessment_engine_provenance"
            ).fetchone()[0], 2)
            self.assertEqual(new.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 4)

    def test_existing_company_change_is_rejected_before_backup_and_write(self):
        execute(self.params())
        raw = json.loads(self.profile.read_text(encoding="utf-8"))
        raw["region"] = "서울"
        self.profile.write_text(json.dumps(raw, ensure_ascii=False), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "Existing company profile differs"):
            execute(self.params())
        self.assertFalse((self.db.parent / "backups").exists())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM profile_versions"
            ).fetchone()[0], 1)

    def test_backup_failure_blocks_any_new_assessment(self):
        execute(self.params())
        with patch.object(BidOwlStore, "backup_to", side_effect=OSError("BACKUP_FAIL")):
            with self.assertRaisesRegex(OSError, "BACKUP_FAIL"):
                execute(self.params())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)

    def test_report_writer_failure_warns_of_partial_change_and_keeps_backup(self):
        execute(self.params())
        with patch("cli.write_xlsx", side_effect=RuntimeError("SYNTHETIC_REPORT_FAILURE")):
            with self.assertRaisesRegex(RuntimeError, "CLI_PARTIAL_OR_UNCERTAIN"):
                execute(self.params())
        backups = sorted((self.db.parent / "backups").glob("*.sqlite3"))
        self.assertEqual(len(backups), 1)
        with BidOwlStore(backups[0]) as original:
            self.assertEqual(original.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)

    def test_foreign_existing_file_never_overwritten(self):
        sentinel = b"FOREIGN_USER_FILE_NOT_SQLITE"
        self.db.write_bytes(sentinel)
        with self.assertRaises((ValueError, sqlite3.DatabaseError)):
            execute(self.params())
        self.assertEqual(self.db.read_bytes(), sentinel)
        self.assertFalse((self.db.parent / "backups").exists())

    def test_new_database_appearing_during_preflight_is_not_adopted(self):
        sentinel = b"ANOTHER_PROCESS_WROTE_THIS"
        def race(*_args, **_kwargs):
            self.db.write_bytes(sentinel)
            return False, 0
        with patch("cli._preflight_existing_db", side_effect=race):
            with self.assertRaises(FileExistsError):
                execute(self.params())
        self.assertEqual(self.db.read_bytes(), sentinel)
        self.assertFalse((self.db.parent / "backups").exists())


if __name__ == "__main__":
    unittest.main()
