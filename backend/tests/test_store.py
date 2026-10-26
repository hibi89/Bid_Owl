"""P1-03 file-backed SQLite integration tests; all test inputs synthetic."""
from __future__ import annotations

import csv
import io
import json
import sqlite3
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path

from bidowl import Bid, BidOwlStore, CSVImportError, CompanyProfile, Requirement, SchemaVersionError

KST = timezone(timedelta(hours=9))
T = datetime(2026,10,26,13,0,tzinfo=KST)


def rule(**overrides):
    values=dict(id='r1',kind='region_any',value=['부산광역시'],source_text='부산 사업장',source_locator='가상공고 2쪽')
    values.update(overrides)
    return Requirement(**values)


def bid(no='DEMO-1', **kwargs):
    values=dict(bid_no=no,title='합성 테스트 공고',agency='가상 발주처',category='IT',
                bid_deadline=T+timedelta(days=1),budget=1000,requirements=(rule(),),
                source_ref='SYNTHETIC',data_as_of=T,input_line=2)
    values.update(kwargs)
    return Bid(**values)


def csv_bytes(*records):
    f=io.StringIO(newline='')
    w=csv.writer(f)
    w.writerow(['bid_no','title','agency','category','bid_deadline','budget','requirements','source_ref','data_as_of'])
    for item in records:
        requirements=[{'id':r.id,'kind':r.kind,'value':r.value,'source':{'text':r.source_text,'locator':r.source_locator}} for r in item.requirements]
        w.writerow([item.bid_no,item.title,item.agency,item.category,item.bid_deadline.isoformat(),str(item.budget),json.dumps(requirements,ensure_ascii=False),item.source_ref,item.data_as_of.isoformat()])
    return f.getvalue().encode('utf-8-sig')


class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'local.sqlite3'
        self.store=BidOwlStore(self.path)
        self.addCleanup(self.store.close)

    def test_schema_version_foreign_keys(self):
        self.assertEqual(self.store.db.execute('PRAGMA user_version').fetchone()[0],1)
        self.assertEqual(self.store.db.execute('PRAGMA foreign_keys').fetchone()[0],1)

    def test_insert_bid_and_read_original(self):
        res=self.store.import_bids((bid(),),source_id='testcsv')
        self.assertEqual((res.inserted,res.revised,res.unchanged),(1,0,0))
        fetched=self.store.get_bid('testcsv','DEMO-1')
        self.assertEqual((fetched.title,fetched.budget,fetched.requirements[0].source_locator),('합성 테스트 공고',1000,'가상공고 2쪽'))
        self.assertEqual(fetched.bid_deadline,T+timedelta(days=1))
        self.assertEqual(fetched.data_as_of,T)
        self.assertEqual(fetched.input_line,0)

    def test_idempotent_reimport_records_audit(self):
        self.store.import_bids([bid()],source_id='testcsv')
        next_run=self.store.import_bids([bid(input_line=999)],source_id='testcsv')
        self.assertEqual((next_run.inserted,next_run.revised,next_run.unchanged),(0,0,1))
        self.assertEqual(len(self.store.bid_versions('testcsv','DEMO-1')),1)
        self.assertEqual([r['unchanged'] for r in self.store.import_runs('testcsv')],[0,1])

    def test_changed_content_creates_revision_and_retains_history(self):
        self.store.import_bids([bid()],source_id='testcsv')
        revised=replace(bid(),title='정정된 합성 공고',budget=1200)
        res=self.store.import_bids([revised],source_id='testcsv')
        self.assertEqual(res.revised,1)
        self.assertEqual(len(self.store.bid_versions('testcsv','DEMO-1')),2)
        self.assertEqual(self.store.get_bid('testcsv','DEMO-1',1).budget,1000)
        self.assertEqual(self.store.get_bid('testcsv','DEMO-1').budget,1200)

    def test_source_isolation_same_bid_number(self):
        self.store.import_bids([bid()],source_id='csv-A')
        self.store.import_bids([replace(bid(),budget=2000)],source_id='csv-B')
        self.assertEqual(self.store.get_bid('csv-A','DEMO-1').budget,1000)
        self.assertEqual(self.store.get_bid('csv-B','DEMO-1').budget,2000)

    def test_changes_back_to_original_add_a_third_revision(self):
        self.store.import_bids([bid()],source_id='csv')
        self.store.import_bids([replace(bid(),budget=1100)],source_id='csv')
        self.store.import_bids([bid()],source_id='csv')
        self.assertEqual(len(self.store.bid_versions('csv','DEMO-1')),3)

    def test_csv_valid_and_identical_file_hash(self):
        data=csv_bytes(bid())
        a=self.store.import_csv(data,source_id='s')
        b=self.store.import_csv(data,source_id='s')
        self.assertEqual(len(a.file_sha256),64)
        self.assertEqual(a.file_sha256,b.file_sha256)
        self.assertEqual((b.inserted,b.unchanged),(0,1))

    def test_csv_partial_invalid_rejected_without_writes(self):
        data=csv_bytes(bid('one'),bid('two'))
        bad=data.decode('utf-8-sig').replace('two,','one,').encode('utf-8')
        with self.assertRaises(CSVImportError):
            self.store.import_csv(bad,source_id='s')
        self.assertEqual(len(self.store.import_runs('s')),0)
        self.assertIsNone(self.store.get_bid('s','one'))

    def test_duplicate_bid_objects_rejected_before_transaction(self):
        with self.assertRaises(ValueError):
            self.store.import_bids([bid(),bid()],source_id='s')
        self.assertEqual(len(self.store.import_runs('s')),0)

    def test_bad_input_does_not_write(self):
        with self.assertRaises(ValueError):
            self.store.import_bids([bid(),replace(bid('two'),budget=0)],source_id='s')
        self.assertIsNone(self.store.get_bid('s','DEMO-1'))

    def test_failed_sql_insert_rolls_back_whole_batch(self):
        self.store.db.execute("""CREATE TRIGGER test_failure BEFORE INSERT ON bid_versions
            WHEN NEW.bid_no='DEMO-2' BEGIN SELECT RAISE(ABORT,'synthetic DB failure'); END;""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.import_bids([bid(),bid('DEMO-2')],source_id='s')
        self.assertIsNone(self.store.get_bid('s','DEMO-1'))
        self.assertEqual(self.store.import_runs('s'),())

    def test_failed_revision_rolls_back_version_pointer(self):
        self.store.import_bids([bid()],source_id='s')
        self.store.db.execute("""CREATE TRIGGER test_failure BEFORE INSERT ON bid_versions
            WHEN NEW.version=2 BEGIN SELECT RAISE(ABORT,'synthetic DB failure'); END;""")
        with self.assertRaises(sqlite3.IntegrityError):
            self.store.import_bids([replace(bid(),budget=5000)],source_id='s')
        self.assertEqual(self.store.get_bid('s','DEMO-1').budget,1000)
        self.assertEqual(len(self.store.bid_versions('s','DEMO-1')),1)

    def test_profile_roundtrip_unknown_vs_empty(self):
        p=CompanyProfile('p1',region=None,licenses=None,categories=(),staff_count=0)
        self.assertEqual(self.store.save_profile(p),1)
        loaded=self.store.get_profile('p1')
        self.assertIsNone(loaded.licenses)
        self.assertEqual(loaded.categories,())
        self.assertEqual(loaded.staff_count,0)

    def test_profile_same_snapshot_does_not_add_version(self):
        p=CompanyProfile('p1',region='부산광역시')
        self.assertEqual(self.store.save_profile(p),1)
        self.assertEqual(self.store.save_profile(p),1)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM profile_versions').fetchone()[0],1)

    def test_profile_changed_keeps_prior(self):
        a=CompanyProfile('p1',region='부산광역시')
        b=CompanyProfile('p1',region='서울특별시')
        self.store.save_profile(a)
        self.assertEqual(self.store.save_profile(b),2)
        self.assertEqual(self.store.get_profile('p1',1).region,'부산광역시')
        self.assertEqual(self.store.get_profile('p1').region,'서울특별시')

    def test_assessment_retains_provenance_and_references(self):
        self.store.import_bids([bid()],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='부산광역시'))
        key,decision=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.assertEqual(decision.status,'PASS')
        entry,rules=self.store.assessment(key)
        self.assertEqual((entry['bid_version'],entry['profile_version'],entry['status']),(1,1,'PASS'))
        self.assertEqual((rules[0]['source_text'],rules[0]['source_locator']),('부산 사업장','가상공고 2쪽'))
        self.assertEqual(entry['checked_at'],T.isoformat())
        self.assertEqual(entry['final_approval_required'],1)

    def test_assessment_expected_profile_version_prevents_stale_batch_write(self):
        self.store.import_bids([bid()], source_id='s')
        self.store.save_profile(CompanyProfile('p', region='부산광역시'))
        old, outcome = self.store.assess_and_record(
            's', 'DEMO-1', 'p', checked_at=T, expected_profile_version=1)
        self.assertEqual(outcome.status, 'PASS')
        self.store.save_profile(CompanyProfile('p', region='서울특별시'))
        with self.assertRaisesRegex(ValueError, 'Profile version mismatch'):
            self.store.assess_and_record(
                's', 'DEMO-1', 'p', checked_at=T, expected_profile_version=1)
        with self.assertRaises(ValueError):
            self.store.assess_and_record(
                's', 'DEMO-1', 'p', checked_at=T, expected_profile_version=True)
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM assessments').fetchone()[0], 1)
        current, outcome = self.store.assess_and_record(
            's', 'DEMO-1', 'p', checked_at=T, expected_profile_version=2)
        self.assertEqual(outcome.status, 'FAIL')
        self.assertEqual(self.store.assessment(old)[0]['profile_version'],1)
        self.assertEqual(self.store.assessment(current)[0]['profile_version'],2)

    def test_assess_after_profile_edit_retains_old_snapshot(self):
        self.store.import_bids([bid()],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='부산광역시'))
        first,decision=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.store.save_profile(CompanyProfile('p',region='서울특별시'))
        second,decision2=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.assertEqual((decision.status,decision2.status),('PASS','FAIL'))
        self.assertEqual(self.store.assessment(first)[0]['profile_version'],1)
        self.assertEqual(self.store.assessment(second)[0]['profile_version'],2)

    def test_bid_revision_does_not_rewrite_earlier_assessment(self):
        self.store.import_bids([bid()],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='부산광역시'))
        first,_=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.store.import_bids([replace(bid(),requirements=(rule(value=['서울특별시']),))],source_id='s')
        second,_=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.assertEqual(self.store.assessment(first)[0]['bid_version'],1)
        self.assertEqual(self.store.assessment(second)[0]['bid_version'],2)
        self.assertEqual((self.store.assessment(first)[0]['status'],self.store.assessment(second)[0]['status']),('PASS','FAIL'))

    def test_empty_rules_unknown_and_no_child_rows(self):
        self.store.import_bids([bid(requirements=())],source_id='s')
        self.store.save_profile(CompanyProfile('p'))
        key,outcome=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.assertEqual(outcome.status,'UNKNOWN')
        self.assertTrue(outcome.requires_human_review)
        self.assertEqual(self.store.assessment(key)[1],())

    def test_no_source_or_profile_assessment_rolls_back(self):
        with self.assertRaises(KeyError):
            self.store.assess_and_record('absent','x','p')
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM assessments').fetchone()[0],0)

    def test_naive_assessment_time_rolls_back(self):
        self.store.import_bids([bid()],source_id='s')
        self.store.save_profile(CompanyProfile('p'))
        with self.assertRaises(ValueError):
            self.store.assess_and_record('s','DEMO-1','p',checked_at=datetime(2026,10,26))
        self.assertEqual(self.store.db.execute('SELECT count(*) FROM assessments').fetchone()[0],0)

    def test_sql_parameter_safety_for_ids(self):
        weird="x');DROP TABLE bids;--"
        self.store.import_bids([bid(no=weird)],source_id=weird)
        self.assertIsNotNone(self.store.get_bid(weird,weird))
        self.assertEqual(self.store.db.execute("SELECT COUNT(*) FROM bids").fetchone()[0],1)

    def test_reopen_persistent_state(self):
        self.store.import_bids([bid()],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='부산광역시'))
        key,_=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        with BidOwlStore(self.path) as again:
            self.assertIsNotNone(again.get_bid('s','DEMO-1'))
            self.assertEqual(again.get_profile('p').region,'부산광역시')
            self.assertEqual(again.assessment(key)[0]['status'],'PASS')
            self.assertEqual(again.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')

    def test_backup_snapshot_and_no_overwrite(self):
        self.store.import_bids([bid()],source_id='s')
        backup=Path(self.temp.name)/'snap.sqlite3'
        self.store.backup_to(backup)
        with BidOwlStore(backup) as restored:
            self.assertEqual(restored.get_bid('s','DEMO-1').budget,1000)
        with self.assertRaises(FileExistsError):
            self.store.backup_to(backup)
        with self.assertRaises(ValueError):
            self.store.backup_to(self.path)

    def test_unknown_schema_version_not_rewritten(self):
        future=Path(self.temp.name)/'future.sqlite3'
        with sqlite3.connect(future) as db:
            db.execute('PRAGMA user_version=99')
        with self.assertRaises(SchemaVersionError):
            BidOwlStore(future)
        with sqlite3.connect(future) as db:
            self.assertEqual(db.execute('PRAGMA user_version').fetchone()[0],99)

    def test_unversioned_foreign_db_not_claimed(self):
        future=Path(self.temp.name)/'unknown.sqlite3'
        with sqlite3.connect(future) as db:
            db.execute('CREATE TABLE business_data (secret TEXT)')
        with self.assertRaises(SchemaVersionError):
            BidOwlStore(future)
        with sqlite3.connect(future) as db:
            self.assertIsNotNone(db.execute("SELECT name FROM sqlite_master WHERE name='business_data'").fetchone())

    def test_source_id_and_hash_validation(self):
        for source in ['', '  ', None]:
            with self.subTest(source=source),self.assertRaises(ValueError):
                self.store.import_bids([bid()],source_id=source)
        with self.assertRaises(ValueError):
            self.store.import_bids([bid()],source_id='s',file_sha256='nothash')
        self.assertEqual(self.store.db.execute('SELECT COUNT(*) FROM bids').fetchone()[0],0)

    def test_expired_stays_separate_from_qualification(self):
        expired=bid(bid_deadline=T-timedelta(seconds=1))
        self.store.import_bids([expired],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='부산광역시'))
        key,answer=self.store.assess_and_record('s','DEMO-1','p',checked_at=T)
        self.assertEqual(answer.status,'PASS')
        self.assertTrue(answer.is_expired)
        self.assertEqual(self.store.assessment(key)[0]['is_expired'],1)


if __name__=='__main__':
    unittest.main()
