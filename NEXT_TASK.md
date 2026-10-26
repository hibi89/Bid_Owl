# BID OWL NEXT — P2-13 disposable local BASIC demo shipped to feature branch, 2026-10-27 KST

User says ㄱ = read current GitHub feature + main heads and START_HERE, AGENTS, STATUS, HANDOFF, REQUIREMENTS, NEXT_TASK, then implement next step without asking user to download/test ZIP. User previously objected to routine manual QA; no extra user actions here. Never modify main, legacy Vercel, private user data, paid tools, external API or distribute private source without approval.

## P2-13 implementation already committed
- NEW root `START_BID_OWL_DEMO.cmd`, `backend/START_DEMO.cmd`: Windows double-click entry from ZIP root, invokes local `py -3` or `python` without ReportLab install requirement, keeps failure message visible.
- NEW `backend/demo_local.py`: Python 3.11+ stdlib + local bidowl; takes **packaged fake CSV/profile only**, explicitly checks all `source_ref=DEMO_ONLY`, bid number prefix `DEMO-` and company ID `SYNTHETIC-` before DB creation, refuses any existing target file. Creates a fresh SQLite in `TemporaryDirectory(prefix='bidowl-synthetic-demo-')`, imports two fake bids, records rule assessments for fake profile, serves existing read-only `viewer.make_server` at 127.0.0.1 random port by default, opens default browser (optional `--no-browser`, explicit `--port`). Ctrl+C releases server and temp directory. No default customer DB path, no external network, no API keys, no ReportLab/font. Abnormal termination can leave OS temp data; do not overclaim deletion guarantee.
- Modified `backend/ui/index.html`, `backend/ui/ui.js`, `backend/ui/ui.css`: visually distinguish synthetic data via persistent-in-session, accessible warning banner when source ID `BIDOWL_SYNTHETIC_DEMO` appears in local bids; styling uses existing 7-theme CSS variables. No HTML interpolation or new API write route.
- NEW `backend/tests/test_demo_local.py`: **8 test methods** covering synthetic 2-bid DB, existing user file untouched, fake/changed fixture rejection, local-only readonly HTTP, teardown after synthetic server exits, invalid port, UI warning and root+backend Windows launchers.
- NEW `backend/DEMO.md`: launch, provenance, safety/termination and validation limitations.
- Updated root README.md (legacy BID INSIGHT warning), backend README.md (demo quickstart), START_HERE.md (latest stage), STATUS/HANDOFF/NEXT_TASK.
- Source-level verification: exact remote new JS parses successfully using V8 Function (syntax-only PASS), GitHub fetched demo files and verified fixture-path/test/warning/loopback guards. **No real Windows double-click, no full Python suite or demo-server runtime executed on authentic private checkout by assistant.** Historical user Windows test 137 cases, 18 WinError 32 (earlier branch), JS PASS; P2-11 fixed handles but current tests still need measured run.
- Declared Python test methods **152** in 12 test files after +8. This is not 152 PASS.

## NEXT P2-14 autonomous work
1. Improve BASIC first-run flow beyond disposable demo: safe, explicit *real* CSV import + profile capture and backup semantics, reducing current CLI friction WITHOUT exposing writable HTTP endpoints to drive-by requests. Consider a single offline CLI wizard or separate deliberate local one-click importer with preflight JSON validation, restricted local path, source IDs and back up before edits. Never mix fake demo DB with real customer storage.
2. Add integration/unit tests for all new flows and Windows handle lifetime, preserve PASS/FAIL/UNKNOWN unknown-first and snapshot evidence, no mandatory cloud. Source-level V8 syntax/statics where runtime checkout unavailable; no fabricated QA.
3. Only after BASIC usability, tackle Windows packaging, real Excel/PDF, 10k performance and final native QA as release gates. P3 PRO official procurement customer key API, P4 PREMIUM opt-in AI, naming/KIPRIS checks and commercial sale are later.
All-tier subjective progress prior approx 35%, do not increase numerically without objective evaluation.

---
## Earlier P2-12 and P2-11 notes retained for context

# BID OWL NEXT — P2-12 autonomous Windows-lock prevention / diagnostic consolidation (2026-10-27 KST)

**Continue on `feature/bid-owl-v1-basic-mvp` only; no user action required for ordinary code tasks.** User has explicitly objected to repeatedly downloading ZIPs and rerunning scripts. Do not request another user-side test in routine ㄱ work; do as much source implementation/static validation as possible independently, and leave native Windows test as an honest release-gate limitation. No paid hosted CI/cloud runner or private-code transfer to third-party project without approval; main and Vercel protected.

**Current changes actually committed:**
- `backend/tests/test_sqlite_handles.py` (4 new tests) uses Python stdlib AST to reject bare `with sqlite3.connect(...)` / `with open_database(...)` across the entire backend and fixtures that detect known-bad patterns. Does NOT claim to find every possible connection leak. The 3 self-contained AST behavior cases passed in the author's Python sandbox; full-repository scan needs authenticated full checkout.
- `backend/bidowl/store.py` P2-11 `backup_to` explicitly closes its target; P2-12 `backend/tests/test_store.py` adds **platform-independent** close proof with `unittest.mock.patch` tracing sqlite3.connect, then asserts the observed connection raises `sqlite3.ProgrammingError` after backup. Minimal synthetic connection-spy proof executed and passed on local Python, not whole product test.
- `backend/qa_runner.py` executes separate synthetic smoke and opt-in 10k benchmark even if one earlier test stage failed. This avoids requiring a complete repeat just to collect independent diagnostics. Overall PASS remains impossible if any invoked mandatory stage FAIL. `backend/tests/test_qa_runner.py` updates failure semantics and adds a distinct smoke-failure-but-benchmark-runs regression; benchmark stays opt-in.
- `backend/BENCHMARK.md` evidence narrative updated. Latest live GitHub source inventory: **144 declared Python test methods in 11 test files**, NOT 144 PASS. Detailed prior count 137 actual Windows test run: 119 successful, 18 WinError32 temporary SQLite handle cleanup errors, 0 assertion failures, JS PASS, smoke and 10k benchmark SKIPPED on that older run.
- Inspected the exact current GitHub source across 25 Python files: no line-beginning direct `with sqlite3.connect(...)`, `with open_database(...)` violations observed. This is a lightweight static pattern scan, not complete AST nor CPython execution.

**Next work P2-13 WITHOUT bothering user:** review release blocking BASIC first-use friction and safely implement an isolated local synthetic demo/one-click launcher or other essential local usability task on feature branch; add unit/static tests, preserve readonly browser/mandatory mutation backups, keep no-customer-data/no-cloud. Or advance additional source-level safety regressions. Do not claim Windows 144/144 runtime PASS or 10k timings without authentic results. A future Windows acceptance gate exists but is not the user's routine responsibility.

## Prior historical P2-11 notes follow (preserved for traceability)

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
