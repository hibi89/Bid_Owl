"""BID OWL BASIC real-importer MVP path, exercised with disposable synthetic files.

Unlike the historical CLI smoke, this uses the same real-user importer that
the Tkinter wizard calls: prepare_import -> apply_import -> read-only viewer ->
report_existing XLSX. It never uses a default customer database or network.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import tempfile
from contextlib import closing
from pathlib import Path
from xml.etree import ElementTree
from zipfile import ZipFile

from bidowl import CompanyProfile
from bidowl.report import check_pdf_support
from import_local import apply_import, plan_summary, prepare_import
from report_existing import export_existing
from viewer import open_database, query_bids, query_detail, query_profile

FIXTURES = Path(__file__).resolve().parent / "fixtures"
SOURCE_ID = "SYNTHETIC-MVP-LOCAL"
PROFILE_ID = "mvp-test-company"


def run_mvp_smoke(*, require_pdf: bool = False) -> dict:
    """Validate the genuine BASIC local backend journey, without customer data."""
    if type(require_pdf) is not bool:
        raise TypeError("require_pdf must be a boolean")
    # Optional strict release gate must fail BEFORE creating even test DB.
    if require_pdf:
        check_pdf_support()
    with tempfile.TemporaryDirectory(prefix="bidowl-basic-mvp-") as temporary:
        root = Path(temporary)
        csv_path = root / "incoming.csv"
        db = root / "basic.sqlite3"
        reports = root / "reports"
        raw = (FIXTURES / "sample_bids.csv").read_bytes()
        raw = raw.replace(b"DEMO_ONLY", b"SYNTHETIC_MVP_TEST")
        raw = raw.replace(b"DEMO-", b"MVP-")
        csv_path.write_bytes(raw)

        source_profile = json.loads(
            (FIXTURES / "sample_profile.json").read_text(encoding="utf-8-sig")
        )
        source_profile["profile_id"] = PROFILE_ID
        company = CompanyProfile.from_mapping(source_profile)
        plan = prepare_import(
            csv_path=csv_path, profile=company,
            source_id=SOURCE_ID, db_path=db,
        )
        preview = plan_summary(plan)
        if (preview["status"] != "PREVIEW_NO_WRITE"
                or preview["bid_count"] != 2
                or db.exists() or reports.exists()):
            raise AssertionError("BASIC preview changed files or failed validation")

        first = apply_import(plan)
        if (first["status"] != "IMPORTED"
                or first["import"]["inserted"] != 2
                or first["assessments_saved"] != 2
                or sum(first["eligibility_counts"].values()) != 2):
            raise AssertionError("BASIC real importer did not persist both assessments")

        exported = []
        with closing(open_database(db)) as readonly:
            list_result = query_bids(readonly, {"profile": [PROFILE_ID]})
            if list_result["total"] != 2 or len(list_result["items"]) != 2:
                raise AssertionError("BASIC viewer omitted newly imported tenders")
            profile = query_profile(readonly, {"profile_id": [PROFILE_ID]})
            if profile["version"] != 1 or profile["profile"]["region"] != "부산광역시":
                raise AssertionError("BASIC viewer company profile does not match")
            ids = set()
            for item in list_result["items"]:
                detail = query_detail(readonly, {
                    "source_id": [SOURCE_ID],
                    "bid_no": [item["bid_no"]],
                    "profile": [PROFILE_ID],
                })
                if (not detail["evidence_is_current"]
                        or not item["assessment_fresh"]
                        or not item["engine_fresh"]
                        or detail["bid"]["assessment_id"] is None):
                    raise AssertionError("BASIC latest assessment evidence is missing/stale")
                assessment_id = detail["bid"]["assessment_id"]
                if assessment_id in ids:
                    raise AssertionError("BASIC import reused the same assessment for two bids")
                ids.add(assessment_id)
                exported.append((item["bid_no"], assessment_id))
            try:
                readonly.execute("DELETE FROM bids")
            except sqlite3.OperationalError:
                pass
            else:
                raise AssertionError("BASIC viewer database was not read-only")

        report_paths = []
        for number, assessment_id in exported:
            report = export_existing(
                db_path=db, assessment_id=assessment_id,
                output_dir=reports,
                format="both" if require_pdf else "xlsx",
            )
            if report["status"] != "LOCAL_EXPORTED":
                raise AssertionError("BASIC saved assessment report did not export")
            files = [Path(path) for path in report["files"]]
            if not any(path.suffix == ".xlsx" for path in files):
                raise AssertionError("BASIC Excel export missing")
            for path in files:
                if not path.is_file() or path.stat().st_size == 0:
                    raise AssertionError("BASIC report file was empty or missing")
                if path.suffix == ".xlsx":
                    with ZipFile(path) as archive:
                        if archive.testzip() is not None:
                            raise AssertionError("BASIC XLSX ZIP integrity failed")
                        for name in archive.namelist():
                            if name.endswith((".xml", ".rels")):
                                ElementTree.fromstring(archive.read(name))
                elif path.suffix == ".pdf":
                    if not path.read_bytes().startswith(b"%PDF"):
                        raise AssertionError("BASIC PDF signature invalid")
                else:
                    raise AssertionError("BASIC exported unexpected report type")
            report_paths.extend(files)

        before = {path.name: path.read_bytes() for path in report_paths}
        second_plan = prepare_import(
            csv_path=csv_path, profile=company,
            source_id=SOURCE_ID, db_path=db,
        )
        if not plan_summary(second_plan)["backup_required"]:
            raise AssertionError("BASIC repeat preview did not flag prewrite backup")
        second = apply_import(second_plan)
        backup = Path(second["backup"]) if second["backup"] else None
        if (backup is None or not backup.is_file()
                or second["assessments_saved"] != 0
                or second["assessments_reused"] != 2):
            raise AssertionError("BASIC repeat import did not preserve existing evidence")
        if any(path.read_bytes() != before[path.name] for path in report_paths):
            raise AssertionError("BASIC repeat import changed existing report files")
        with closing(open_database(db)) as current:
            actual = current.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
        with closing(open_database(backup)) as old:
            prior = old.execute("SELECT COUNT(*) FROM assessments").fetchone()[0]
        if (actual, prior) != (2, 2):
            raise AssertionError("BASIC repeat import altered evidence or backup history")

        return {
            "status": "BASIC_MVP_SYNTHETIC_E2E_PASS",
            "path": "real CSV importer -> saved company and assessments -> "
                    "readonly viewer/details -> saved reports -> backup/no-op reimport",
            "bids": 2, "reports": len(report_paths),
            "format": "xlsx+pdf" if require_pdf else "xlsx",
            "assessments_saved": first["assessments_saved"],
            "assessments_reused_on_repeat": second["assessments_reused"],
            "backup_verified": True,
            "original_reports_preserved": True,
            "customer_data_used": False,
            "windows_gui_tested": False,
            "real_browser_tested": False,
            "pdf_tested": require_pdf,
            "pdf_dependency_optional": not require_pdf,
        }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL BASIC offline real-importer MVP QA")
    parser.add_argument("--require-pdf", action="store_true",
                        help="Fail if the optional ReportLab/Korean font PDF is unavailable")
    args = parser.parse_args(argv)
    try:
        print(json.dumps(run_mvp_smoke(require_pdf=args.require_pdf),
                         ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(json.dumps({
            "status": "BASIC_MVP_SYNTHETIC_E2E_FAILED",
            "error_type": type(exc).__name__,
            "error": str(exc)[:500],
        }, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
