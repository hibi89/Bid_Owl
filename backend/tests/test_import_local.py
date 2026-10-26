"""P2-14 real local onboarding tests. Only synthetic fixtures and temp SQLite."""
from __future__ import annotations

import contextlib
import io
import json
import sqlite3
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
        self.assertEqual(second["assessments_saved"], 0)
        self.assertEqual(second["assessments_reused"], 2)
        with BidOwlStore(self.db) as current:
            self.assertEqual(current.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2)
        self.assertEqual(self.csv.read_bytes().count(b"SYNTHETIC_TEST"), 2)

    def test_engine_change_never_reuses_old_pass(self):
        initial = apply_import(self.prepare())
        self.assertEqual(initial["assessments_saved"], 2)
        with BidOwlStore(self.db) as store:
            store.db.execute(
                "UPDATE assessment_engine_provenance SET engine_hash=?",
                ("0" * 64,),
            )
        changed = apply_import(self.prepare())
        self.assertEqual(changed["assessments_saved"], 2)
        self.assertEqual(changed["assessments_reused"], 0)
        self.assertTrue(changed["backup"])
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 4)
            self.assertEqual(store.db.execute(
                "SELECT COUNT(DISTINCT engine_hash) FROM assessment_engine_provenance"
            ).fetchone()[0], 2)
        again = apply_import(self.prepare())
        self.assertEqual(again["assessments_saved"], 0)
        self.assertEqual(again["assessments_reused"], 2)

    def test_legacy_v1_engine_metadata_migrates_only_after_backup(self):
        apply_import(self.prepare())
        with BidOwlStore(self.db) as store:
            store.db.execute("DROP TABLE assessment_engine_provenance")
        plan = self.prepare()
        self.assertEqual(plan_summary(plan)["status"], "PREVIEW_NO_WRITE")
        with BidOwlStore(self.db) as store:
            self.assertIsNone(store.db.execute(
                "SELECT 1 FROM sqlite_master WHERE name='assessment_engine_provenance'"
            ).fetchone())
        migrated = apply_import(plan)
        self.assertEqual(migrated["assessments_saved"], 2)
        self.assertEqual(migrated["assessments_reused"], 0)
        self.assertTrue(migrated["backup"])
        with BidOwlStore(migrated["backup"]) as before:
            self.assertIsNone(before.db.execute(
                "SELECT 1 FROM sqlite_master WHERE name='assessment_engine_provenance'"
            ).fetchone())
            self.assertEqual(before.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)
        with BidOwlStore(self.db) as after:
            self.assertIsNotNone(after.db.execute(
                "SELECT 1 FROM sqlite_master WHERE name='assessment_engine_provenance'"
            ).fetchone())
            self.assertEqual(after.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 4)

    def test_noop_reimport_preserves_immutable_assessment_ids(self):
        first = apply_import(self.prepare())
        with BidOwlStore(self.db) as store:
            before = tuple(row[0] for row in store.db.execute(
                "SELECT id FROM assessments ORDER BY id"
            ))
        second = apply_import(self.prepare())
        self.assertEqual(first["eligibility_counts"], second["eligibility_counts"])
        self.assertEqual(second["assessments_saved"], 0)
        self.assertEqual(second["assessments_reused"], 2)
        self.assertTrue(second["backup"])
        with BidOwlStore(self.db) as store:
            self.assertEqual(before, tuple(row[0] for row in store.db.execute(
                "SELECT id FROM assessments ORDER BY id"
            )))

    def test_force_reassess_regenerates_identical_input_evidence(self):
        apply_import(self.prepare())
        second = apply_import(self.prepare(), force_reassess=True)
        self.assertEqual(second["assessments_saved"], 2)
        self.assertEqual(second["assessments_reused"], 0)
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 4)

    def test_force_reassess_flag_rejects_nonboolean(self):
        with self.assertRaisesRegex(ValueError, "boolean"):
            apply_import(self.prepare(), force_reassess="yes")
        self.assertFalse(self.db.exists())

    def test_revised_bid_only_reassesses_its_own_snapshot(self):
        apply_import(self.prepare())
        data = self.csv.read_bytes()
        self.assertIn(b"120000000", data)
        self.csv.write_bytes(data.replace(b"120000000", b"120000001", 1))
        outcome = apply_import(self.prepare())
        self.assertEqual(outcome["import"]["revised"], 1)
        self.assertEqual(outcome["import"]["unchanged"], 1)
        self.assertEqual(outcome["assessments_saved"], 1)
        self.assertEqual(outcome["assessments_reused"], 1)
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 3)

    def test_expiry_transition_forces_fresh_assessment_not_stale_reuse(self):
        first = apply_import(self.prepare())
        self.assertEqual(first["assessments_saved"], 2)
        with BidOwlStore(self.db) as store:
            # Simulate a previous snapshot from a different time without
            # changing the bid/profile version. Rechecking must not reuse it.
            store.db.execute("""
                UPDATE assessments SET is_expired = 1 - is_expired
                WHERE bid_no = 'TEST-2027-001'
            """)
        second = apply_import(self.prepare())
        self.assertEqual(second["assessments_saved"], 1)
        self.assertEqual(second["assessments_reused"], 1)
        with BidOwlStore(self.db) as store:
            row = store.db.execute("""
                SELECT a.is_expired
                FROM assessments a
                WHERE a.bid_no='TEST-2027-001'
                ORDER BY a.id DESC LIMIT 1
            """).fetchone()
            self.assertEqual(row["is_expired"], 0)

    def test_profile_revision_invalidates_reuse_for_all_bids(self):
        first = apply_import(self.prepare())
        self.assertEqual(first["assessments_saved"], 2)
        with BidOwlStore(self.db) as store:
            # Simulate a concurrent profile change then explicit restoration
            # to the original contents as a new version.
            version2 = store.save_profile(
                CompanyProfile("test-company", region="서울"), expected_version=1
            )
            self.assertEqual(version2, 2)
            restored = store.save_profile(self.company, expected_version=2)
            self.assertEqual(restored, 3)
        second = apply_import(self.prepare())
        self.assertEqual(second["assessments_saved"], 2)
        self.assertEqual(second["assessments_reused"], 0)
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 4)
            new_versions = tuple(r[0] for r in store.db.execute(
                "SELECT profile_version FROM assessments ORDER BY id DESC LIMIT 2"
            ))
            self.assertEqual(new_versions, (3, 3))

    def test_mid_import_profile_version_drift_stops_cached_reuse(self):
        apply_import(self.prepare())
        plan = self.prepare()
        original = BidOwlStore.import_bids

        def drift_after_import(store, *args, **kwargs):
            result = original(store, *args, **kwargs)
            store.save_profile(
                CompanyProfile("test-company", region="서울특별시"),
                expected_version=1,
            )
            return result

        with patch.object(BidOwlStore, "import_bids", new=drift_after_import):
            with self.assertRaisesRegex(RuntimeError, "IMPORT_PARTIAL_OR_UNCERTAIN"):
                apply_import(plan)
        backups = list((self.root / "backups").glob("*.sqlite3"))
        self.assertEqual(len(backups), 1)
        with BidOwlStore(backups[0]) as original_backup:
            self.assertEqual(original_backup.db.execute(
                "SELECT latest_version FROM profiles WHERE profile_id='test-company'"
            ).fetchone()[0], 1)
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 2)

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
        with self.assertRaises((ValueError, sqlite3.DatabaseError)):
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

    def test_existing_db_replaced_after_preview_is_rejected_without_backup(self):
        import os
        apply_import(self.prepare())
        plan = self.prepare()
        different = self.root / "new-owner.sqlite3"
        with BidOwlStore(different) as store:
            store.save_profile(self.company, expected_version=0)
        os.replace(different, self.db)
        with self.assertRaisesRegex(ValueError, "replaced or modified"):
            apply_import(plan)
        self.assertFalse((self.root / "backups").exists())
        with BidOwlStore(self.db) as other:
            self.assertEqual(other.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 0)

    def test_existing_db_deleted_during_writer_open_is_not_recreated(self):
        apply_import(self.prepare())
        plan = self.prepare()
        original_store = BidOwlStore

        def remove_before_open(*args, **kwargs):
            self.db.unlink()
            return original_store(*args, **kwargs)

        with patch("import_local.BidOwlStore", side_effect=remove_before_open):
            with self.assertRaises(FileNotFoundError):
                apply_import(plan)
        self.assertFalse(self.db.exists())
        self.assertFalse((self.root / "backups").exists())

    def test_existing_db_swapped_after_apply_preflight_is_rejected(self):
        import os
        apply_import(self.prepare())
        plan = self.prepare()
        replacement = self.root / "different.sqlite3"
        with BidOwlStore(replacement) as store:
            store.save_profile(self.company, expected_version=0)
        original_store = BidOwlStore

        def swap_before_writer(*args, **kwargs):
            os.replace(replacement, self.db)
            return original_store(*args, **kwargs)

        with patch("import_local.BidOwlStore", side_effect=swap_before_writer):
            with self.assertRaisesRegex(ValueError, "identity changed"):
                apply_import(plan)
        self.assertFalse((self.root / "backups").exists())
        with BidOwlStore(self.db) as other:
            self.assertEqual(other.db.execute(
                "SELECT COUNT(*) FROM assessments"
            ).fetchone()[0], 0)

    def test_new_file_racing_after_preflight_is_never_adopted(self):
        plan = self.prepare()

        def simulate_race(*_args, **_kwargs):
            # Another process creates the path AFTER preflight recheck
            # but BEFORE our sqlite3.connect. Exclusive create must fail.
            self.db.write_bytes(b"RACING_OTHER_OWNER")
            return False, 0, "CREATE"

        with patch("import_local._existing_db_state", side_effect=simulate_race):
            with self.assertRaises(FileExistsError):
                apply_import(plan)
        self.assertEqual(self.db.read_bytes(), b"RACING_OTHER_OWNER")
        self.assertFalse((self.root / "backups").exists())

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

    def test_overlong_gui_profile_id_rejected_prewrite(self):
        oversize = CompanyProfile("X" * 301)
        with self.assertRaisesRegex(ValueError, "300 characters"):
            self.prepare(profile=oversize)
        self.assertFalse(self.db.exists())

    def test_source_id_whitespace_rejected_prewrite(self):
        with self.assertRaisesRegex(ValueError, "Source ID"):
            self.prepare(source_id=" LOCAL TEST ")
        self.assertFalse(self.db.exists())

    def test_cli_force_reassess_creates_new_assessments(self):
        profile_file = self.root / "profile.json"
        profile_file.write_text(json.dumps({
            "profile_id": self.company.profile_id,
            "region": self.company.region,
            "categories": self.company.categories,
            "licenses": self.company.licenses,
            "staff_count": self.company.staff_count,
        }, ensure_ascii=False), encoding="utf-8")
        options = ["--csv", str(self.csv), "--profile", str(profile_file),
                   "--source-id", "LOCAL-TEST", "--db", str(self.db), "--apply"]
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main(options), 0)
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(main(options + ["--force-reassess"]), 0)
        result = json.loads(stdout.getvalue())
        self.assertEqual(result["assessments_saved"], 2)
        self.assertEqual(result["assessments_reused"], 0)

    def _cli_input_arguments(self):
        profile = self.root / "mvp-company.json"
        profile.write_text(json.dumps({
            "profile_id": self.company.profile_id,
            "region": self.company.region,
            "categories": self.company.categories,
            "licenses": self.company.licenses,
            "staff_count": self.company.staff_count,
        }, ensure_ascii=False), encoding="utf-8")
        return [
            "--csv", str(self.csv), "--profile", str(profile),
            "--source-id", "LOCAL-TEST", "--db", str(self.db),
        ]

    def test_import_returns_saved_and_reused_assessment_ids(self):
        first = apply_import(self.prepare())
        saved = first["assessments"]
        self.assertEqual(len(saved), 2)
        self.assertTrue(all(not x["reused"] for x in saved))
        self.assertEqual(len({x["assessment_id"] for x in saved}), 2)
        self.assertEqual(sum(first["eligibility_counts"].values()), len(saved))
        second = apply_import(self.prepare())
        reused = second["assessments"]
        self.assertEqual(len(reused), 2)
        self.assertTrue(all(x["reused"] for x in reused))
        self.assertEqual(
            {x["bid_no"]: (x["assessment_id"], x["status"]) for x in reused},
            {x["bid_no"]: (x["assessment_id"], x["status"]) for x in saved},
        )
        with BidOwlStore(self.db, must_exist=True) as store:
            for row in saved:
                stored = store.db.execute(
                    "SELECT status FROM assessments WHERE id=?",
                    (row["assessment_id"],),
                ).fetchone()
                self.assertEqual(stored["status"], row["status"])

    def test_one_shot_real_import_then_saved_xlsx_exports(self):
        from zipfile import ZipFile
        from xml.etree import ElementTree
        folder = self.root / "client-reports"
        argv = self._cli_input_arguments() + [
            "--apply", "--export-dir", str(folder),
        ]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(argv), 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "IMPORTED_AND_EXPORTED")
        self.assertEqual(payload["assessments_saved"], 2)
        self.assertEqual(len(payload["reports"]), 2)
        self.assertEqual(
            {x["assessment_id"] for x in payload["reports"]},
            {x["assessment_id"] for x in payload["assessments"]},
        )
        for report in payload["reports"]:
            self.assertEqual(len(report["files"]), 1)
            path = Path(report["files"][0])
            self.assertEqual(path.parent, folder)
            with ZipFile(path) as archive:
                self.assertIsNone(archive.testzip())
                for name in archive.namelist():
                    if name.endswith((".xml", ".rels")):
                        ElementTree.fromstring(archive.read(name))

    def test_report_export_failure_does_not_disguise_successful_import(self):
        argv = self._cli_input_arguments() + [
            "--apply", "--export-dir", str(self.root / "exports"),
        ]
        with patch("import_local.export_existing", side_effect=RuntimeError("EXPORT_BROKEN")):
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(main(argv), 2)
        result = json.loads(stderr.getvalue())
        self.assertEqual(result["status"], "IMPORTED_EXPORT_FAILED")
        self.assertEqual(result["assessments_saved"], 2)
        self.assertEqual(result["reports"], [])
        self.assertIn("EXPORT_BROKEN", result["export_error"])
        with BidOwlStore(self.db, must_exist=True) as store:
            self.assertEqual(
                store.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2,
            )

    def test_export_path_exists_cannot_overwrite_previous_reports(self):
        folder = self.root / "fixed-output"
        argv = self._cli_input_arguments() + [
            "--apply", "--export-dir", str(folder),
        ]
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            self.assertEqual(main(argv), 0)
        first = json.loads(stdout.getvalue())
        original = {
            item["files"][0]: Path(item["files"][0]).read_bytes()
            for item in first["reports"]
        }
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(main(argv), 2)
        repeated = json.loads(stderr.getvalue())
        self.assertEqual(repeated["status"], "IMPORTED_EXPORT_FAILED")
        self.assertEqual(repeated["assessments_reused"], 2)
        self.assertTrue(repeated["backup"])
        self.assertEqual(repeated["reports"], [])
        for path, contents in original.items():
            self.assertEqual(Path(path).read_bytes(), contents)
        with BidOwlStore(self.db, must_exist=True) as store:
            self.assertEqual(
                store.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2,
            )

    def test_second_report_failure_preserves_first_file_and_import_evidence(self):
        from report_existing import export_existing as real_export
        export_dir = self.root / "partial-exports"
        argv = self._cli_input_arguments() + [
            "--apply", "--export-dir", str(export_dir),
        ]
        calls = {"count": 0}

        def fail_second(**kwargs):
            calls["count"] += 1
            if calls["count"] == 2:
                raise RuntimeError("SYNTHETIC_SECOND_REPORT_FAILURE")
            return real_export(**kwargs)

        with patch("import_local.export_existing", side_effect=fail_second):
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(main(argv), 2)
        result = json.loads(stderr.getvalue())
        self.assertEqual(result["status"], "IMPORTED_EXPORT_FAILED")
        self.assertEqual(result["assessments_saved"], 2)
        self.assertEqual(len(result["reports"]), 1)
        first = Path(result["reports"][0]["files"][0])
        self.assertTrue(first.exists())
        self.assertGreater(first.stat().st_size, 0)
        self.assertIn("SYNTHETIC_SECOND_REPORT_FAILURE", result["export_error"])
        with BidOwlStore(self.db, must_exist=True) as store:
            self.assertEqual(
                store.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2
            )
        self.assertEqual(len(list(export_dir.glob("*.xlsx"))), 1)

    def test_pdf_missing_dependency_refused_before_import_or_output(self):
        target = self.root / "client"
        argv = self._cli_input_arguments() + [
            "--apply", "--export-dir", str(target), "--report-format", "both",
        ]
        with patch("import_local.check_pdf_support",
                   side_effect=RuntimeError("SYNTHETIC_NO_KOREAN_FONT")):
            with contextlib.redirect_stderr(io.StringIO()) as stderr:
                self.assertEqual(main(argv), 2)
        self.assertEqual(json.loads(stderr.getvalue())["status"], "IMPORT_FAILED")
        self.assertFalse(self.db.exists())
        self.assertFalse(target.exists())

    def test_export_option_requires_apply_and_keeps_preview_nonwriting(self):
        target = self.root / "unused-reports"
        argv = self._cli_input_arguments() + ["--export-dir", str(target)]
        with contextlib.redirect_stderr(io.StringIO()) as stderr:
            self.assertEqual(main(argv), 2)
        result = json.loads(stderr.getvalue())
        self.assertEqual(result["status"], "IMPORT_FAILED")
        self.assertFalse(self.db.exists())
        self.assertFalse(target.exists())

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
