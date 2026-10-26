"""P2 localhost viewer regression tests with synthetic schema-compatible SQLite data."""
from __future__ import annotations

import http.client
import json
import sqlite3
import tempfile
import threading
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import urlencode

from bidowl.engine_identity import engine_fingerprint
from viewer import make_server, open_database, query_bids, query_detail, query_profiles, query_favorites, query_profile


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
        CREATE TABLE profile_versions(profile_id TEXT,version INTEGER,payload TEXT);
        CREATE TABLE assessments(id INTEGER,source_id TEXT,bid_no TEXT,bid_version INTEGER,
          profile_id TEXT,profile_version INTEGER,status TEXT,checked_at TEXT,requires_human_review INTEGER,data_as_of TEXT);
        CREATE TABLE rule_assessments(assessment_id INTEGER,position INTEGER,rule_id TEXT,kind TEXT,
          status TEXT,reason_code TEXT,explanation TEXT,source_text TEXT,source_locator TEXT,requires_human_review INTEGER);
        CREATE TABLE assessment_engine_provenance(assessment_id INTEGER PRIMARY KEY, engine_hash TEXT NOT NULL);
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
        c.execute('INSERT INTO profile_versions VALUES (?,?,?)',('P1',1,json.dumps({'profile_id':'P1','region':'부산','categories':['IT'], 'licenses':None, 'staff_count':0,'experience_total_krw':None},ensure_ascii=False)))
        for row in [(1,'A',1,'PASS'),(2,'B',1,'FAIL'),(3,'C',1,'PASS')]:
            c.execute('INSERT INTO assessments VALUES (?,?,?,?,?,?,?,?,?,?)',
                      (row[0],'TEST',row[1],row[2],'P1',1,row[3],now.isoformat(),0,now.isoformat()))
        c.execute('INSERT INTO rule_assessments VALUES (?,?,?,?,?,?,?,?,?,?)',
                  (1,0,'r1','license_all','PASS','MATCH','면허 조건 충족','자격조건 원문','공고문 p.3',0))
        for assessment_id in (1,2,3):
            c.execute("INSERT INTO assessment_engine_provenance VALUES (?,?)",
                      (assessment_id, engine_fingerprint()))
        c.commit();c.close()

    def test_legacy_database_without_policy_provenance_shows_unknown(self):
        with closing(sqlite3.connect(self.path)) as writer:
            writer.execute("DROP TABLE assessment_engine_provenance")
            writer.commit()
        with closing(open_database(self.path)) as reader:
            rows = {r["bid_no"]: r for r in query_bids(reader, {})["items"]}
            self.assertEqual(rows["A"]["snapshot_status"], "PASS")
            self.assertEqual(rows["A"]["status"], "UNKNOWN")
            self.assertFalse(rows["A"]["assessment_fresh"])
            self.assertFalse(rows["A"]["engine_fresh"])
            self.assertTrue(rows["A"]["requires_human_review"])
            self.assertIn("판정 엔진", rows["A"]["review_reason"])

    def test_missing_rule_engine_source_never_displays_pass(self):
        from unittest.mock import patch
        with patch("viewer.engine_fingerprint", side_effect=FileNotFoundError("missing policy")):
            with closing(open_database(self.path)) as reader:
                rows = {r["bid_no"]: r for r in query_bids(reader, {})["items"]}
        self.assertEqual(rows["A"]["status"], "UNKNOWN")
        self.assertEqual(rows["A"]["snapshot_status"], "PASS")
        self.assertFalse(rows["A"]["engine_fresh"])

    def test_missing_policy_source_and_legacy_provenance_are_not_equal(self):
        from unittest.mock import patch
        with closing(sqlite3.connect(self.path)) as writer:
            writer.execute("DROP TABLE assessment_engine_provenance")
            writer.commit()
        with patch("viewer.engine_fingerprint", side_effect=FileNotFoundError("missing source")):
            with closing(open_database(self.path)) as reader:
                rows = {r["bid_no"]: r for r in query_bids(reader, {})["items"]}
        self.assertEqual(rows["A"]["status"], "UNKNOWN")
        self.assertEqual(rows["A"]["snapshot_status"], "PASS")
        self.assertFalse(rows["A"]["engine_fresh"])
        self.assertTrue(rows["A"]["requires_human_review"])

    def test_stale_policy_fingerprint_invalidates_previous_pass(self):
        with closing(sqlite3.connect(self.path)) as writer:
            writer.execute(
                "UPDATE assessment_engine_provenance SET engine_hash=? WHERE assessment_id=1",
                ("0" * 64,),
            )
            writer.commit()
        with closing(open_database(self.path)) as reader:
            rows = {r["bid_no"]: r for r in query_bids(reader, {})["items"]}
            self.assertEqual(rows["A"]["snapshot_status"], "PASS")
            self.assertEqual(rows["A"]["status"], "UNKNOWN")
            self.assertFalse(rows["A"]["engine_fresh"])
            self.assertEqual(rows["B"]["status"], "FAIL")

    def test_metadata_paging_is_exactly_equivalent_to_legacy_full_scan(self):
        from viewer import _latest_rows

        # Multiple sources, deadlines, Unicode casefold, ties and pages.
        with closing(sqlite3.connect(self.path)) as writer:
            for i in range(65):
                source = "SYN" if i % 2 else "TEST"
                number = f"PAGE-{i:03d}"
                payload = {
                    "bid_no": number,
                    "title": ("한글 AI 테스트" if i % 3 else "Straße 공공 용역"),
                    "agency": "한국 공공기관",
                    "category": ("IT" if i % 2 else "교육"),
                    "bid_deadline": self.deadline if i % 5 else self.old_deadline,
                    "budget": i * 101,
                    "source_ref": "SYNTHETIC",
                }
                writer.execute(
                    "INSERT INTO bids VALUES (?,?,?)", (source, number, 1),
                )
                writer.execute(
                    "INSERT INTO bid_versions VALUES (?,?,?,?)",
                    (source, number, 1, json.dumps(payload, ensure_ascii=False)),
                )
            writer.commit()

        def expected_full_scan(conn, filters, favorites=None):
            profile = filters.get("profile", "P1")
            page = int(filters.get("page", "1"))
            page_size = int(filters.get("page_size", "30"))
            rows = _latest_rows(conn, profile)
            categories = sorted({
                str(row["category"]) for row in rows if row["category"]
            })
            if favorites is not None:
                rows = [
                    row for row in rows
                    if (row["source_id"], row["bid_no"]) in favorites
                ]
            q = filters.get("q", "").strip().casefold()
            if q:
                rows = [
                    row for row in rows
                    if q in " ".join(
                        str(row[key]) for key in
                        ("title", "agency", "bid_no", "source_id")
                    ).casefold()
                ]
            category = filters.get("category", "").strip()
            if category:
                rows = [row for row in rows if row["category"] == category]
            status = filters.get("status", "").strip()
            if status:
                rows = [row for row in rows if row["status"] == status]
            deadline = filters.get("deadline", "").strip()
            if deadline:
                rows = [
                    row for row in rows
                    if row["expired"] == (deadline == "expired")
                ]
            rows.sort(key=lambda row: (
                row["expired"], row["deadline"] or "",
                row["source_id"], row["bid_no"],
            ))
            return {
                "items": rows[(page - 1) * page_size:page * page_size],
                "total": len(rows),
                "categories": categories,
                "page": page,
                "page_size": page_size,
            }

        favorites = {("TEST", "A"), ("SYN", "PAGE-001"),
                     ("TEST", "PAGE-002"), ("MISSING", "VOID")}
        cases = [
            ({}, None),
            ({"page_size": "1", "page": "2"}, None),
            ({"page_size": "7", "page": "6"}, None),
            ({"page_size": "4", "page": "999"}, None),
            ({"q": "AI"}, None),
            ({"q": "STRASSE"}, None),
            ({"q": "공공"}, None),
            ({"category": "IT", "q": "한글"}, None),
            ({"category": "교육", "deadline": "expired"}, None),
            ({"deadline": "open", "page_size": "6"}, None),
            ({"profile": "P1", "page_size": "3"}, None),
            ({"profile": "not-a-profile"}, None),
            ({"status": "PASS"}, None),
            ({"status": "UNKNOWN", "category": "IT"}, None),
            ({"page_size": "1", "page": "2"}, favorites),
            ({"q": "AI", "deadline": "open"}, favorites),
            ({"page_size": "20"}, set()),
        ]
        with closing(open_database(self.path)) as conn:
            for filters, favorites_for_case in cases:
                with self.subTest(filters=filters, favorites=favorites_for_case):
                    before = expected_full_scan(conn, filters, favorites_for_case)
                    output = query_bids(
                        conn, {key: [value] for key, value in filters.items()},
                        favorite_keys=favorites_for_case,
                    )
                    for key in ("items", "total", "categories",
                                "page", "page_size"):
                        self.assertEqual(output[key], before[key])
                    self.assertFalse(conn.in_transaction)

    def test_non_status_page_loads_only_selected_assessment_keys(self):
        from unittest.mock import patch
        import viewer

        with closing(open_database(self.path)) as conn:
            original = viewer._latest_rows
            with patch("viewer._latest_rows", wraps=original) as observed:
                result = query_bids(
                    conn, {"page": ["1"], "page_size": ["2"]}
                )
            self.assertEqual(result["total"], 3)
            self.assertEqual(observed.call_count, 1)
            self.assertEqual(len(observed.call_args.kwargs["candidate_keys"]), 2)
            self.assertFalse(conn.in_transaction)
            with patch("viewer._latest_rows", wraps=original) as observed:
                result = query_bids(conn, {"status": ["PASS"]})
            self.assertEqual(result["total"], 1)
            self.assertEqual(observed.call_count, 1)
            self.assertEqual(len(observed.call_args.kwargs["candidate_keys"]), 1)

    def test_status_filters_equal_full_snapshot_across_profiles_and_provenance(self):
        from viewer import _latest_rows
        from unittest.mock import patch

        query_variants = [
            {"status": "PASS"}, {"status": "FAIL"},
            {"status": "UNKNOWN"}, {"status": "PASS", "profile": "P1"},
            {"status": "UNKNOWN", "profile": "P1"},
            {"status": "UNKNOWN", "profile": "missing"},
            {"status": "PASS", "deadline": "open"},
            {"status": "FAIL", "deadline": "expired"},
            {"status": "UNKNOWN", "category": "IT"},
            {"status": "UNKNOWN", "q": "사업"},
            {"status": "PASS", "page_size": "1", "page": "2"},
        ]
        with closing(open_database(self.path)) as conn:
            for filters in query_variants:
                with self.subTest(filters=filters):
                    original = _latest_rows(conn, filters.get("profile", ""))
                    filtered = [x for x in original if x["status"] == filters["status"]]
                    if filters.get("deadline"):
                        filtered = [x for x in filtered if x["expired"] == (filters["deadline"] == "expired")]
                    if filters.get("category"):
                        filtered = [x for x in filtered if x["category"] == filters["category"]]
                    if filters.get("q"):
                        term = filters["q"].casefold()
                        filtered = [x for x in filtered if term in " ".join(
                            str(x[k]) for k in ("title","agency","bid_no","source_id")
                        ).casefold()]
                    filtered.sort(key=lambda x: (
                        x["expired"], x["deadline"] or "", x["source_id"], x["bid_no"]
                    ))
                    page = int(filters.get("page", "1"))
                    size = int(filters.get("page_size", "30"))
                    with patch("viewer._latest_rows", wraps=_latest_rows) as full_load:
                        actual = query_bids(conn, {k: [v] for k,v in filters.items()})
                    self.assertEqual(actual["total"], len(filtered))
                    self.assertEqual(actual["items"], filtered[(page-1)*size:page*size])
                    self.assertEqual(full_load.call_count, 1)
                    self.assertEqual(len(full_load.call_args.kwargs["candidate_keys"]), len(actual["items"]))
                    self.assertFalse(conn.in_transaction)

    def test_missing_or_mismatched_engine_hash_never_passes_status_filter(self):
        from viewer import _latest_rows
        from unittest.mock import patch
        import viewer

        with closing(sqlite3.connect(self.path)) as writer:
            writer.execute(
                "UPDATE assessment_engine_provenance SET engine_hash=? WHERE assessment_id=1",
                ("0" * 64,)
            )
            writer.commit()
        with closing(open_database(self.path)) as conn:
            self.assertEqual(query_bids(conn, {"status": ["PASS"]})["total"], 0)
            unknown = query_bids(conn, {"status": ["UNKNOWN"]})
            self.assertEqual({x["bid_no"] for x in unknown["items"]}, {"A", "C"})
        with closing(sqlite3.connect(self.path)) as writer:
            writer.execute("DROP TABLE assessment_engine_provenance")
            writer.commit()
        with closing(open_database(self.path)) as conn:
            self.assertEqual(query_bids(conn, {"status": ["PASS"]})["total"], 0)
            self.assertEqual(query_bids(conn, {"status": ["UNKNOWN"]})["total"], 3)
            with patch("viewer.engine_fingerprint", side_effect=FileNotFoundError("missing policy")):
                self.assertEqual(query_bids(conn, {"status": ["PASS"]})["total"], 0)
                unknown = query_bids(conn, {"status": ["UNKNOWN"]})
                self.assertEqual(unknown["total"], 3)
                self.assertTrue(all(x["status"] == "UNKNOWN" for x in unknown["items"]))

    def test_status_query_batches_over_old_sqlite_parameter_limit(self):
        from viewer import _latest_rows
        from unittest.mock import patch
        import viewer

        now = datetime.now(timezone.utc)
        with closing(sqlite3.connect(self.path)) as writer:
            for i in range(425):
                bid_no = f"BIG-{i:04d}"
                payload = {
                    "bid_no": bid_no, "title": f"합성 사업 {i}",
                    "agency": "샘플기관", "category": "IT",
                    "bid_deadline": self.deadline, "source_ref": "SYNTHETIC",
                }
                writer.execute("INSERT INTO bids VALUES (?,?,?)", ("BATCH", bid_no, 1))
                writer.execute("INSERT INTO bid_versions VALUES (?,?,?,?)",
                    ("BATCH", bid_no, 1, json.dumps(payload, ensure_ascii=False)))
                if i % 3 == 0:
                    aid = 1000 + i
                    writer.execute("INSERT INTO assessments VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (aid, "BATCH", bid_no, 1, "P1", 1,
                         "FAIL" if i % 2 else "PASS", now.isoformat(), 0, now.isoformat()))
                    writer.execute("INSERT INTO assessment_engine_provenance VALUES (?,?)",
                                   (aid, engine_fingerprint()))
            writer.commit()
        with closing(open_database(self.path)) as conn:
            from viewer import _status_for_candidate_keys
            keys = [("BATCH", f"BIG-{i:04d}") for i in range(425)]
            statuses = _status_for_candidate_keys(conn, keys, "P1")
            self.assertEqual(len(statuses), 425)
            self.assertEqual(statuses[("BATCH", "BIG-0000")], "PASS")
            self.assertEqual(statuses[("BATCH", "BIG-0003")], "FAIL")
            self.assertEqual(statuses[("BATCH", "BIG-0001")], "UNKNOWN")
            result = query_bids(conn, {"status": ["PASS"], "page_size": ["10"]})
            baseline = [x for x in _latest_rows(conn, "P1") if x["status"] == "PASS"]
            self.assertGreater(result["total"], 10)
            self.assertEqual(result["total"], len(baseline))

    def test_filtered_favorites_use_status_shortlist_not_full_assessment_scan(self):
        from unittest.mock import patch
        import viewer
        with closing(open_database(self.path)) as conn:
            with patch("viewer._latest_rows", wraps=viewer._latest_rows) as full_load:
                result = query_favorites(conn, {
                    "favorites": [["TEST", "A"], ["TEST", "B"], ["TEST", "C"]],
                    "filters": {"status": "UNKNOWN", "page_size": "1"},
                })
            self.assertEqual(result["total"], 1)
            self.assertEqual(result["items"][0]["bid_no"], "C")
            self.assertEqual(len(full_load.call_args.kwargs["candidate_keys"]), 1)
            self.assertFalse(conn.in_transaction)

    def test_empty_page_and_no_favorites_never_request_full_assessment_scan(self):
        from unittest.mock import patch
        import viewer

        with closing(open_database(self.path)) as conn:
            original = viewer._latest_rows
            with patch("viewer._latest_rows", wraps=original) as observed:
                output = query_bids(
                    conn, {"page": ["999"], "page_size": ["1"]},
                    favorite_keys=set(),
                )
            self.assertEqual(output["total"], 0)
            self.assertEqual(output["items"], [])
            self.assertEqual(output["categories"], ["IT", "교육"])
            self.assertEqual(observed.call_count, 1)
            self.assertEqual(observed.call_args.kwargs["candidate_keys"], [])
            self.assertFalse(conn.in_transaction)

    def test_filters_and_stale_assessment_are_conservative(self):
        with closing(open_database(self.path)) as c:
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

    def test_detail_fetch_is_key_scoped(self):
        from viewer import _latest_rows
        with closing(open_database(self.path)) as conn:
            ids = [(r['source_id'], r['bid_no']) for r in _latest_rows(conn, 'P1', ('TEST','B'))]
            self.assertEqual(ids,[('TEST','B')])
            self.assertEqual(_latest_rows(conn, 'P1', ('TEST','MISSING')),[])
            detail=query_detail(conn,{'source_id':['TEST'],'bid_no':['A'],'profile':['P1']})
            self.assertEqual(detail['bid']['bid_no'],'A')
            self.assertEqual(detail['rules'][0]['rule_id'],'r1')

    def test_schema_length_identifiers_reach_detail_and_profile_filters(self):
        # Stored source/bid/profile IDs are allowed up to 300 characters.
        # A shared 160-character URL argument limit made those records unviewable.
        source = '출' * 220
        number = '공' * 220
        profile = '회' * 220
        with closing(sqlite3.connect(self.path)) as writer:
            record = {'bid_no':number, 'title':'긴 ID 합성 공고',
                'agency':'테스트 기관','category':'IT',
                'bid_deadline':self.deadline,'budget':1200,
                'data_as_of':datetime.now(timezone.utc).isoformat(),
                'source_ref':'SYNTHETIC','requirements':[]}
            writer.execute('INSERT INTO bids VALUES (?,?,?)',(source,number,1))
            writer.execute('INSERT INTO bid_versions VALUES (?,?,?,?)',
                           (source,number,1,json.dumps(record,ensure_ascii=False)))
            writer.execute('INSERT INTO profiles VALUES (?,?)',(profile,1))
            writer.execute('INSERT INTO profile_versions VALUES (?,?,?)',
                           (profile,1,json.dumps({'profile_id':profile})))
            writer.execute('INSERT INTO assessments VALUES (?,?,?,?,?,?,?,?,?,?)',
                (400,source,number,1,profile,1,'UNKNOWN',
                 datetime.now(timezone.utc).isoformat(),1,
                 datetime.now(timezone.utc).isoformat()))
            writer.commit()
        with closing(open_database(self.path)) as conn:
            detail=query_detail(conn,{'source_id':[source],'bid_no':[number],
                                      'profile':[profile]})
            self.assertEqual(detail['bid']['assessment_id'],400)
            self.assertEqual(detail['bid']['bid_no'],number)
            self.assertEqual(detail['bid']['source_id'],source)
            result=query_bids(conn,{'profile':[profile]})
            self.assertTrue(any(item['bid_no']==number for item in result['items']))
            self.assertEqual(query_profile(conn,{'profile_id':[profile]})['version'],1)
            with self.assertRaises(ValueError):
                query_detail(conn,{'source_id':['X'*301],'bid_no':[number]})
        # HTTP percent-encoding of three long Korean identifiers exceeds 1 KB.
        # It must work without relaxing parsed field or route-size boundaries.
        server=make_server(self.path,0)
        worker=threading.Thread(target=server.serve_forever,daemon=True)
        worker.start()
        try:
            host=f'127.0.0.1:{server.server_port}'
            target='/api/detail?'+urlencode({
                'source_id':source,'bid_no':number,'profile':profile})
            self.assertGreater(len(target),1024)
            self.assertLess(len(target),12288)
            for path, expected in ((target,200),('/api/bids?'+'x'*12290,414)):
                connection=http.client.HTTPConnection('127.0.0.1',server.server_port,timeout=5)
                try:
                    connection.request('GET',path,headers={'Host':host})
                    response=connection.getresponse()
                    result=json.loads(response.read())
                    self.assertEqual(response.status,expected)
                    if expected==200:
                        self.assertEqual(result['bid']['bid_no'],number)
                finally:
                    connection.close()
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=3)

    def test_read_only_and_rule_provenance(self):
        with closing(open_database(self.path)) as c:
            self.assertEqual(query_profiles(c)['profiles'][0]['profile_id'],'P1')
            detail=query_detail(c,{'source_id':['TEST'],'bid_no':['A']})
            self.assertEqual(detail['rules'][0]['source_text'],'자격조건 원문')
            self.assertEqual(detail['rules'][0]['source_locator'],'공고문 p.3')
            self.assertTrue(detail['evidence_is_current'])
            self.assertFalse(query_detail(c,{'source_id':['TEST'],'bid_no':['C']})['evidence_is_current'])
            with self.assertRaises(sqlite3.OperationalError):
                c.execute("DELETE FROM bids")

    def test_input_validation_and_missing_data(self):
        with closing(open_database(self.path)) as c:
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

    def test_global_favorites_filter_before_pagination(self):
        with closing(open_database(self.path)) as conn:
            # B is not among first two open bids but must still be found globally.
            all_page = query_bids(conn, {'page':['1'], 'page_size':['1']})
            self.assertNotEqual(all_page['items'][0]['bid_no'], 'B')
            saved = [['TEST', 'B'], ['TEST', 'C']]
            response = query_favorites(conn, {'favorites': saved, 'filters': {'page':'1', 'page_size':'1'}})
            self.assertEqual(response['total'], 2)
            self.assertEqual(response['items'][0]['bid_no'], 'C')
            next_page = query_favorites(conn, {'favorites': saved, 'filters': {'page':'2', 'page_size':'1'}})
            self.assertEqual(next_page['items'][0]['bid_no'], 'B')
            checked = query_favorites(conn, {'favorites': saved, 'filters': {'status':'UNKNOWN'}})
            self.assertEqual([b['bid_no'] for b in checked['items']], ['C'])
            self.assertEqual(query_favorites(conn, {'favorites': [], 'filters': {}})['total'], 0)
            for invalid in (
                {'favorites':[['TEST','B']], 'filters': {'sort':'DROP TABLE bids'}},
                {'favorites': [['TEST']], 'filters': {}},
                {'favorites': [[11,'B']], 'filters': {}},
                {'favorites': [['TEST','B']]*1001, 'filters': {}},
                {'favorites': 'TEST', 'filters': {}},
                {'favorites': [], 'filters': {'page':1}},
            ):
                with self.subTest(invalid=repr(invalid)[:60]), self.assertRaises(ValueError):
                    query_favorites(conn, invalid)
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM bids').fetchone()[0], 3)

    def test_http_favorites_query_same_origin_and_bounded_body(self):
        server = make_server(self.path, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(thread.join, 2)
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        url = '/api/bids/favorites'
        host = f'127.0.0.1:{server.server_port}'
        base = {'Host': host, 'Origin': f'http://{host}', 'Content-Type':'application/json'}
        def post(payload, headers=None):
            con = http.client.HTTPConnection('127.0.0.1', server.server_port, timeout=3)
            con.request('POST', url, body=payload, headers=headers if headers is not None else base)
            response = con.getresponse()
            result = (response.status, response.read())
            con.close()
            return result
        body = json.dumps({'favorites':[['TEST','B']], 'filters': {'page':'1', 'page_size':'30'}}).encode()
        status, raw = post(body)
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(raw)['total'], 1)
        self.assertEqual(json.loads(raw)['items'][0]['bid_no'], 'B')
        self.assertEqual(post(body, {**base, 'Origin':'http://evil.example'})[0], 403)
        self.assertEqual(post(body, {k:v for k,v in base.items() if k!='Origin'})[0], 403)
        self.assertEqual(post(body, {**base, 'Host':'evil.example'})[0], 403)
        self.assertEqual(post(body, {**base, 'Content-Type':'text/plain'})[0], 415)
        self.assertEqual(post(b'{no-json')[0], 400)
        self.assertEqual(post(body, {**base, 'Content-Length':'1048577'})[0], 413)
        self.assertEqual(post(body, {**base, 'Content-Length':'0'})[0], 413)
        self.assertEqual(post(json.dumps({'favorites': [['TEST','B']]*1001, 'filters':{}}).encode())[0], 400)
        self.assertEqual(post(body, {**base, 'Host':host})[0], 200)

    def test_current_profile_is_read_only_and_unmodified(self):
        with closing(open_database(self.path)) as conn:
            found=query_profile(conn, {'profile_id':['P1']})
            self.assertTrue(found['read_only'])
            self.assertEqual(found['version'],1)
            self.assertEqual(found['profile']['region'],'부산')
            self.assertEqual(found['profile']['staff_count'],0)
            with self.assertRaises(LookupError):
                query_profile(conn, {'profile_id':['unknown']})
            for bad in ({}, {'profile_id':['']}, {'profile_id':['P1','other']},
                        {'profile_id':['x'*301]}):
                with self.subTest(bad=bad), self.assertRaises(ValueError):
                    query_profile(conn,bad)
            self.assertEqual(conn.execute('SELECT count(*) FROM profiles').fetchone()[0],1)

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
        # Only export a local JSON, never permit a browser route to mutate SQLite.
        self.assertIn('id="create-profile"',html)
        self.assertIn('id="edit-profile"',html)
        self.assertIn("creating?'--create'",js)
        self.assertIn('profile_id:chosenId',js)
        self.assertIn('--apply --backup',js)

if __name__=='__main__':unittest.main()