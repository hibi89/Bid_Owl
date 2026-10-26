"""Synthetic-only recovery and backup safety tests; no real customer files."""
from __future__ import annotations

import contextlib
import io
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backup_recovery import main, prepare_recovery, preview_summary, restore_to_new_file
from bidowl import BidOwlStore, CompanyProfile
from bidowl.engine_identity import engine_fingerprint
from viewer import open_database, query_bids


class BackupRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bidowl-recovery-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "live.sqlite3"
        self.backup = self.root / "snapshot.sqlite3"
        self.recovered = self.root / "recovered" / "new.sqlite3"
        fixtures = Path(__file__).resolve().parents[1] / "fixtures"
        raw = (fixtures / "sample_bids.csv").read_bytes()
        profile_data = json.loads(
            (fixtures / "sample_profile.json").read_text(encoding="utf-8")
        )
        with BidOwlStore(self.db) as store:
            imported = store.import_csv(raw, source_id="SYNTHETIC-RESTORE")
            self.assertEqual(imported.inserted, 2)
            profile = CompanyProfile.from_mapping(profile_data)
            store.save_profile(profile)
            for number in ("DEMO-2027-001", "DEMO-2025-002"):
                store.assess_and_record("SYNTHETIC-RESTORE", number, profile.profile_id)
            store.backup_to(self.backup)

    def test_readonly_preview_never_creates_destination_directory(self):
        plan = prepare_recovery(self.backup, self.recovered)
        result = preview_summary(plan)
        self.assertEqual(result["status"], "RECOVERY_PREVIEW_NO_WRITE")
        self.assertEqual(result["record_counts"]["bids"], 2)
        self.assertEqual(result["record_counts"]["profiles"], 1)
        self.assertEqual(result["record_counts"]["assessments"], 2)
        self.assertTrue(result["engine_provenance_table"])
        self.assertEqual(len(result["source_sha256"]), 64)
        self.assertFalse(self.recovered.parent.exists())

    def test_restore_to_new_file_retains_live_db_and_historical_evidence(self):
        before = self.db.read_bytes()
        backup_before = self.backup.read_bytes()
        result = restore_to_new_file(prepare_recovery(self.backup, self.recovered))
        self.assertEqual(result["status"], "RESTORED_TO_NEW_FILE")
        self.assertFalse(result["original_database_modified"])
        self.assertTrue(self.recovered.is_file())
        self.assertEqual(self.db.read_bytes(), before)
        self.assertEqual(self.backup.read_bytes(), backup_before)
        with BidOwlStore(self.recovered, must_exist=True) as store:
            self.assertEqual(store.db.execute("SELECT COUNT(*) FROM bids").fetchone()[0], 2)
            self.assertEqual(store.db.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2)
            hashes = {r[0] for r in store.db.execute(
                "SELECT engine_hash FROM assessment_engine_provenance"
            )}
            self.assertEqual(hashes, {engine_fingerprint()})

    def test_evidence_digest_is_identical_after_complete_restore(self):
        plan = prepare_recovery(self.backup, self.recovered)
        self.assertEqual(len(plan.evidence_sha256), 64)
        before = preview_summary(plan)
        self.assertEqual(before["evidence_sha256"], plan.evidence_sha256)
        result = restore_to_new_file(plan)
        self.assertEqual(result["evidence_sha256"], plan.evidence_sha256)
        # A new source preview over the restored file must hash the same rows.
        second = prepare_recovery(self.recovered, self.root / "third.sqlite3")
        self.assertEqual(second.evidence_sha256, plan.evidence_sha256)

    def test_same_count_mutated_restored_record_is_detected_and_removed(self):
        plan = prepare_recovery(self.backup, self.recovered)
        from backup_recovery import _source_snapshot as original_snapshot

        def mutate_restored(path):
            if path == self.recovered:
                with contextlib.closing(sqlite3.connect(path)) as writer:
                    writer.execute("UPDATE profiles SET latest_version=99")
                    writer.commit()
            return original_snapshot(path)

        with patch("backup_recovery._source_snapshot", side_effect=mutate_restored):
            with self.assertRaisesRegex(ValueError, "evidence content differs"):
                restore_to_new_file(plan)
        self.assertFalse(self.recovered.exists())
        self.assertTrue(self.backup.exists())

    def test_same_count_changed_source_blocks_preview_apply(self):
        plan = prepare_recovery(self.backup, self.recovered)
        with contextlib.closing(sqlite3.connect(self.backup)) as writer:
            writer.execute("UPDATE profiles SET latest_version=99")
            writer.commit()
        self.assertEqual(
            preview_summary(prepare_recovery(self.backup, self.recovered))["record_counts"],
            preview_summary(plan)["record_counts"],
        )
        with self.assertRaisesRegex(ValueError, "changed since preview"):
            restore_to_new_file(plan)
        self.assertFalse(self.recovered.exists())

    def test_sidecar_appearing_during_hash_aborts_preview(self):
        from backup_recovery import _file_hash
        sidecar = Path(str(self.backup) + "-wal")

        def create_sidecar(path):
            result = _file_hash(path)
            if path == self.backup:
                sidecar.write_bytes(b"synthetic newly-active journal")
            return result

        with patch("backup_recovery._file_hash", side_effect=create_sidecar):
            with self.assertRaisesRegex(ValueError, "sidecar appeared"):
                prepare_recovery(self.backup, self.recovered)
        self.assertFalse(self.recovered.exists())

    def test_backup_shm_sidecar_is_rejected_before_destination_created(self):
        sidecar = Path(str(self.backup) + "-shm")
        sidecar.write_bytes(b"synthetic shared memory")
        with self.assertRaisesRegex(ValueError, "WAL/journal"):
            prepare_recovery(self.backup, self.recovered)
        self.assertFalse(self.recovered.exists())

    def test_destination_already_exists_never_overwritten(self):
        self.recovered.parent.mkdir(parents=True)
        self.recovered.write_bytes(b"DO_NOT_OVERWRITE")
        with self.assertRaises(FileExistsError):
            prepare_recovery(self.backup, self.recovered)
        self.assertEqual(self.recovered.read_bytes(), b"DO_NOT_OVERWRITE")

    def test_backup_path_itself_cannot_be_the_destination(self):
        with self.assertRaisesRegex(ValueError, "must not be"):
            prepare_recovery(self.backup, self.backup)
        self.assertTrue(self.backup.is_file())

    def test_corrupt_backup_rejected_without_output(self):
        self.backup.write_bytes(b"NOT_SQLITE")
        with self.assertRaises(sqlite3.DatabaseError):
            prepare_recovery(self.backup, self.recovered)
        self.assertFalse(self.recovered.exists())

    def test_foreign_schema_v1_rejected(self):
        self.backup.unlink()
        with contextlib.closing(sqlite3.connect(self.backup)) as conn:
            conn.execute("CREATE TABLE unrelated(secret TEXT)")
            conn.execute("PRAGMA user_version=1")
            conn.commit()
        with self.assertRaisesRegex(ValueError, "Missing BID OWL"):
            prepare_recovery(self.backup, self.recovered)

    def test_legacy_without_policy_metadata_preserved_but_is_unknown(self):
        with contextlib.closing(sqlite3.connect(self.backup)) as conn:
            conn.execute("DROP TABLE assessment_engine_provenance")
        plan = prepare_recovery(self.backup, self.recovered)
        self.assertFalse(plan.policy_provenance)
        restore_to_new_file(plan)
        with contextlib.closing(open_database(self.recovered)) as conn:
            records = query_bids(conn, {})["items"]
            self.assertEqual(len(records), 2)
            self.assertTrue(all(x["status"] == "UNKNOWN" for x in records))
            self.assertTrue(all(x["requires_human_review"] for x in records))

    def test_backup_content_change_after_preview_blocks_restore(self):
        plan = prepare_recovery(self.backup, self.recovered)
        with contextlib.closing(sqlite3.connect(self.backup)) as conn:
            conn.execute("CREATE TABLE added_after_preview(n INTEGER)")
            conn.commit()
        with self.assertRaisesRegex(ValueError, "changed since preview"):
            restore_to_new_file(plan)
        self.assertFalse(self.recovered.exists())

    def test_backup_removed_after_preview_does_not_create_recovered_db(self):
        plan = prepare_recovery(self.backup, self.recovered)
        self.backup.unlink()
        with self.assertRaises(FileNotFoundError):
            restore_to_new_file(plan)
        self.assertFalse(self.recovered.exists())

    def test_destination_race_after_recheck_cannot_overwrite_other_file(self):
        plan = prepare_recovery(self.backup, self.recovered)
        original = prepare_recovery

        def race(*args, **kwargs):
            validated = original(*args, **kwargs)
            self.recovered.parent.mkdir(parents=True, exist_ok=True)
            self.recovered.write_bytes(b"CREATED_BY_OTHER_PROGRAM")
            return validated

        with patch("backup_recovery.prepare_recovery", side_effect=race):
            with self.assertRaises(FileExistsError):
                restore_to_new_file(plan)
        self.assertEqual(self.recovered.read_bytes(), b"CREATED_BY_OTHER_PROGRAM")

    def test_postreservation_failure_only_cleans_our_new_file(self):
        plan = prepare_recovery(self.backup, self.recovered)
        from backup_recovery import _validate_v1
        calls = {"n": 0}

        def fail_second_validation(conn):
            calls["n"] += 1
            if calls["n"] == 2:
                raise sqlite3.DatabaseError("synthetic recovery failure")
            return _validate_v1(conn)

        with patch("backup_recovery._validate_v1", side_effect=fail_second_validation):
            with self.assertRaisesRegex(sqlite3.DatabaseError, "synthetic recovery"):
                restore_to_new_file(plan)
        self.assertFalse(self.recovered.exists())
        self.assertTrue(self.backup.is_file())

    def test_foreign_key_corruption_detected_in_readonly_preview(self):
        with contextlib.closing(sqlite3.connect(self.backup)) as conn:
            conn.execute("PRAGMA foreign_keys=OFF")
            conn.execute("DELETE FROM profiles")
            conn.commit()
        with self.assertRaisesRegex(ValueError, "foreign key"):
            prepare_recovery(self.backup, self.recovered)
        self.assertFalse(self.recovered.exists())

    def test_cli_requires_apply_for_new_file_and_reports_json(self):
        args = ["--source", str(self.backup), "--destination", str(self.recovered)]
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(args), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "RECOVERY_PREVIEW_NO_WRITE")
        self.assertFalse(self.recovered.exists())
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(main(args + ["--apply"]), 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "RESTORED_TO_NEW_FILE")
        self.assertTrue(self.recovered.is_file())

    def test_existing_output_cli_fails_without_mutation(self):
        self.recovered.parent.mkdir()
        self.recovered.write_bytes(b"SAFE")
        with contextlib.redirect_stderr(io.StringIO()) as error:
            status = main([
                "--source", str(self.backup), "--destination", str(self.recovered),
                "--apply",
            ])
        self.assertEqual(status, 2)
        self.assertEqual(json.loads(error.getvalue())["status"], "RECOVERY_FAILED")
        self.assertEqual(self.recovered.read_bytes(), b"SAFE")


if __name__ == "__main__":
    unittest.main()
