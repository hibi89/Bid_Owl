"""P2-05 synthetic saved-assessment export tests, requiring no PDF font."""
from __future__ import annotations

import http.client
import io
import json
import sqlite3
import tempfile
import threading
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile
from unittest.mock import patch

from bidowl import Bid, BidOwlStore, CompanyProfile, Requirement
from report_existing import SnapshotReader, export_existing, main
from viewer import open_database, make_server, render_saved_xlsx


class ExistingReportTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.db = self.root / "synthetic.sqlite3"
        now = datetime.now(timezone.utc)
        bid = Bid(
            bid_no="ONE", title="과거 기록 시험", agency="합성 기관", category="IT",
            bid_deadline=now + timedelta(days=2), budget=1000,
            requirements=(Requirement("region", "region_any", ["부산"], "부산 소재", "p.2"),),
            source_ref="SYNTHETIC", data_as_of=now, input_line=2,
        )
        with BidOwlStore(self.db) as store:
            store.import_bids([bid], source_id="sample")
            store.save_profile(CompanyProfile("office", region="부산"))
            self.first, _ = store.assess_and_record("sample", "ONE", "office")
        self.destination = self.root / "reports"

    def test_export_saved_snapshot_xlsx_without_new_assessment(self):
        result = export_existing(
            db_path=self.db, assessment_id=self.first,
            output_dir=self.destination, format="xlsx",
        )
        self.assertEqual(result["status"], "LOCAL_EXPORTED")
        self.assertEqual(result["snapshot_status"], "PASS")
        self.assertEqual(len(result["files"]), 1)
        with ZipFile(result["files"][0]) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn("xl/worksheets/sheet2.xml", archive.namelist())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute("SELECT count(*) FROM assessments").fetchone()[0], 1)
            self.assertEqual(store.get_profile("office").region, "부산")

    def test_history_remains_frozen_after_new_profile_and_assessment(self):
        with BidOwlStore(self.db) as store:
            store.save_profile(CompanyProfile("office", region="서울"))
            second, _ = store.assess_and_record("sample", "ONE", "office")
        report = export_existing(
            db_path=self.db, assessment_id=self.first,
            output_dir=self.destination, format="xlsx",
        )
        self.assertEqual((report["snapshot_status"],report["profile_version"]), ("PASS", 1))
        newer = export_existing(
            db_path=self.db, assessment_id=second,
            output_dir=self.destination, format="xlsx",
        )
        self.assertEqual((newer["snapshot_status"],newer["profile_version"]), ("FAIL", 2))

    def test_existing_output_not_overwritten(self):
        self.destination.mkdir()
        name = self.destination / f"bidowl_review_{self.first:08d}.xlsx"
        name.write_bytes(b"KEEP")
        with self.assertRaises(FileExistsError):
            export_existing(db_path=self.db,assessment_id=self.first,
                            output_dir=self.destination,format="xlsx")
        self.assertEqual(name.read_bytes(), b"KEEP")

    def test_combined_export_cleans_first_file_after_pdf_failure(self):
        # Force failure AFTER the XLSX writer has completed successfully.
        with patch("report_existing.check_pdf_support", return_value=Path("/synthetic.ttf")):
            with patch("report_existing.write_pdf", side_effect=RuntimeError("synthetic PDF error")):
                with self.assertRaisesRegex(RuntimeError, "synthetic PDF error"):
                    export_existing(db_path=self.db, assessment_id=self.first,
                        output_dir=self.destination, format="both")
        self.assertFalse((self.destination / f"bidowl_review_{self.first:08d}.xlsx").exists())
        self.assertFalse((self.destination / f"bidowl_review_{self.first:08d}.pdf").exists())
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute("SELECT count(*) FROM assessments").fetchone()[0], 1)

    def test_preexisting_pdf_is_never_replaced_on_both(self):
        self.destination.mkdir()
        filename=self.destination / f"bidowl_review_{self.first:08d}.pdf"
        filename.write_bytes(b"KEEP-SENTINEL")
        with patch("report_existing.check_pdf_support", return_value=Path("/synthetic.ttf")):
            with self.assertRaises(FileExistsError):
                export_existing(db_path=self.db, assessment_id=self.first,
                    output_dir=self.destination, format="both")
        self.assertEqual(filename.read_bytes(), b"KEEP-SENTINEL")
        self.assertFalse((self.destination / f"bidowl_review_{self.first:08d}.xlsx").exists())

    def test_missing_assessment_and_invalid_id_do_not_create_output(self):
        with self.assertRaises(KeyError):
            export_existing(db_path=self.db,assessment_id=999999,
                            output_dir=self.destination,format="xlsx")
        self.assertFalse(self.destination.exists())
        for ident in (0,-2,True,"1"):
            with self.subTest(ident=ident), self.assertRaises(ValueError):
                export_existing(db_path=self.db,assessment_id=ident,
                                output_dir=self.destination,format="xlsx")

    def test_snapshot_reader_sqlite_connection_rejects_writes(self):
        with closing(open_database(self.db)) as conn:
            r = SnapshotReader(conn)
            record, rules = r.assessment(self.first)
            self.assertEqual(record["status"], "PASS")
            self.assertEqual(len(rules), 1)
            self.assertIsNone(r.assessment(99999))
            self.assertEqual(r.get_bid("sample","ONE",1).bid_no,"ONE")
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("DELETE FROM assessments")

    def test_readonly_download_renders_valid_historical_xlsx_bytes(self):
        with closing(open_database(self.db)) as conn:
            payload = render_saved_xlsx(conn,self.first)
            self.assertTrue(payload.startswith(b'PK'))
            with ZipFile(io.BytesIO(payload)) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn('xl/worksheets/sheet1.xml', archive.namelist())
            with self.assertRaises(sqlite3.OperationalError):
                conn.execute("UPDATE assessments SET status='FAIL'")
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.assessment(self.first)[0]['status'],'PASS')

    def test_http_download_content_disposition_and_host_validation(self):
        server=make_server(self.db,0)
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        self.addCleanup(worker.join,2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        host=f'127.0.0.1:{server.server_port}'
        def get(path, headers=None):
            connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=5)
            try:
                connection.request('GET',path,headers={'Host':host,**(headers or {})})
                response=connection.getresponse()
                return response.status,dict(response.getheaders()),response.read()
            finally:
                connection.close()
        good=f'/api/report?assessment_id={self.first}'
        status,headers,data=get(good,{'Sec-Fetch-Site':'same-origin'})
        self.assertEqual(status,200)
        self.assertIn('spreadsheetml.sheet',headers['Content-Type'])
        self.assertIn('attachment; filename=',headers['Content-Disposition'])
        self.assertEqual(headers['X-Content-Type-Options'],'nosniff')
        with ZipFile(io.BytesIO(data)) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn('xl/worksheets/sheet2.xml',archive.namelist())
        self.assertEqual(get(good,{'Host':'evil.example'})[0],403)
        self.assertEqual(get(good,{'Sec-Fetch-Site':'cross-site'})[0],403)
        for path,expected in (
            ('/api/report',400),
            ('/api/report?assessment_id=0',400),
            ('/api/report?assessment_id=abc',400),
            ('/api/report?assessment_id=999999',404),
            (good+'&format=pdf',400),
            ('/api/report?assessment_id=1&assessment_id=2',400),
        ):
            with self.subTest(path=path):
                self.assertEqual(get(path)[0],expected)
        with BidOwlStore(self.db) as store:
            self.assertEqual(store.db.execute('SELECT COUNT(*) FROM assessments').fetchone()[0],1)

    def test_command_main_json_exit_code(self):
        result = main([
            "--db",str(self.db),"--assessment-id",str(self.first),
            "--output",str(self.destination),"--format","xlsx",
        ])
        self.assertEqual(result, 0)
        self.assertTrue((self.destination/f"bidowl_review_{self.first:08d}.xlsx").exists())


if __name__ == "__main__":
    unittest.main()
