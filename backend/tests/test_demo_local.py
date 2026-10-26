"""P2-13 disposable BASIC demo tests: packaged synthetic data ONLY."""
from __future__ import annotations

import contextlib
import http.client
import io
import json
import tempfile
import threading
import unittest
from contextlib import closing
from pathlib import Path
from unittest.mock import patch

from demo_local import DEMO_SOURCE, FIXTURE_DIR, create_demo_database, serve_demo
from viewer import make_server, open_database, query_bids


class LocalDemoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="bidowl-demo-unit-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.db = self.root / "synthetic.sqlite3"

    def test_only_packaged_fake_bids_saved_in_fresh_db(self):
        result = create_demo_database(self.db)
        self.assertEqual(result["source_id"], DEMO_SOURCE)
        self.assertEqual(result["bid_count"], 2)
        self.assertEqual(result["profile_id"], "SYNTHETIC-COMPANY")
        with closing(open_database(self.db)) as conn:
            listing = query_bids(conn, {})
            self.assertEqual(listing["total"], 2)
            self.assertTrue(all(item["source_id"] == DEMO_SOURCE for item in listing["items"]))
            self.assertTrue(all(item["source_ref"] == "DEMO_ONLY" for item in listing["items"]))
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0], 1)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM assessments").fetchone()[0], 2)
            self.assertEqual(conn.execute("SELECT COUNT(*) FROM import_runs").fetchone()[0], 1)

    def test_preexisting_target_never_overwritten(self):
        self.db.write_bytes(b"USER_FILE_MUST_SURVIVE")
        with self.assertRaises(FileExistsError):
            create_demo_database(self.db)
        self.assertEqual(self.db.read_bytes(), b"USER_FILE_MUST_SURVIVE")

    def test_non_demo_csv_source_rejected_before_db_creation(self):
        fake_dir = self.root / "fixtures"
        fake_dir.mkdir()
        original = (FIXTURE_DIR / "sample_bids.csv").read_bytes()
        self.assertIn(b"DEMO_ONLY", original)
        (fake_dir / "sample_bids.csv").write_bytes(original.replace(b"DEMO_ONLY", b"OTHER_SOURCE"))
        (fake_dir / "sample_profile.json").write_bytes(
            (FIXTURE_DIR / "sample_profile.json").read_bytes()
        )
        with patch("demo_local.FIXTURE_DIR", fake_dir):
            with self.assertRaisesRegex(ValueError, "synthetic"):
                create_demo_database(self.db)
        self.assertFalse(self.db.exists())

    def test_real_profile_identifier_rejected_before_db_creation(self):
        fake_dir = self.root / "fixtures"
        fake_dir.mkdir()
        (fake_dir / "sample_bids.csv").write_bytes(
            (FIXTURE_DIR / "sample_bids.csv").read_bytes()
        )
        profile = json.loads((FIXTURE_DIR / "sample_profile.json").read_text(encoding="utf-8"))
        profile["profile_id"] = "REAL-COMPANY"
        (fake_dir / "sample_profile.json").write_text(
            json.dumps(profile, ensure_ascii=False), encoding="utf-8"
        )
        with patch("demo_local.FIXTURE_DIR", fake_dir):
            with self.assertRaisesRegex(ValueError, "synthetic"):
                create_demo_database(self.db)
        self.assertFalse(self.db.exists())

    def test_http_view_is_loopback_and_readonly(self):
        create_demo_database(self.db)
        with make_server(self.db, 0) as server:
            worker = threading.Thread(target=server.serve_forever, daemon=True)
            worker.start()
            try:
                self.assertEqual(server.server_address[0], "127.0.0.1")
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                try:
                    conn.request("GET", "/api/bids", headers={
                        "Host": f"127.0.0.1:{server.server_port}"
                    })
                    response = conn.getresponse()
                    data = json.loads(response.read())
                    self.assertEqual(response.status, 200)
                    self.assertEqual(data["total"], 2)
                    self.assertEqual({row["source_id"] for row in data["items"]}, {DEMO_SOURCE})
                finally:
                    conn.close()
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                try:
                    conn.request("POST", "/api/bids", headers={
                        "Host": f"127.0.0.1:{server.server_port}"
                    })
                    res = conn.getresponse()
                    res.read()
                    self.assertEqual(res.status, 405)
                finally:
                    conn.close()
            finally:
                server.shutdown()
                worker.join(timeout=5)

    def test_transient_db_deleted_when_demo_server_returns(self):
        observed = []

        class FakeServer:
            server_port = 42424

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def serve_forever(self, *, poll_interval):
                self.poll_interval = poll_interval
                self.assertion = poll_interval == 0.2

        fake = FakeServer()

        def inspect_server(db_path, port):
            self.assertTrue(db_path.exists())
            self.assertEqual(port, 0)
            observed.append(db_path)
            return fake

        with patch("demo_local.make_server", side_effect=inspect_server), \
             patch("demo_local.webbrowser.open", side_effect=AssertionError("browser unexpectedly launched")), \
             contextlib.redirect_stdout(io.StringIO()):
            serve_demo(open_browser=False)
        self.assertTrue(fake.assertion)
        self.assertEqual(len(observed), 1)
        self.assertFalse(observed[0].exists())
        self.assertFalse(observed[0].parent.exists())

    def test_rejects_port_outside_local_range(self):
        for port in (-1, 65536, True, "8765"):
            with self.subTest(port=port), self.assertRaises(ValueError):
                serve_demo(port=port, open_browser=False)

    def test_ui_labels_reserved_demo_source_and_launcher_exists(self):
        backend = Path(__file__).resolve().parents[1]
        html = (backend / "ui" / "index.html").read_text(encoding="utf-8")
        js = (backend / "ui" / "ui.js").read_text(encoding="utf-8")
        cmd = (backend / "START_DEMO.cmd").read_text(encoding="utf-8")
        self.assertIn('id="demo-indicator"', html)
        self.assertIn("합성 데모", html)
        self.assertIn(DEMO_SOURCE, js)
        self.assertIn("demo_local.py", cmd)
        self.assertIn('%~dp0', cmd)
        outer = (backend.parent / "START_BID_OWL_DEMO.cmd").read_text(encoding="utf-8")
        self.assertIn('backend\\START_DEMO.cmd', outer)


if __name__ == "__main__":
    unittest.main()
