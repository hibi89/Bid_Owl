"""P2 localhost viewer regression tests with synthetic schema-compatible SQLite data."""
from __future__ import annotations

import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from viewer import make_server, open_database, query_bids, query_detail, query_profiles


class ViewerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "synthetic.sqlite3"
        c = sqlite3.connect(self.path)
        c.executescript("""
        CREATE TABLE bids(source_id TEXT,bid_no TEXT,latest_version INTEGER);
        CREATE TABLE bid_versions(source_id TEXT,bid_no TEXT,version INTEGER,payload TEXT);
        CREATE TABLE profiles(profile_id TEXT,latest_version INTEGER);
        CREATE TABLE assessments(id INTEGER,source_id TEXT,bid_no TEXT,bid_version INTEGER,
          profile_id TEXT,profile_version INTEGER,status TEXT,checked_at TEXT,requires_human_review INTEGER,data_as_of TEXT);
        CREATE TABLE rule_assessments(assessment_id INTEGER,position INTEGER,rule_id TEXT,kind TEXT,
          status TEXT,reason_code TEXT,explanation TEXT,source_text TEXT,source_locator TEXT,requires_human_review INTEGER);
        PRAGMA user_version=1;
        """)
        now = datetime.now(timezone.utc)
        self.deadline = (now + timedelta(days=2)).isoformat()
        self.old_deadline = (now - timedelta(days=1)).isoformat()
        def add_bid(no, title, category, deadline, version=1):
            p = {'bid_no':no,'title':title,'agency':'한국 공공기관','category':category,
                 'bid_deadline':deadline,'budget':123000,'data_as_of':now.isoformat(),
                 'source_ref':'SYNTHETIC','requirements':[]}
            c.execute('INSERT INTO bids VALUES (?,?,?)',('TEST',no,version))
            c.execute('INSERT INTO bid_versions VALUES (?,?,?,?)',('TEST',no,version,json.dumps(p,ensure_ascii=False)))
        add_bid('A','AI 유지보수','IT',self.deadline)
        add_bid('B','교육 행사','교육',self.old_deadline)
        add_bid('C','미검증 사업','IT',self.deadline,version=2)
        c.execute('INSERT INTO profiles VALUES (?,?)',('P1',1))
        for row in [(1,'A',1,'PASS'),(2,'B',1,'FAIL'),(3,'C',1,'PASS')]:
            c.execute('INSERT INTO assessments VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (row[0],'TEST',row[1],row[2],'P1',1,row[3],now.isoformat(),0,now.isoformat()))
        c.execute('INSERT INTO rule_assessments VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (1,0,'r1','license_all','PASS','MATCH','면허 조건 충족','자격조건 원문','공고문 p.3',0))
        c.commit();c.close()

    def test_filters_and_stale_assessment_are_conservative(self):
        with open_database(self.path) as c:
            data=query_bids(c,{})
            self.assertEqual(data['total'],3)
            self.assertEqual(data['categories'],['IT','교육'])
            by_no={x['bid_no']:x for x in data['items']}
            self.assertEqual(by_no['A']['status'],'PASS')
            self.assertEqual(by_no['B']['status'],'FAIL')
            self.assertTrue(by_no['B']['expired'])
            self.assertEqual(by_no['C']['status'],'UNKNOWN')
            self.assertEqual(by_no['C']['snapshot_status'],'PASS')
            self.assertFalse(by_no['C']['assessment_fresh'])
            self.assertTrue(by_no['C']['requires_human_review'])
            self.assertEqual(query_bids(c,{'q':['ai']})['total'],1)
            self.assertEqual(query_bids(c,{'category':['IT'],'status':['UNKNOWN']})['total'],1)
            self.assertEqual(query_bids(c,{'deadline':['open']})['total'],2)
            self.assertEqual(query_bids(c,{'deadline':['expired']})['total'],1)
            self.assertEqual(query_bids(c,{'page_size':['1'],'page':['2']})['page'],2)

    def test_read_only_and_rule_provenance(self):
        with open_database(self.path) as c:
            self.assertEqual(query_profiles(c)['profiles'][0]['profile_id'],'P1')
            detail=query_detail(c,{'source_id':['TEST'],'bid_no':['A']})
            self.assertEqual(detail['rules'][0]['source_text'],'자격조건 원문')
            self.assertEqual(detail['rules'][0]['source_locator'],'공고문 p.3')
            self.assertTrue(detail['evidence_is_current'])
            self.assertFalse(query_detail(c,{'source_id':['TEST'],'bid_no':['C']})['evidence_is_current'])
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("DELETE FROM bids")

    def test_input_validation_and_missing_data(self):
        with open_database(self.path) as c:
            for q in ({'page':['0']},{'page_size':['101']},{'status':['OTHER']},{'q':['x'*121]},
                      {'page':['1 OR 1=1']},{'q':['A','B']}):
                with self.subTest(q=q),self.assertRaises(ValueError):query_bids(c,q)
            with self.assertRaises(LookupError):query_detail(c,{'source_id':['TEST'],'bid_no':['Z']})
            with self.assertRaises(ValueError):query_detail(c,{'source_id':["' OR 1=1 --"],'bid_no':['']})
        with self.assertRaises(FileNotFoundError):open_database(self.path.parent/'missing.db')
        other=self.path.parent/'invalid.db';sqlite3.connect(other).close()
        with self.assertRaises(ValueError):open_database(other)

    def test_http_local_host_origin_static_and_write_rejection(self):
        server=make_server(self.path,0)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(thread.join,2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        def get(method,path,headers=None):
            connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=3)
            base={'Host':f'127.0.0.1:{server.server_port}'}
            base.update(headers or {})
            connection.request(method,path,headers=base)
            response=connection.getresponse()
            result=response.status,response.read(),dict(response.getheaders())
            connection.close();return result
        status,raw,headers=get('GET','/api/bids?q=AI')
        self.assertEqual(status,200)
        self.assertEqual(json.loads(raw)['total'],1)
        self.assertEqual(headers['X-Content-Type-Options'],'nosniff')
        self.assertIn("default-src 'none'",headers['Content-Security-Policy'])
        self.assertEqual(get('GET','/')[0],200)
        self.assertEqual(get('GET','/ui.js')[0],200)
        self.assertEqual(get('GET','/ui.css')[0],200)
        self.assertEqual(get('GET','/../secrets')[0],404)
        self.assertEqual(get('GET','/api/bids',{'Host':'evil.example'})[0],403)
        self.assertEqual(get('GET','/api/bids',{'Origin':'http://evil.example'})[0],403)
        self.assertEqual(get('POST','/api/bids')[0],405)
        self.assertEqual(get('GET','/api/detail?'+urlencode({'source_id':'TEST','bid_no':'A'}))[0],200)

    def test_all_seven_themes_and_safe_render_path(self):
        ui=Path(__file__).resolve().parents[1]/'ui'
        css=(ui/'ui.css').read_text(encoding='utf-8')
        html=(ui/'index.html').read_text(encoding='utf-8')
        js=(ui/'ui.js').read_text(encoding='utf-8')
        for theme in ('cloud','obsidian','midnight','graphite','emerald','sand','iris'):
            self.assertIn(f'data-theme="{theme}"',css)
            self.assertIn(f'value="{theme}"',html)
        self.assertNotIn('.innerHTML',js)
        self.assertIn('textContent',js)
        self.assertIn('localStorage',js)

if __name__=='__main__':unittest.main()