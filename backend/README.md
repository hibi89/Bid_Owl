# BID OWL BASIC engine — developer guide (P1-01 → P1-03)

All code is local/offline, standard-library Python. **Development module, not yet a Windows application or commercial product.** No API calls or real customer documents are shipped. The CSV fixture under fixtures/ is synthetic.

## CSV format (P1-01)
Required columns: bid_no,title,agency,category,bid_deadline,budget,requirements. Optional: source_ref,data_as_of.
UTF-8/UTF-8-SIG; KRW budget positive integer; ISO 8601 timestamps must include seconds and time zone. requirements JSON is an array of objects {"id","kind","value","source":{"text","locator"}}. Supported literal kinds: region_any, category_any, license_all (lists of strings), staff_min and experience_total_min_krw (nonnegative integers).
Unknown rules/missing evidence are retained but evaluate to UNKNOWN. An invalid batch is entirely rejected before persistence. Maximum input 10 MiB, 10,000 bids, 100 rules/bid. Expired ≠ CSV error.

## Profiles / eligibility (P1-02)
CompanyProfile.from_mapping accepts profile_id (required), region, categories, licenses, staff_count, experience_total_krw. None = unknown, empty list for categories/licenses = explicitly empty. evaluate_bid returns a verdict and each individual condition's status/source/explanation. All values compared literally (no implicit synonyms or law interpretation). FAIL > UNKNOWN > PASS if all conditions present; no conditions = UNKNOWN. Mixed FAIL and UNKNOWN has aggregate FAIL with needs-review on unknown rules. PASS never implies final legal authorization.

## SQLite store (P1-03)
- Class: bidowl.store.BidOwlStore. Default path: Windows LOCALAPPDATA/BID_OWL/bidowl.sqlite3 or Linux XDG_DATA_HOME/bidowl/bidowl.sqlite3 (~/.local/share/bidowl/bidowl.sqlite3).
- Can supply an explicit local path; test code uses tempfile paths, NOT customer data.
- import_csv(data: bytes, source_id="...") validates the whole CSV and writes in a transaction; import_bids(bids, source_id="...") accepts already parsed Bid objects.
- Stable semantic SHA-256 of normalized content tracks a bid across imports keyed by (source_id, bid_no). Same latest content -> unchanged; changed -> append version. Reverting to older content is a fresh version; input_line excluded from semantic hash. Source id must remain stable for equivalent imports. File SHA-256 in import_runs is an audit field, NOT a government correction identifier. **Official bid amendment/차수 parsing is pending P3 API work.**
- save_profile(profile) versions company data on change. get_profile/profile version and get_bid/bid version retrieve old snapshots. assess_and_record(source_id,bid_no,profile_id) recomputes against latest stored versions and persists every condition's reason/evidence under immutable assessment IDs.
- import_runs captures accepted run counts; rejected malformed input makes no DB write. SQLite SQL is parameterized, foreign keys enabled, BEGIN IMMEDIATE transactions and rollback; schema user_version=1. Unknown/newer schema and nonempty unversioned foreign databases are rejected rather than auto-migrated. **Schema migration utility not yet implemented.**
- backup_to(new_filename) makes a SQLite-consistent backup, runs integrity_check and refuses to overwrite backups. There is no automatic periodic backup. Actual interrupted-power/corruption recovery on Windows remains unverified.
- SQLite original customer databases and exports must stay outside GitHub; backend/.gitignore provides local protection but is not a substitute for secret scanning.

## Run locally

    cd backend
    python -m unittest discover -s tests -v

P1-03 tests require no third-party packages, network, user API key, or Vercel.

Example (synthetic only):

    from pathlib import Path
    from bidowl import BidOwlStore, CompanyProfile
    with BidOwlStore(Path("local-demo.sqlite3")) as db:
        result = db.import_csv(Path("fixtures/sample_bids.csv").read_bytes(), source_id="SYNTHETIC-CSV")
        db.save_profile(CompanyProfile.from_mapping({"profile_id":"DEMO","region":"부산광역시","licenses":["소프트웨어사업자"],"staff_count":3}))
        assessment_id, outcome = db.assess_and_record("SYNTHETIC-CSV", "DEMO-2027-001", "DEMO")
        print(result, outcome.status, assessment_id)

Delete the synthetic demo database after testing. Do not commit it.

## Verification record — 2026-10-26 KST
- P1-01 prior run: 21 PASS, 0 FAIL. P1-02 prior run: 27 PASS, 0 FAIL separately (using a matching schema surface).
- **P1-03 current run: 28 PASS / 0 FAIL / 0 SKIP** under Linux CPython 3.13.5. These test a local reproduction of the P1-01/P1-02 public module contracts; new P1-03 store.py, tests/test_store.py and updated __init__.py Git blob SHAs were confirmed identical to the tested files.
- The complete 76-case suite of the exact GitHub checkout was **not** executed together in this turn. Do not advertise 76 PASS.
- Windows 11 actual install/restore/low-disk/reboot, official CSV correction identifiers, PDF/Excel, browser UI, actual production application all **untested/not implemented**.

NEXT: P1-04 local CLI + inspectable Excel/PDF reports with Korean font and source traceability tests, plus full checkout regression before MVP readiness.
