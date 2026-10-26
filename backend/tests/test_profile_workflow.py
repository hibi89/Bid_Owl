"""Synthetic-only profile workflow tests: versioning, preflight, backup, restore."""
from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from datetime import datetime, timedelta, timezone

from bidowl import Bid, BidOwlStore, CompanyProfile, Requirement
from profile_workflow import execute, load_profile_file, main


class ProfileWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "sample.sqlite3"
        self.profile_file = self.root / "profile.json"
        deadline = datetime.now(timezone.utc) + timedelta(days=7)
        bid = Bid(bid_no="S1", title="합성 공고", agency="가상 발주처", category="IT",
                  bid_deadline=deadline, budget=3000,
                  requirements=(Requirement(id="region", kind="region_any", value=["부산"],
                                source_text="부산 소재", source_locator="테스트 원문"),),
                  source_ref="SYNTHETIC", data_as_of=datetime.now(timezone.utc), input_line=2)
        with BidOwlStore(self.db) as store:
            store.import_bids([bid], source_id="synthetic")
            store.save_profile(CompanyProfile("company", region="부산"))
            self.old_id, self.old = store.assess_and_record("synthetic", "S1", "company")
        self.write_profile(region="서울")

    def write_profile(self, *, region="서울", profile_id="company"):
        self.profile_file.write_text(json.dumps({"profile_id":profile_id, "region":region}, ensure_ascii=False), encoding="utf-8")

    def run_flow(self, **kwargs):
        return execute(db_path=self.db, profile_path=self.profile_file, expected_version=1, **kwargs)

    def test_preview_never_changes_file_or_reassesses(self):
        before = self.db.read_bytes()
        result = self.run_flow(reassess=True)
        self.assertEqual(result["status"], "PREVIEW")
        self.assertEqual((result["previous_version"],result["planned_version"]), (1,2))
        self.assertEqual(result["reassess_count"], 1)
        self.assertEqual(before, self.db.read_bytes())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.get_profile("company").region,"부산")
            self.assertEqual(store.db.execute("SELECT count(*) FROM assessments").fetchone()[0],1)

    def test_apply_requires_backup_and_creates_version_with_history(self):
        with self.assertRaises(ValueError):
            self.run_flow(apply=True)
        backup=self.root/"safe-backup.sqlite3"
        result=self.run_flow(apply=True,backup_path=backup,reassess=True)
        self.assertEqual((result["status"],result["planned_version"],result["assessments_saved"]),("APPLIED",2,1))
        self.assertTrue(backup.exists())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.get_profile("company").region,"서울")
            self.assertEqual(store.get_profile("company",1).region,"부산")
            self.assertEqual(store.assessment(self.old_id)[0]["status"],"PASS")
            latest=store.db.execute("SELECT id FROM assessments ORDER BY id DESC LIMIT 1").fetchone()[0]
            self.assertEqual(store.assessment(latest)[0]["profile_version"],2)
            self.assertEqual(store.assessment(latest)[0]["status"],"FAIL")
        with BidOwlStore(backup) as restored:
            self.assertEqual(restored.get_profile("company").region,"부산")
            self.assertEqual(restored.db.execute("SELECT count(*) FROM assessments").fetchone()[0],1)

    def test_version_conflict_never_writes_or_backs_up(self):
        backup=self.root/"dont-create.sqlite3"
        with self.assertRaisesRegex(ValueError,"version mismatch"):
            execute(db_path=self.db,profile_path=self.profile_file,expected_version=99,
                    apply=True,backup_path=backup)
        self.assertFalse(backup.exists())

    def test_backup_overwrite_refused_with_original_unchanged(self):
        backup=self.root/"existing.sqlite3"
        backup.write_bytes(b"NEVER OVERWRITE")
        with self.assertRaises(FileExistsError):
            self.run_flow(apply=True,backup_path=backup)
        self.assertEqual(backup.read_bytes(), b"NEVER OVERWRITE")
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.get_profile("company").region,"부산")

    def test_invalid_profile_rejected_before_any_db_edit(self):
        backup=self.root/"never.sqlite3"
        self.profile_file.write_text('{"profile_id":"company","region":""}', encoding="utf-8")
        with self.assertRaises(ValueError):
            self.run_flow(apply=True,backup_path=backup)
        self.assertFalse(backup.exists())
        self.profile_file.write_bytes(b"x"*65537)
        with self.assertRaisesRegex(ValueError,"64 KiB"):
            load_profile_file(self.profile_file)

    def test_create_requires_explicit_flag(self):
        self.write_profile(region="부산",profile_id="newco")
        with self.assertRaisesRegex(ValueError,"--create"):
            self.run_flow()
        backup=self.root/"create-backup.sqlite3"
        result=execute(db_path=self.db,profile_path=self.profile_file,expected_version=0,
                       create=True,apply=True,backup_path=backup)
        self.assertEqual((result["status"],result["planned_version"]),("APPLIED",1))
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.get_profile("newco").region,"부산")

    def test_safe_limit_validation(self):
        with self.assertRaises(ValueError):
            self.run_flow(max_reassess=0)
        with self.assertRaises(ValueError):
            self.run_flow(max_reassess=10001)

    def test_preview_uses_no_writable_store(self):
        from profile_workflow import ReadOnlyProfileStore
        with patch('profile_workflow.BidOwlStore', side_effect=AssertionError('write connection created')):
            result = self.run_flow(reassess=True)
        self.assertEqual(result['status'], 'PREVIEW')
        with ReadOnlyProfileStore(self.db) as conn:
            self.assertEqual(conn.get_profile('company').region, '부산')
            with self.assertRaises(sqlite3.OperationalError):
                conn.db.execute("UPDATE profiles SET latest_version=9")

    def test_invalid_existing_database_never_gets_initialized(self):
        other = self.root/'empty.sqlite3'
        sqlite3.connect(other).close()
        before = other.read_bytes()
        for should_apply in (False, True):
            with self.subTest(apply=should_apply), self.assertRaises(ValueError):
                execute(db_path=other, profile_path=self.profile_file,
                        expected_version=1, apply=should_apply,
                        backup_path=self.root/'never-create.sqlite3')
        self.assertEqual(other.read_bytes(), before)
        self.assertFalse((self.root/'never-create.sqlite3').exists())

    def test_atomic_version_conflict_at_commit(self):
        from bidowl.store import BidOwlStore as ActualStore
        original_save = ActualStore.save_profile
        def change_behind_the_scenes(store, profile, **kwargs):
            # Simulate another process editing after the initial read and backup.
            original_save(store, CompanyProfile('company', region='제주'), expected_version=1)
            return original_save(store, profile, **kwargs)
        backup = self.root/'conflict.sqlite3'
        with patch.object(ActualStore, 'save_profile', autospec=True,
                          side_effect=change_behind_the_scenes):
            with self.assertRaisesRegex(ValueError, 'CONFLICT_NO_WRITE'):
                self.run_flow(apply=True, backup_path=backup)
        self.assertTrue(backup.exists())
        with ActualStore(self.db) as store:
            self.assertEqual(store.get_profile('company').region, '제주')
            self.assertEqual(store.db.execute('SELECT COUNT(*) FROM profile_versions').fetchone()[0], 2)

    def test_racing_profile_change_during_reassess_reports_partial_not_no_write(self):
        actual_assess = BidOwlStore.assess_and_record
        actual_save = BidOwlStore.save_profile
        def conflicting_assessment(store, source_id, bid_no, profile_id, **kwargs):
            # Another client writes a newer revision after THIS apply has
            # already saved v2, but before its first assessment.
            actual_save(store, CompanyProfile('company', region='제주'),
                        expected_version=2)
            return actual_assess(store, source_id, bid_no, profile_id, **kwargs)
        backup = self.root / 'racing-assessment.sqlite3'
        with patch.object(BidOwlStore, 'assess_and_record', autospec=True,
                          side_effect=conflicting_assessment):
            with self.assertRaisesRegex(RuntimeError, 'PARTIAL_WRITE: 0/1'):
                self.run_flow(apply=True, backup_path=backup, reassess=True)
        self.assertTrue(backup.exists())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.get_profile('company',2).region,'서울')
            self.assertEqual(store.get_profile('company',3).region,'제주')
            self.assertEqual(store.db.execute('SELECT COUNT(*) FROM assessments').fetchone()[0],1)
        with BidOwlStore(backup) as previous:
            self.assertEqual(previous.get_profile('company').region,'부산')
            self.assertEqual(previous.db.execute('SELECT COUNT(*) FROM assessments').fetchone()[0],1)

    def test_partial_failure_reports_backup_and_preserves_old_snapshot(self):
        backup=self.root/"partial.sqlite3"
        with patch.object(BidOwlStore,"assess_and_record", side_effect=RuntimeError("synthetic failure")):
            with self.assertRaisesRegex(RuntimeError,"PARTIAL_WRITE"):
                self.run_flow(apply=True,backup_path=backup,reassess=True)
        self.assertTrue(backup.exists())
        with BidOwlStore(backup) as store:
            self.assertEqual(store.get_profile("company").region,"부산")
            self.assertEqual(store.assessment(self.old_id)[0]["status"],"PASS")


if __name__ == "__main__":
    unittest.main()
