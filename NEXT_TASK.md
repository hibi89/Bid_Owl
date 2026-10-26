# BID OWL NEXT_TASK — P2-08, 2026-10-27 KST

## Resume
Repo private hibi89/Bid_Owl, work only `feature/bid-owl-v1-basic-mvp`. On user ㄱ fetch main/feature HEAD, then read HANDOFF, STATUS, AGENTS, REQUIREMENTS and this file, inspect actual code. No production/legacy Vercel/main changes or paid/external data operations.

## Existing source (P1–P2-07)
P1 strict CSV and source-backed PASS/FAIL/UNKNOWN, revisioned SQLite with backups, CLI PDF/XLSX. P2-01 read-only localhost UI and 7 themes; P2-02 global favorites; P2-03 browser JSON company form + CLI preview/backup/apply/reassess; P2-04 profile CAS/write transaction and single-key detail; P2-05 immutable historical reports and disposable synthetic smoke; P2-06 output-failure cleanup, new profile onboarding and Windows `verify_local.ps1`; P2-07 GET /api/report by saved ID yields XLSX from read-only SQLite, with temporary files, attachment, bounded request and same-origin controls, one-click UI link.

## P2-08 implementation (committed, runtime not verified)
1. `backend/viewer.py`: previously `_arg()` rejected all filters over 160 chars even though source_id/bid_no/profile_id are valid up to 300. Set individual max_length=300 for source_id, bid_no and profile. Raised capped GET request-target from 1024 to 12288 characters because valid Korean 220–300-character IDs become several KB after percent encoding. Retain max 12 query fields, 300-character semantic limits, 414 on excessive target, same-origin/loopback restrictions.
2. `backend/bidowl/store.py`: `assess_and_record(..., expected_profile_version=N)` optional guard inside BEGIN IMMEDIATE checks latest profile revision before any assessment INSERT. Default None retains original CLI compatibility. This prevents an ongoing batch from silently saving judgments against another process's newly changed company profile.
3. `backend/profile_workflow.py`: reassessment pins `summary["planned_version"]` on each assessment; records `profile_committed` and only emits CONFLICT_NO_WRITE if THIS workflow actually saved neither a profile nor an assessment. If profile was committed then a race occurs, report PARTIAL_WRITE with backup path, even for 0 successful assessments; no deceptive all-or-nothing claim.
4. New one-method synthetic regressions in `tests/test_store.py`, `tests/test_profile_workflow.py`, `tests/test_viewer.py`. Viewer test uses 220-character Korean IDs and true localhost GET (percent encoded), checks permitted requests and 414 on excessive URLs. Test SQLite writer explicitly commits and closes for Windows.
5. Exact GitHub latest JS parsed by V8 Function constructor PASS (no UI changes this step). Static source checks confirm version guard occurs before INSERT. No actual Python full-suite execution, browser DOM run, Windows/Excel/PDF validation.
6. **131 declared unique Python test functions** across 8 files: eligibility27, importer21, profile_workflow12, report21, report_existing10, smoke_local1, store29, viewer10. This is a definition inventory, **NOT 131 PASS**. Last actual P1 baseline 96 PASS on 2026-10-26; does not validate current branch. No existing GitHub Actions workflow runs on feature branch at time of check; do not create paid CI runner without approval.

## NEXT P2-09 — unblock measured quality before feature expansion
- Obtain authorized full private checkout in a real Python-capable environment. Run from `backend`:
  `python -m unittest discover -s tests -v`
  `python smoke_local.py`
  `node --check ui/ui.js`
  Windows local shortcut: `powershell -ExecutionPolicy Bypass -File .\verify_local.ps1`.
  Record real PASS/FAIL/skip and fix failures; this is the highest remaining release blocker. Python sandbox earlier could not resolve private git clone, signed raw.githubusercontent.com or api.github.com and contains only older partial stand-in; don't repeat identical network attempts or call stand-in tests current.
- Synthetic end-to-end verify backup/immutable history and profile change during reassessment. Test GET /api/detail for 220-char Korean triple keys, GET /api/report binary on loopback, download file and no DB writes; confirm oversized requests fail.
- Windows 11 real Edge/Chrome: 7 themes/mobile/focus, profile Blob JSON export and explicit CLI apply, XLSX direct download/native Excel, ReportLab PDF with installed/licensed Korean TTF. Benchmark 10k-bid dataset and tune indexes only after measuring.
- BASIC import/profile mutation and PDF remain CLI-assisted, so not yet a finished one-click paid product. No mutable HTTP endpoint without CSRF/auth, backups and explicit user approval. P3 official procurement API, P4 opt-in AI, P5 Windows packaging/security, P6 trademark/KIPRIS/sales gate later.

## Privacy and stop
No customer DB/CSV/documents/reports/font/API keys/.env in GitHub, no external services/fees and no main/Vercel changes. Historic 340/340 school demo is unrelated to BID OWL product QA. New source committed; current SHA verified after HANDOFF update. 
