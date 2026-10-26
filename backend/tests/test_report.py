"""P1-04 integration: persisted evidence -> real Excel/PDF, CLI safety."""
from __future__ import annotations
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from datetime import datetime, timezone, timedelta

from bidowl import BidOwlStore, CompanyProfile, Bid, Requirement, CSVImportError
from bidowl.report import load_review_report, write_pdf, write_xlsx, check_pdf_support, KoreanFontUnavailable, REPORT_DISCLAIMER
from cli import execute, main
from argparse import Namespace

NOW=datetime(2026,10,26,tzinfo=timezone(timedelta(hours=9)))


def make_bid(*, source_text='사업장 소재지가 부산광역시',title='합성 공고',rule=True):
    rules=(Requirement('1','region_any',['부산광역시'],source_text,'공고 2쪽'),) if rule else ()
    return Bid('D-1',title,'가상기관','IT',NOW+timedelta(days=2),1000000,rules,'SYNTHETIC',NOW,2)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.store=BidOwlStore(self.root/'local.sqlite3')
        self.addCleanup(self.store.close)
        self.store.import_bids([make_bid()],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='부산광역시'))
        self.assessment_id,self.decision=self.store.assess_and_record('s','D-1','p',checked_at=NOW)
        self.report=load_review_report(self.store,self.assessment_id)

    def test_read_persisted_decision_and_provenance(self):
        self.assertEqual(self.report.status,'PASS')
        self.assertEqual(self.report.rules[0]['source_text'],'사업장 소재지가 부산광역시')
        self.assertEqual(self.report.rules[0]['source_locator'],'공고 2쪽')
        self.assertEqual(self.report.checked_at,NOW.isoformat())

    def test_revisions_do_not_change_prior_report(self):
        self.store.import_bids([make_bid(title='정정 공고',source_text='부산 주소 요건')],source_id='s')
        self.store.save_profile(CompanyProfile('p',region='서울특별시'))
        old=load_review_report(self.store,self.assessment_id)
        self.assertEqual(old.bid_version,1)
        self.assertEqual(old.profile_version,1)
        self.assertEqual(old.title,'합성 공고')
        self.assertEqual(old.status,'PASS')
        self.assertEqual(old.rules[0]['source_text'],'사업장 소재지가 부산광역시')

    def test_missing_assessment(self):
        with self.assertRaises(KeyError):
            load_review_report(self.store,3456)

    def test_real_xlsx_structure_and_data(self):
        path=write_xlsx(self.report,self.root/'report.xlsx')
        with ZipFile(path) as z:
            self.assertIsNone(z.testzip())
            for name in z.namelist():
                if name.endswith(('.xml','.rels')):
                    ET.fromstring(z.read(name))
            sheets=[z.read('xl/worksheets/sheet1.xml'),z.read('xl/worksheets/sheet2.xml')]
            self.assertIn('부산광역시'.encode(),sheets[1])
            self.assertIn(REPORT_DISCLAIMER.encode(),sheets[0])
            self.assertIn(b'inlineStr',sheets[0])
            self.assertNotIn(b'<f>',sheets[0])
            self.assertNotIn(b'<f>',sheets[1])

    def test_excel_formula_prefix_injection_defused(self):
        evil='=HYPERLINK("https://evil.invalid","click")'
        b=make_bid(title=evil,source_text='-1+2')
        self.store.import_bids([b],source_id='s')
        assess,_=self.store.assess_and_record('s','D-1','p',checked_at=NOW)
        report=load_review_report(self.store,assess)
        path=write_xlsx(report,self.root/'safe.xlsx')
        with ZipFile(path) as z:
            values=''.join(z.read(s).decode() for s in ('xl/worksheets/sheet1.xml','xl/worksheets/sheet2.xml'))
            self.assertIn("'=HYPERLINK",values)
            self.assertIn("'-1+2",values)
            self.assertNotIn('<f>',values)

    def test_invalid_xml_control_character_removed(self):
        report=replace(self.report,title='hello\x01world')
        file=write_xlsx(report,self.root/'clean.xlsx')
        with ZipFile(file) as z:
            xml=z.read('xl/worksheets/sheet1.xml')
            ET.fromstring(xml)
            self.assertNotIn(b'\x01',xml)

    def test_refuse_truncation_of_source_evidence(self):
        report=replace(self.report,title='X'*33000)
        with self.assertRaises(ValueError):
            write_xlsx(report,self.root/'huge.xlsx')

    def test_failed_xlsx_writer_removes_its_own_partial_file(self):
        from bidowl import report as report_module
        target = self.root/'incomplete.xlsx'
        original = report_module._sheet_xml
        calls = 0
        def fail_second_sheet(rows):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise RuntimeError('synthetic final worksheet failure')
            return original(rows)
        with patch.object(report_module, '_sheet_xml', side_effect=fail_second_sheet):
            with self.assertRaisesRegex(RuntimeError,'synthetic final worksheet failure'):
                write_xlsx(self.report,target)
        self.assertFalse(target.exists())
        self.assertEqual(calls,2)

    def test_never_overwrite_existing_xlsx(self):
        path=self.root/'report.xlsx'
        path.write_bytes(b'do not replace')
        with self.assertRaises(FileExistsError):
            write_xlsx(self.report,path)
        self.assertEqual(path.read_bytes(),b'do not replace')

    def test_unknown_rule_generates_explanatory_row(self):
        self.store.import_bids([make_bid(rule=False)],source_id='s')
        assess,_=self.store.assess_and_record('s','D-1','p',checked_at=NOW)
        file=write_xlsx(load_review_report(self.store,assess),self.root/'unknown.xlsx')
        with ZipFile(file) as z:
            self.assertIn(b'NO_RULES',z.read('xl/worksheets/sheet2.xml'))

    def test_real_pdf_header_and_korean_font(self):
        path=write_pdf(self.report,self.root/'report.pdf')
        self.assertTrue(path.read_bytes().startswith(b'%PDF-'))
        self.assertGreater(path.stat().st_size,2000)
        self.assertIn(b'FontFile2',path.read_bytes())

    def test_pdf_non_overwrite(self):
        file=self.root/'old.pdf'
        file.write_bytes(b'old')
        with self.assertRaises(FileExistsError):
            write_pdf(self.report,file)
        self.assertEqual(file.read_bytes(),b'old')

    def test_unsupported_font_fails_early(self):
        with patch('bidowl.report._korean_font_path',side_effect=KoreanFontUnavailable('no font')):
            with self.assertRaises(KoreanFontUnavailable):
                write_pdf(self.report,self.root/'absent.pdf')
        self.assertFalse((self.root/'absent.pdf').exists())


class CLITests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        fixture=Path(__file__).resolve().parent.parent/'fixtures'
        self.csv=self.root/'input.csv'
        self.csv.write_bytes((fixture/'sample_bids.csv').read_bytes())
        self.profile=self.root/'company.json'
        self.profile.write_text((fixture/'sample_profile.json').read_text(encoding='utf-8'),encoding='utf-8')
        self.db=self.root/'db.sqlite3'
        self.out=self.root/'reports'

    def params(self,fmt='both'):
        return Namespace(csv=str(self.csv),profile=str(self.profile),source_id='SYNTHETIC',db=str(self.db),output=str(self.out),format=fmt)

    def test_full_cli_two_actual_reports(self):
        result=execute(self.params())
        self.assertEqual(result['status'],'LOCAL_COMPLETE')
        self.assertEqual(result['import']['inserted'],2)
        self.assertEqual(len(result['reports']),2)
        self.assertEqual(len(list(self.out.glob('*.pdf'))),2)
        self.assertEqual(len(list(self.out.glob('*.xlsx'))),2)
        self.assertEqual(result['reports'][1]['expired'],True)
        with BidOwlStore(self.db) as db:
            self.assertEqual(len(db.import_runs('SYNTHETIC')),1)

    def test_cli_repeat_idempotent_bid_versions(self):
        execute(self.params('xlsx'))
        again=execute(self.params('xlsx'))
        self.assertEqual(again['import']['unchanged'],2)
        with BidOwlStore(self.db) as db:
            self.assertEqual(len(db.bid_versions('SYNTHETIC','DEMO-2027-001')),1)
        self.assertEqual(len(list(self.out.glob('*.xlsx'))),4)

    def test_invalid_csv_aborts_before_database_creation(self):
        self.csv.write_bytes(b'not,csv\n')
        with self.assertRaises(CSVImportError):
            execute(self.params('xlsx'))
        self.assertFalse(self.db.exists())

    def test_invalid_company_aborts_before_database_creation(self):
        self.profile.write_text('{invalid json',encoding='utf-8')
        with self.assertRaises(ValueError):
            execute(self.params('xlsx'))
        self.assertFalse(self.db.exists())

    def test_unsupported_company_type_aborts(self):
        self.profile.write_text('{"profile_id":"x","staff_count":true}',encoding='utf-8')
        with self.assertRaises(ValueError):
            execute(self.params('xlsx'))
        self.assertFalse(self.db.exists())

    def test_pdf_missing_font_aborts_before_writes(self):
        with patch('cli.check_pdf_support',side_effect=KoreanFontUnavailable('font absent')):
            with self.assertRaises(KoreanFontUnavailable):
                execute(self.params('both'))
        self.assertFalse(self.db.exists())

    def test_xlsx_does_not_require_pdf_font(self):
        with patch('cli.check_pdf_support',side_effect=KoreanFontUnavailable('font absent')):
            result=execute(self.params('xlsx'))
        self.assertEqual(len(result['reports'][0]['files']),1)

    def test_bad_csv_cli_error_code(self):
        self.csv.write_bytes(b'\xff\xfe\x01')
        self.assertEqual(main(['--csv',str(self.csv),'--profile',str(self.profile),'--source-id','x',
                               '--db',str(self.db),'--output',str(self.out),'--format','xlsx']),2)


if __name__=='__main__':
    unittest.main()
