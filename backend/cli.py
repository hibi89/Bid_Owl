"""BID OWL offline local import, screening and report command-line MVP."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from bidowl import BidOwlStore, CompanyProfile, CSVImportError, parse_csv
from bidowl.report import check_pdf_support, load_review_report, write_pdf, write_xlsx
from bidowl.store import default_database_path


def positive_local_path(path: str, label: str) -> Path:
    output = Path(path).expanduser().resolve()
    if not output.is_file():
        raise ValueError(f"{label} file missing: {output}")
    return output


def execute(args: argparse.Namespace) -> dict:
    csv_path = positive_local_path(args.csv, "CSV")
    profile_path = positive_local_path(args.profile, "company profile")
    if args.format in ("pdf", "both"):
        check_pdf_support()  # fail early before importing company data
    csv_bytes = csv_path.read_bytes()
    payload = parse_csv(csv_bytes)
    bids = payload.require_valid()  # validate ALL records, no partial import
    try:
        raw_profile = json.loads(profile_path.read_text(encoding="utf-8-sig"))
    except (json.JSONDecodeError,UnicodeError) as exc:
        raise ValueError(f"Invalid profile JSON: {exc}") from exc
    company = CompanyProfile.from_mapping(raw_profile)
    db_path = Path(args.db).expanduser().resolve() if args.db else default_database_path()
    output = Path(args.output).expanduser().resolve()
    output.mkdir(parents=True,exist_ok=True)
    source_id = args.source_id
    if args.format not in {"xlsx", "pdf", "both"}:
        raise ValueError("Unsupported output format")
    exported = []
    with BidOwlStore(db_path) as store:
        result = store.import_csv(csv_bytes,source_id=source_id)
        store.save_profile(company)
        for bid in bids:
            assessment_id,decision = store.assess_and_record(source_id,bid.bid_no,company.profile_id)
            report = load_review_report(store,assessment_id)
            stem = f"bidowl_review_{assessment_id:08d}"
            outputs = []
            for ext,func in (("xlsx",write_xlsx),("pdf",write_pdf)):
                if args.format in (ext,"both"):
                    destination = func(report,output/f"{stem}.{ext}")
                    outputs.append(str(destination))
            exported.append({"bid_no":bid.bid_no,"assessment_id":assessment_id,"status":decision.status,
                             "expired":decision.is_expired,"requires_human_review":decision.requires_human_review,
                             "files":outputs})
    return {"status":"LOCAL_COMPLETE","source_id":source_id,"database":str(db_path),
            "import":{"inserted":result.inserted,"revised":result.revised,"unchanged":result.unchanged},
            "reports":exported,"disclaimer":"규칙 비교 참고용. 최종 판단은 담당자가 공고 원문 확인."}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL offline CSV / eligibility / SQLite / PDF·Excel")
    parser.add_argument("--csv",required=True,help="UTF-8 bid CSV file")
    parser.add_argument("--profile",required=True,help="Company profile JSON file")
    parser.add_argument("--source-id",required=True,help="Stable source identifier, e.g. manual-import")
    parser.add_argument("--db",help="SQLite file path (default platform local app data)")
    parser.add_argument("--output",required=True,help="Local report output directory")
    parser.add_argument("--format",default="both",choices=["both","xlsx","pdf"])
    options = parser.parse_args(argv)
    try:
        print(json.dumps(execute(options),ensure_ascii=False,indent=2))
        return 0
    except (ValueError,KeyError,CSVImportError,RuntimeError,OSError) as exc:
        if isinstance(exc,CSVImportError):
            problems=[{"code":p.code,"line":p.line,"field":p.field,"message":p.message} for p in exc.issues]
            print(json.dumps({"status":"INPUT_REJECTED","issues":problems},ensure_ascii=False),file=sys.stderr)
        else:
            print(json.dumps({"status":"FAILED","reason":str(exc)},ensure_ascii=False),file=sys.stderr)
        return 2


if __name__=="__main__":
    raise SystemExit(main())
