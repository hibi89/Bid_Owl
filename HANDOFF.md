# BID OWL HANDOFF — P2-12 autonomous source hardening (2026-10-27 KST)

## 1. User intent and current product
Private BID OWL Windows-local procurement screening: BASIC CSV/profile/versioned SQLite + conservative evidence based PASS/FAIL/UNKNOWN + readonly localhost UI/seven themes + saved XLSX/PDF; PRO official Korean procurement API via user's own key, PREMIUM opt-in AI, planned 59k/149k/299k KRW, unverified prices/trademark. The user **explicitly does not want repeated manual test requests**. Continue own source development on feature branch. Final native Windows acceptance is a distinct release gate, not routine user labor.

## 2. P2-12 changes (this turn)
- New `backend/tests/test_sqlite_handles.py` (4 tests) AST-scans backend app and test Python source, rejecting direct `with sqlite3.connect(...)` / `with open_database(...)` because sqlite3 Connection.__exit__ is transaction-only and does NOT close file handles. Includes 3 synthetic positive/negative AST scanner cases; no customer data/DB. Does not detect aliases or all possible lifetime leaks.
- `backend/tests/test_store.py` +1 deterministic cross-platform test wraps `bidowl.store.sqlite3.connect` with side-effect tracer during `backup_to`, then asserts tracked target is already closed after return (sqlite3.ProgrammingError). Complements P2-11 Windows-only backup unlink regression; minimal standalone connection-spy proof PASS in local Python. No production backup logic changed in P2-12.
- `backend/qa_runner.py` now runs the isolated synthetic smoke and opt-in 10k synthetic benchmark independently even if unit tests have errors; still reports overall FAIL unless all mandatory invoked stages PASS, Node missing still SKIP. Prevents unneeded repeat downloads/commands just to gather additional independent diagnostics. `backend/tests/test_qa_runner.py` updated prior fail-gating test and adds 1 explicit isolated smoke-fails-but-benchmark-runs test.
- `backend/BENCHMARK.md` recorded new semantics and previous first measured Windows failure evidence; `NEXT_TASK.md`, `STATUS.md`, `HANDOFF.md` updated.

## 3. Actual source and test evidence / limitations
Remote authenticated GitHub inspection of exact 25 Python backend files found **0 direct bare SQLite `with` patterns** after P2-11 closure fix (static line-pattern scan, does not execute AST across exact authenticated repo in local CPython). Standalone copy of the new AST scanner executed 3 behavioral unit tests PASS under the author's Python environment; fourth full-repo scan could NOT run locally without authenticated full checkout. Standalone synthetic tracer demonstrated how to detect a closed SQLite handle by `sqlite3.ProgrammingError`. These do **NOT** constitute full project integrated QA.
Current authenticated source contains **144 declared Python test_* methods in 11 files**. **144 not executed**. Historical user Windows ZIP run on preceding version actually executed 137 tests in 7.237 seconds: 119 successful, 18 ERROR WinError32 deletion of still-open temporary SQLite files, zero assertion failures; JavaScript syntax PASS, then synthetic smoke and 10k benchmark SKIP under previous failure-gated QA semantics. P2-11 fixed observed open connections but new code is not yet measured on Windows. P1 old 96 Linux PASS on earlier branch is not current QA. Do not fabricate Windows success/10k timing.
Current running environment sandbox cannot fetch and mount entire authenticated private repo (earlier DNS/auth failures); GitHub connector reads/writes files but not Python execution checkout. No main/production/customer changes.

## 4. Next iteration without user work
P2-13: improve BASIC first-use usability or add more offline/local source safety tests; prioritize actual user-facing workflow after Windows handle leak fixes. Keep 127.0.0.1 app read-only and data modifications only through explicit CLI with backups and expected revisions, unless approved secure authentication/CSRF threat model. If a safe way to execute the authenticated full private suite from own authorized environment becomes available without paid external CI/private-code egress, use it and record real results. Do not automatically request the user to download another ZIP on ㄱ. Native Windows/browser/Excel/PDF real acceptance remains pending and must be reported honestly.

## 5. Repository, commits, backups, restrictions
Private https://github.com/hibi89/Bid_Owl repo id 1399359397, work branch `feature/bid-owl-v1-basic-mvp`. P2-12 begins at `dd4fbfa2966e277a23726916ff30491ae2458e69`. Source commits:
- `d4640f97eb4c7c61b0f7ab71828c3b9c106517dd` test_sqlite_handles.py 4 new;
- `098dc1596b023e54ceda800b1aa92def01b74a70` qa_runner independent stages;
- `8f0b6fbbc521f60c0ba4204d2319d6816dd51cff` qa-runner tests;
- `74b35dce7d44148c13ba4a5f9c148e6f9c2c0f33` cross-platform backup-close spy test;
- `8dffb415c91ef2c5e24b76d135102eb8ccb449be` benchmark docs;
- NEXT_TASK and STATUS updates follow; current HANDOFF update is last expected HEAD, verify SHA/author after write.
Main must remain `c888c795bef72734f3f7016e54013b82453f11d8` and old school demo/Vercel unchanged. No actual customer SQLite/CSV/PDF/XLSX/keys/secret/fonts uploaded; no GitHub public action/paid services/external API/permission change; backup always non-overwriting before write. Old school demo 340/340 not BID OWL QA.

## 6. Production and environment
New Python BID OWL has no public deployment. Authenticated local developer after CSV import may run `python viewer.py --db ./demo.sqlite3 --port 8765` in backend and access http://127.0.0.1:8765; app HTTP is read-only. PDF uses ReportLab and locally installed permitted Korean font, one-click historical XLSX is read-only. Prior unrelated Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched. No verified Windows native browser/Excel/PDF or install yet.

## 7. Explicit QA logic and acceptance
`python qa_runner.py --benchmark` from an **actual current** authenticated checkout records real unittest results, separate synthetic smoke, optional Node syntax, requested 10k benchmark with timings, Git SHA when checkout exposes git (ZIP SHA may be null), and writes local ignored `qa_results` JSON. One failing stage can no longer suppress independent diagnostics; no stage failure is converted into success. This implementation has not been run end-to-end from exact source in this turn. Final commercial BASIC gates: Windows cleanup lock bug confirmed fixed by real runs, 10k measured acceptable, native Excel/PDF, accessibility and 7 themes, packaging, customer-data privacy, legal clearance.

## 8. Last checkpoint and continuation
2026-10-27 KST. Authenticated GitHub source updated and static checks performed; latest current full run unverified. No further user action requested. User ㄱ resumes P2-13 autonomous work. The more detailed historical P2-11 handoff follows for earlier errors, exact Windows console result and rationale.

---

# BID OWL HANDOFF — P2-11 Windows SQLite handle fix, 2026-10-27 KST

## 1. Product and technical requirements
Private BID OWL/비드아울 Windows local-first tender screening. BASIC planned KRW 59,000 one-time: CSV validation, company profile, cited source-backed conservative PASS/FAIL/UNKNOWN and human review, versioned SQLite, search/favorites and seven themes, historical XLSX/PDF. PRO planned KRW 149,000 official Korean procurement API via user-issued key, on-PC sync; PREMIUM KRW 299,000 opt-in customer AI API and profitability. Pricing and trademark legally unverified, no legal bidding or award guarantee. Python 3.11+, SQLite v1, stdlib XLSX, ReportLab optional with licensed locally installed Korean TTF, localhost 127.0.0.1 UI with no mandatory cloud for BASIC.

## 2. Previously completed source and this turn's code changes
P1 strict CSV/schema/rules/evidence + persisted revisions and PDF/XLSX. P2-01 readonly localhost viewer 7 themes, P2-02 favorites, P2-03 profile editor JSON + backed-up CLI, P2-04 SQLite CAS/version safety, P2-05 saved historical report replay/synthetic smoke, P2-06 report output failure cleanup/new profile form, P2-07 one-click localhost XLSX, P2-08 long Korean ID & pinned profile version during reassess, P2-09 10k synthetic perf helper, P2-10 full-suite local JSON QA runner.
P2-11 **response to actual user's first Windows 137-test run**:
- `backend/bidowl/store.py` now imports `closing` and executes `with closing(sqlite3.connect(str(dest))) as target` inside backup_to. The old `with sqlite3.connect` SQLite context manager DOES NOT CLOSE connection, leaving backup destination file locked, manifesting as WinError 32 on Windows TemporaryDirectory cleanup. Existing exclusive backup output and integrity check unchanged; no customer backup overwritten.
- `backend/tests/test_viewer.py`: 7 `with open_database(self.path) as...` converted to `with closing(open_database(self.path)) as...`, preserving readonly query semantics, releasing file before temp cleanup.
- `backend/tests/test_report_existing.py`: 2 read-only direct SQLite context managers similarly wrapped with closing.
- `backend/tests/test_store.py`: 4 existing `with sqlite3.connect(future) as db` converted to `with closing(sqlite3.connect(future)) as db, db:` so transaction commit/rollback semantics stay intact before connection closes; +1 Windows backup destination handle-release test that immediately unlinks verified disposable backup file.
- `backend/qa_runner.py` adds per-error last exception summary `failed_test_errors` in local JSON to allow smaller uploads during future diagnostics; never automatically uploaded.
- NEXT_TASK.md, STATUS.md, HANDOFF.md updated.

## 3. ACTUAL Windows test outcome, and what is still unverified
User supplied real Windows PowerShell log from downloaded feature ZIP with Python 3.11, ReportLab 4.5.1 newly installed.
`python qa_runner.py --benchmark` -> `Ran 137 tests in 7.237s`, `FAILED (errors=18)`, zero assertion failures, zero skipped, JS check `PASS`; 18 errors are **ALL** PermissionError [WinError 32] deleting open SQLite files during TemporaryDirectory cleanup, spread profile_workflow5, report_existing2, smoke_local1, store3, viewer7. Synthetic smoke standalone and optional 10k benchmark were `SKIP` automatically because unit suite failed. This is the **first current-branch measured real test run**, not a simulation. 119 tests finished without reported failure/error, but 137 did **not** PASS.
After the GitHub patches above, 138 Python test methods now defined (benchmark3, eligibility27, importer21, profile_workflow12, QA runner3, report21, existing report10, smoke1, store30, viewer10). These new **138 have not been executed** in a current full checkout, so do NOT claim the 18 errors are fixed in runtime until user reruns. Checked remotely that source no longer has plain raw with-open_database or with-sqlite3.connect test contexts, backup destination now explicitly closed. A minimal standalone Python snippet verified `with closing(sqlite3.connect(...)) as db, db` commits and closes, but not full repo. Previous historical P1 96 PASS does not override actual full P2 failure.

## 4. Stage, completion estimate and stop
Source through P2-11 committed, but the release QA gate is OPEN pending rerun. Existing broad overall completion estimate ~35% subjective across BASIC+PRO+PREMIUM+installer; no objective increase asserted. BASIC not yet sellable because full tested Windows functionality, user-friendly import/profile/PDF and installer/security still pending. After this handoff commit, verify feature/main HEAD, commit owner hibi89; stop pending user rerun or next ㄱ.

## 5. Failures and blockers
Real fault is Windows SQLite file-handle lifetime: CPython sqlite3.Connection.__exit__ commits/rolls back but does NOT close. Tests and backup code incorrectly assumed otherwise. A common POSIX/Linux test run cannot expose this lock due Unix allowing deletion of open files. Prior private repo checkout into assistant container failed DNS/auth; GitHub connector can read/write files but no local checkout for actual entire Python suite. Earlier automated browser loopback blocked by sandbox ERR_BLOCKED_BY_ADMINISTRATOR. New patch is statically reviewed only; user Windows rerun mandatory. User's prior ZIP is immutable/stale and **cannot** test recent fixes. Future local JSON now saves last exception summary without requiring full 500-line log, and remains git-ignored.

## 6. Repository/branch/commits/paths and protected originals
Private https://github.com/hibi89/Bid_Owl repo ID 1399359397; branch feature/bid-owl-v1-basic-mvp, iteration start SHA f2f408299abdf4402abd83a7a07376ee9cbc47b7. Commits in this iteration include
`f1767b9de61c1e07dbadbc422022099b34a48823` backup handle closure,
`91c622fff90312786090db9ec78d893d53e9ff65` viewer test closure,
`9d458bb6dba7722dae7efc6c75d434e41985a806` report test closure,
`3275414d6d3c93eb5132ccd5e715ec9444d22e0d` store test closure,
`176fc596b0e6ff635e768f942efd368629aa5c2e` handle regression,
`7fe88933687d3be965e4110076a012de7dba89d1` local JSON error summary,
and docs updates. Main starting SHA c888c795bef72734f3f7016e54013b82453f11d8, untouched; legacy original rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Full list of modified files this iteration: backend/bidowl/store.py, backend/tests/test_viewer.py, backend/tests/test_report_existing.py, backend/tests/test_store.py, backend/qa_runner.py, NEXT_TASK.md, STATUS.md, HANDOFF.md. Recheck final SHA after this commit, author/committer hibi89.

## 7. Local running and production deployment
No new BID OWL public deployment. From authenticated checkout `backend`, run `python viewer.py --db ./demo.sqlite3 --port 8765`, open http://127.0.0.1:8765; only localhost, not uploaded or hosted. One-click saved XLSX GET /api/report?assessment_id=N uses mode=ro and no-store; PDF still explicit CLI via installed licensed Korean TTF and ReportLab. School demo's old Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched; production URL/live HTTP unverified. No deploy or user database exposure.

## 8. Privacy, backup and permissions
No customer SQLite/CSV/contract, fonts, PDF/XLSX, .env/API secrets or real procurement docs uploaded. Local QA JSON under backend/qa_results is ignored by Git; contains generic runtime, local paths and test errors but no deliberate secret dumps. The synthetic QA runner does not transmit anything. Existing profile apply requires explicit backup and expected profile version; all reports snapshot-preserving, backup refuses overwrite. No user approval for paid external API, public sales, company data transmission, main/Vercel edits. Brand KIPRIS trademark check pending; planned prices not validated.

## 9. NEXT — user's minimal action and acceptance criteria
Have user DOWNLOAD A FRESH ZIP of development branch (GitHub Code > Download ZIP), extract to a new folder, PowerShell `cd backend` in this NEW source, run `python qa_runner.py --benchmark`. ReportLab 4.5.1 already installed on their same Python 3.11 unless changed; no need to pip install again.
Attach latest `backend/qa_results/bidowl_qa_*.json` or console output. Compare actual count (138 expected), failures/errors/skip, smoke status, JavaScript check, benchmark status with real timings; if all PASS, record actual Windows results and move to native browser/Excel/PDF. If FAIL, use JSON `failed_test_errors` to repair exact remaining cases. Note user downloaded GitHub ZIP, so Git sha might be null in QA JSON; do not mistake that for an outdated source as long as new ZIP provenance confirmed.
After full QA pass, test seven themes, mobile/keyboard/Edge, native XLSX and Korean PDF, actual 10k UI speed, data backup/restore and Windows packaging. Then PRO official procurement API with customer's key, PREMIUM AI opt-in, name/legal sales checks.

## 10. Updated timestamp/continuation
2026-10-27 KST. Important distinction: **137-run Windows 18-error actual measured**; **138 newly defined but not rerun**. Next user ㄱ or rerun JSON continues focused P2-12 fix/validation. Never claim 138/138 PASS until genuine Windows output proves it.
