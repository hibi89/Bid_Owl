"""Disposable, offline BID OWL BASIC walkthrough.

This intentionally uses packaged, clearly synthetic fixtures only.
It never opens, writes, imports, or discovers the user's regular BID OWL DB.
Press Ctrl+C / close the console to end the demo and delete its temporary DB.
No ReportLab, external API, AI key, network service, or installed font required.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import sys
import tempfile
import webbrowser
from pathlib import Path

from bidowl import BidOwlStore, CompanyProfile, parse_csv
from viewer import make_server

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
DEMO_SOURCE = "BIDOWL_SYNTHETIC_DEMO"


def create_demo_database(path: Path) -> dict:
    """Build a new demo-only SQLite file; reject unsafe fixture edits before opening it."""
    if not isinstance(path, Path):
        raise TypeError("path must be a pathlib.Path")
    if path.exists():
        raise FileExistsError("Demo refuses to overwrite an existing file")
    raw_csv = (FIXTURE_DIR / "sample_bids.csv").read_bytes()
    bids = parse_csv(raw_csv).require_valid()
    if not bids or any(
        not bid.bid_no.startswith("DEMO-") or bid.source_ref != "DEMO_ONLY"
        for bid in bids
    ):
        raise ValueError("Only packaged, explicitly synthetic bid fixtures may be used")
    profile_data = json.loads((FIXTURE_DIR / "sample_profile.json").read_text(encoding="utf-8-sig"))
    company = CompanyProfile.from_mapping(profile_data)
    if not company.profile_id.startswith("SYNTHETIC-"):
        raise ValueError("Demo company profile must be explicitly synthetic")
    # No persistent default_database_path(): caller passes a fresh temporary path.
    with BidOwlStore(path) as store:
        imported = store.import_bids(bids, source_id=DEMO_SOURCE)
        if imported.inserted != len(bids):
            raise RuntimeError("Demo bid import incomplete")
        store.save_profile(company)
        for bid in bids:
            store.assess_and_record(DEMO_SOURCE, bid.bid_no, company.profile_id)
    return {"source_id": DEMO_SOURCE, "bid_count": len(bids), "profile_id": company.profile_id}


def serve_demo(*, port: int = 0, open_browser: bool = True) -> None:
    """Serve a loopback-only, temporary database until interrupted."""
    if type(port) is not int or not 0 <= port <= 65535:
        raise ValueError("Demo port must be an integer from 0 to 65535")
    with tempfile.TemporaryDirectory(prefix="bidowl-synthetic-demo-") as scratch:
        path = Path(scratch) / "demo_only.sqlite3"
        details = create_demo_database(path)
        with make_server(path, port) as server:
            url = f"http://127.0.0.1:{server.server_port}/"
            print("BID OWL — 합성 데모 / 가상 공고만 표시됩니다.", flush=True)
            print(f"공고 {details['bid_count']}건 · 실제 고객 DB 및 공공 API 사용 안 함", flush=True)
            print(f"로컬 주소: {url}", flush=True)
            print("종료: Ctrl+C. 데모 DB는 종료 시 삭제됩니다.", flush=True)
            if open_browser:
                try:
                    if not webbrowser.open(url, new=2):
                        print("브라우저가 열리지 않으면 위 로컬 주소를 직접 여세요.", flush=True)
                except (OSError, webbrowser.Error):
                    print("브라우저 시작 실패: 위 로컬 주소를 직접 여세요.", flush=True)
            server.serve_forever(poll_interval=0.2)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL isolated offline synthetic demo")
    parser.add_argument("--no-browser", action="store_true", help="Do not automatically open a browser")
    parser.add_argument("--port", type=int, default=0, help="Local loopback port (default random free port)")
    args = parser.parse_args(argv)
    try:
        serve_demo(port=args.port, open_browser=not args.no_browser)
        return 0
    except KeyboardInterrupt:
        print("\n합성 데모 종료. 임시 데이터 삭제 완료.", flush=True)
        return 0
    except (OSError, ValueError, TypeError, RuntimeError, sqlite3.Error, json.JSONDecodeError) as exc:
        print(f"DEMO_FAILED: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
