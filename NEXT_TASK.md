# BID OWL NEXT_TASK — Windows SQLite handle QA remediation (2026-10-27 KST)

Repository private `hibi89/Bid_Owl`; only write to `feature/bid-owl-v1-basic-mvp`. On ㄱ inspect actual main/feature HEAD and HANDOFF.md, STATUS.md, AGENTS.md, REQUIREMENTS.md and this file. No main/Vercel/deployment/paid API/customer data upload.

## Actual external test proof, first-ever current-branch execution
The user ran on Windows 11? (Windows PowerShell, CPython 3.11; actual OS edition **not confirmed**) in the downloaded source ZIP's `backend`:
`python -m pip install -r requirements.txt` -> ReportLab 4.5.1 installed.
`python qa_runner.py --benchmark` -> **Ran 137 Python tests in 7.237s; 0 assertion failures, 18 unittest ERROR, 0 skipped, 119 successful**; JavaScript syntax check PASS; synthetic_smoke SKIP and synthetic_benchmark SKIP by QA runner after unit failure. Local timestamped JSON in backend/qa_results recorded. ALL 18 errors are `PermissionError: [WinError 32]` from `TemporaryDirectory.cleanup` trying to remove an OPEN SQLITE file, not 18 independently demonstrated eligibility/rule errors. They clustered 5 profile workflow backups, 2 historical report reader tests, 1 synthetic end-to-end backup, 3 StoreTests (backup + foreign DB preflight), 7 ViewerTests. Do NOT claim full suite passed.

## This response/iteration's GitHub source fix, NOT yet retested on user's Windows
1. `backend/bidowl/store.py`: `backup_to` replaced `with sqlite3.connect(dest) as target:` with `with contextlib.closing(sqlite3.connect(dest)) as target:`. SQLite Connection's ordinary context manager commits/rolls back transactions but **DOES NOT CLOSE THE CONNECTION**. A lingering backup destination connection prevented Windows deleting temporary backups.
2. `backend/tests/test_viewer.py`: seven `with open_database(self.path) as conn` blocks replaced with `with closing(open_database(self.path)) as conn`. This is intentionally a *test* fix (application server already uses `closing`). Preserve `query_only` semantics and no DB writes.
3. `backend/tests/test_report_existing.py`: same closing fix in two read-only connection test blocks.
4. `backend/tests/test_store.py`: four `with sqlite3.connect(future) as db` contexts replaced by `with closing(sqlite3.connect(future)) as db, db:` so original commit/rollback semantics are preserved and handles close before Windows cleanup. New targeted test `test_backup_destination_handle_released_before_return` creates a synthetic backup, reads/validates integrity, then explicitly unlinks it immediately; designed to fail on Windows if the backup handle remains open.
5. `backend/qa_runner.py`: locally saved JSON now adds `failed_test_errors` showing each unittest's last exception summary (up to 600 chars), so full 500-line console paste should not be required next time. JSON stays only on customer's PC and `qa_results/` is git-ignored.
6. Authenticated GitHub static inspection found **138 declared test methods** across 10 files (benchmark3, eligibility27, importer21, profile_workflow12, qa_runner3, report21, report_existing10, smoke1, store30, viewer10). Not 138 PASS. No current Python full-suite execution by authoring environment.

## User action NEXT (must be a NEW downloaded ZIP, not old)
Download a fresh private feature-branch Code > Download ZIP from https://github.com/hibi89/Bid_Owl/tree/feature/bid-owl-v1-basic-mvp, extract and open PowerShell inside its `backend`, then:
`python qa_runner.py --benchmark`
ReportLab previously installed in CPython 3.11; no need to rerun pip unless interpreter changes. Provide the new `backend/qa_results/bidowl_qa_*.json` (latest file) or whole output. Do not need to share customer database, API key, fonts, external service data.
If actual 138-run result PASS and smoke and 10k measurement PASS, record measured elapsed/timings and compare Git HEAD. ZIP `git_commit` might be null, **do not falsely call it wrong checkout**: use downloaded branch/ZIP name and version of this file. If errors remain, inspect `failed_test_errors` and patch exact failing code then repeat. If Node missing, JS syntax stage SKIP not PASS.

## Next after QA pass
Native Windows 11 Edge/Chrome one-click XLSX, Korean ReportLab PDF, 7 themes/mobile/keyboard; 10k performance from measured JSON, then BASIC first-use import/company edit workflow and Windows packaging/security. P3 official procurement user-key API and P4 AI opt-in only after BASIC. P5 installer and P6 KIPRIS/sales. Basic currently CLI-assisted and NOT ready to sell. Previous all-tier overall completion estimate ~35% was subjective; don't claim an objective increase from test remediation alone.
