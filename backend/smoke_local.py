"""One-command local synthetic end-to-end smoke; never touches a customer database.

Exercises real CSV import, rule assessment, XLSX, loopback HTTP, global
favorites, saved-report replay and backed-up company profile reassessment.
"""
from __future__ import annotations

import http.client
import io
import json
import tempfile
import threading
from contextlib import redirect_stdout
from pathlib import Path
from zipfile import ZipFile

from bidowl import BidOwlStore
from cli import main as cli_main
from profile_workflow import execute as profile_edit
from report_existing import export_existing
from viewer import make_server


FIXTURES = Path(__file__).resolve().parent / "fixtures"


def run_smoke() -> dict:
    """Returns measured assertions; the caller owns no persistent files."""
    with tempfile.TemporaryDirectory(prefix="bidowl-synthetic-") as scratch:
        root = Path(scratch)
        db = root / "only_synthetic.sqlite3"
        reports = root / "initial_reports"
        argv = [
            "--csv", str(FIXTURES / "sample_bids.csv"),
            "--profile", str(FIXTURES / "sample_profile.json"),
            "--source-id", "SYNTHETIC-SMOKE",
            "--db", str(db), "--output", str(reports), "--format", "xlsx",
        ]
        with redirect_stdout(io.StringIO()) as output:
            if cli_main(argv) != 0:
                raise AssertionError("Synthetic CLI import/export failed")
        imported = json.loads(output.getvalue())
        if len(imported["reports"]) != 2 or imported["import"]["inserted"] != 2:
            raise AssertionError("Expected exactly two synthetic imported bids")
        with ZipFile(imported["reports"][0]["files"][0]) as archive:
            if archive.testzip() is not None:
                raise AssertionError("Synthetic XLSX archive is corrupted")
        first_id = imported["reports"][0]["assessment_id"]
        with BidOwlStore(db) as store:
            prior = store.assessment(first_id)[0]["status"]
            if store.db.execute("SELECT count(*) FROM assessments").fetchone()[0] != 2:
                raise AssertionError("Expected two historical assessments")

        server = make_server(db, 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host = f"127.0.0.1:{server.server_port}"

        def http_json(method: str, url: str, body: dict | None = None) -> dict:
            payload = json.dumps(body).encode() if body is not None else None
            headers = {"Host": host}
            if method == "POST":
                headers.update({"Origin": f"http://{host}", "Content-Type": "application/json"})
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            try:
                conn.request(method, url, body=payload, headers=headers)
                response = conn.getresponse()
                data = json.loads(response.read())
                if response.status != 200:
                    raise AssertionError(f"Loopback {url} status={response.status}: {data}")
                return data
            finally:
                conn.close()

        try:
            listed = http_json("GET", "/api/bids")
            if listed["total"] != 2:
                raise AssertionError("Viewer did not see the two synthetic bids")
            selected = listed["items"][0]
            detail = http_json(
                "GET", "/api/detail?source_id=SYNTHETIC-SMOKE&bid_no=" + selected["bid_no"]
            )
            if detail["bid"]["bid_no"] != selected["bid_no"]:
                raise AssertionError("Detail API returned wrong saved bid")
            # Binary attachment path is intentionally not handled by http_json.
            download = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=5)
            try:
                download.request("GET", f"/api/report?assessment_id={first_id}",
                                 headers={"Host":host,"Sec-Fetch-Site":"same-origin"})
                attachment = download.getresponse()
                download_bytes = attachment.read()
                if attachment.status != 200 or not download_bytes.startswith(b"PK"):
                    raise AssertionError("Read-only report download did not return XLSX")
                with ZipFile(io.BytesIO(download_bytes)) as archive:
                    if archive.testzip() is not None:
                        raise AssertionError("Downloaded XLSX is corrupted")
            finally:
                download.close()
            favorites = http_json("POST", "/api/bids/favorites", {
                "favorites": [[selected["source_id"], selected["bid_no"]]],
                "filters": {"page": "1", "page_size": "1"}
            })
            if favorites["total"] != 1:
                raise AssertionError("Global favorites returned incorrect count")
            company = http_json("GET", "/api/profile?profile_id=SYNTHETIC-COMPANY")
            if company["version"] != 1 or company["profile"]["region"] != "부산광역시":
                raise AssertionError("Read-only profile view incorrect")

            export = export_existing(
                db_path=db, assessment_id=first_id, format="xlsx",
                output_dir=root / "replayed_reports",
            )
            if export["snapshot_status"] != prior:
                raise AssertionError("Re-export changed the historical assessment")
            updated = dict(company["profile"])
            updated["region"] = "서울특별시"
            edit_json = root / "updated-profile.json"
            edit_json.write_text(json.dumps(updated, ensure_ascii=False), encoding="utf-8")
            preview = profile_edit(
                db_path=db, profile_path=edit_json, expected_version=1, reassess=True
            )
            if preview["status"] != "PREVIEW" or preview["reassess_count"] != 2:
                raise AssertionError("Profile preview not conservative")
            backup = root / "before-update.sqlite3"
            applied = profile_edit(
                db_path=db, profile_path=edit_json, expected_version=1,
                reassess=True, apply=True, backup_path=backup,
            )
            if applied["status"] != "APPLIED" or applied["assessments_saved"] != 2:
                raise AssertionError("Profile revision/reassessment failed")
            with BidOwlStore(db) as store:
                if store.get_profile("SYNTHETIC-COMPANY", 1).region != "부산광역시":
                    raise AssertionError("Historical company version changed")
                if store.get_profile("SYNTHETIC-COMPANY").region != "서울특별시":
                    raise AssertionError("Current company version not saved")
                if store.assessment(first_id)[0]["status"] != prior:
                    raise AssertionError("Historical assessment mutated")
                if store.db.execute("SELECT count(*) FROM assessments").fetchone()[0] != 4:
                    raise AssertionError("Expected four immutable assessments")
            with BidOwlStore(backup) as old:
                if old.db.execute("SELECT count(*) FROM assessments").fetchone()[0] != 2:
                    raise AssertionError("Backup did not preserve pre-edit DB")
            live = http_json("GET", "/api/bids?profile=SYNTHETIC-COMPANY")
            if live["total"] != 2 or not all(r["assessment_fresh"] for r in live["items"]):
                raise AssertionError("Revised assessments missing from viewer")
            return {
                "status": "SYNTHETIC_E2E_PASS", "source_id": "SYNTHETIC-SMOKE",
                "imported": 2, "http_endpoints": 5,
                "favorites_checked": 1, "historical_assessment_preserved": True,
                "backup_verified": True, "new_profile_version": 2,
                "new_assessments": 2, "pdf_tested": False,
                "browser_tested": False, "windows_tested": False,
            }
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=3)


def main() -> int:
    try:
        print(json.dumps(run_smoke(), ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "SYNTHETIC_E2E_FAILED", "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
