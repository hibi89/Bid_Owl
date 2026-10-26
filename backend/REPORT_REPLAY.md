# P2-05 Saved report re-export and local synthetic verification

Use only on a local copy of BID OWL with an existing schema-v1 SQLite database.

From backend, re-export a prior saved assessment without re-importing/re-evaluating or writing to the source DB:

    python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./replayed_reports --format both

This opens SQLite read-only; it uses the original saved profile/bid versions and evidence. Historical PASS/FAIL is not a new/current legal eligibility result. Existing report output paths are not overwritten. For machines without ReportLab/Korean TTF use --format xlsx.

The detail drawer displays the matching assessment ID and local command. The browser cannot mutate DB data.

For a real end-to-end synthetic check (all files go into a new disposable temporary directory):

    python smoke_local.py

The runner imports fixtures/sample_bids.csv and fixtures/sample_profile.json, tests XLSX and localhost HTTP list/detail/favorites/profile, re-exports a saved report, applies a versioned profile revision with a backup, re-assesses, and verifies the old assessment and backup. It does not use customer data, official APIs, external services or PDFs.

Full Python regression:

    python -m unittest discover -s tests -v

Current GitHub test inventory should include 116 prior methods plus 6 report re-export and 1 synthetic smoke = 123. **These 123 have not yet been run in an authenticated full checkout**. The new source/tests are committed but runtime and Windows/native browser and PDF validation remain pending.

## P2-06 failure recovery and first-use onboarding

Saved report replay is now more conservative on output failure:
- The XLSX writer cleans up a newly created partial archive if ZIP/XML writing fails, while never unlinking an already existing report.
- If the PDF renderer fails after a completed XLSX in a `--format both` replay, the completed sibling XLSX is removed; the PDF writer separately cleans up its own partial output. This is best-effort cleanup, not a general two-file atomic transaction against power loss or abnormal process death.
- Added tests for interrupted second worksheet, second-format failure and pre-existing PDF preservation. These tests are committed but the full checkout has not been run.

The BASIC interface now supports "새 회사 프로필 만들기" (download validated JSON) and existing profile editing. Both lead to a local CLI command; database writes require explicit `--create --apply --backup` and preflight. The browser itself remains read-only toward SQLite.

Windows 11 authorized private checkout verification from backend:

    powershell -ExecutionPolicy Bypass -File .\verify_local.ps1

This runs the full unittest suite, then the synthetic local end-to-end test and optional Node syntax validation. It prints a completion notice only after invoked checks return successful exit codes; it does NOT check native Excel/PDF appearance or live government bids. PowerShell script has been committed, not executed on Windows in this session.

Current GitHub source declares **126 Python test methods** in eight test files, confirmed by reading code. Do not call that 126 passing tests until `verify_local.ps1` or `python -m unittest discover -s tests -v` actually completes against an authenticated checkout. No new app deployment or GitHub main changes.


## P2-07 direct local Excel download (source implemented)

With `python viewer.py --db ./demo.sqlite3 --port 8765` running on 127.0.0.1, open a previously assessed bid's details. The "Excel (.xlsx) 직접 다운로드" link now calls:

    GET http://127.0.0.1:8765/api/report?assessment_id=1

This is a **read-only** path: it accepts only a positive, bounded persisted assessment ID, opens the local DB in `mode=ro` with `PRAGMA query_only=ON`, reconstructs the immutable original version/evidence, writes the generated XLSX only into a self-cleaning temporary directory, then responds with XLSX binary and a fixed Content-Disposition attachment filename. The response has `Cache-Control: no-store`, `nosniff` and existing localhost Host/Origin checks. When Fetch Metadata is present, explicit cross-site requests are refused; browser same-origin downloads work through a normal link. Maximum generated file size is 16 MiB. No arbitrary download directory path or file upload is accepted from HTTP, and no permanent report is created by this new route.

PDF still uses the existing explicit CLI `report_existing.py --format pdf`, because its local ReportLab/Korean-font dependency and browser handling have not been validated. The detail drawer retains that CLI example.

New regression methods in `tests/test_report_existing.py` test actual synthesized XLSX byte signatures, ZIP contents, DB read-only enforcement, localhost HTTP attachment headers, nonexistent IDs, invalid parameters and cross-site/host rejection. `smoke_local.py` now exercises HTTP attachment bytes too. All source/tests are committed but full Python execution in an exact private checkout is still pending. Do not call the number of declared test definitions PASS.
