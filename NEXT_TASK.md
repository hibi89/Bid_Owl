# BID OWL NEXT — P2-18 strict SQLite DB identity/open boundary (2026-10-27 KST)

**Next ㄱ resumes P2-19 automatically.** User directs autonomous work without repeating ZIP/PowerShell test requests. Private `hibi89/Bid_Owl`, work only on `feature/bid-owl-v1-basic-mvp`. Protect main/Vercel, never make customer files public, no paid CI or API services without approval. Read current heads, START_HERE.md, AGENTS.md, REQUIREMENTS.md, STATUS/HANDOFF, then proceed.

## P2-18 source changes completed
- `backend/bidowl/store.py`: backward-compatible `BidOwlStore(..., must_exist=False, expected_identity=None)`. Strict mode `must_exist=True` opens SQLite with **URI mode=rw, no auto-create**, refuses absent, empty, foreign or unsupported DB. `database_file_identity(path)` captures st_dev/st_ino/st_size/st_mtime_ns; caller can pass `expected_identity`, checked both before and after connecting. For intentionally fresh O_EXCL-reserved blank DB, pass expected_identity but must_exist=False: mode=rw opens the already reserved new file and explicitly initializes its schema, while refusing a changed/newly missing file. Default legacy constructor still permits creating new DB for synthetic/unit compatibility.
- `backend/import_local.py`: `ImportPlan.db_identity` stores readonly preview identity for existing DBs; compares identity again before+after apply preflight; opens existing with must_exist=True and expected_identity, fresh reserved file with expected_identity. No silent new DB creation when preflighted existing DB disappears. Rejects swapped same-path valid database before backing up or mutating.
- `backend/cli.py`: snapshot identity before readonly preflight; reject missing/swapped existing path, reserve new via `xb`, pass expected identity and existing flag to strict store. Previous P2-17 backup-first/engine policy unchanged.
- `backend/profile_workflow.py`: apply snapshots existing file identity, read-only validates, rejects change, and opens strict existing writer with same identity. Preview still readonly.
- New synthetic test definitions: `test_store.py` +6 (missing/empty/schema, matching file, swapped valid DB, deleted between stat and connect, deliberately reserved new file), `test_import_local.py` +3 (preview→apply swap, deleted on writer, swapped on writer), `test_cli_safe.py` +2 (CLI writer deletion and swap after readonly validation), `test_profile_workflow.py` +2 (same scenarios for company profile). **+13 tests: 212 defined in 15 files**, not 212 runtime PASS.
- `backend/DB_FILE_SAFETY.md` documents semantics and limitations; update README, STATUS/HANDOFF/START_HERE.
- Independent real Python sqlite3 stdlib temporary-file contract: **4/4 PASS** (URI mode=rw never creates missing db, file stays absent, empty SQLite is schema-version 0, os.replace alters observed file identity). These are not full GitHub tests or native Windows tests.

## Known remaining risk and P2-19
- This is *best-effort* TOCTOU conflict detection, NOT a filesystem-level lock or cross-process serializability. File inode reuse, concurrent writes after validation, SQLite WAL and Windows OneDrive/network behavior need real tests; no claim of absolute prevention or production hardening.
- NEXT P2-19: materially improve customer backup recovery / guided snapshot restore with explicit safety and no automatic overwrite, then tackle commercial BASIC Windows installer & actual end-to-end QA, report/Excel/PDF outputs and 10k synthetic benchmark in an approved non-paid authorized environment. No routine user testing. PRO customer-key procurement API and PREMIUM AI remain unimplemented.
- Feature branch started P2-18 at `dd6536cd9be340e503deb92e030405b8c9ab9d0e`, main baseline `c888c795bef72734f3f7016e54013b82453f11d8`. After docs fetch final feature HEAD/main SHA and compare changes; DO NOT guess SHA.
- Previous all-tier subjective estimate 42%; don't artificially increase without objective release evidence.

---
## Earlier NEXT_TASK history

# BID OWL NEXT — P2-17 legacy CLI prewrite safety implementation (2026-10-27 KST)

**Next ㄱ => P2-18 autonomous.** User expects direct GitHub work, no routine ZIP download or PowerShell testing from user. Keep `main` and prior Vercel untouched; only `feature/bid-owl-v1-basic-mvp`. Do not use paid private GitHub CI, public deploy, customer data, or API keys without approval. Inspect actual latest refs and START_HERE, AGENTS, REQUIREMENTS, HANDOFF, STATUS before acting.

## P2-17 source changes
- `backend/cli.py` (historical CLI CSV -> assessments -> XLSX/PDF) used to mutate an existing SQLite database without backup and update same-ID company profiles without CAS. Now executes preflight checks on selected CSV, validated company JSON (existing `profile_workflow.load_profile_file`), source ID, PDF environment before DB writes. For an existing DB, uses `viewer.open_database` in **read-only mode** for schema/profile preflight and refuses an existing company ID with changed contents. After opening the writer it creates an exclusive, consistent `BidOwlStore.backup_to(_new_backup_path)` before any DB/provenance/import/profile writes. Rechecks profile/version after backup and never silently edits existing profile; brand-new profile created with `expected_version=0`. Legacy v1 missing `assessment_engine_provenance` is migrated with additive table **only after backup**, and all new assessments record current engine hash in a single transaction (via existing store). Assessment uses `expected_profile_version` CAS. New DB uses `open('xb')` against path appearance race. Report writes remain XLSX/PDF and legacy synthetic sample CSV compatibility maintained; this is a distinct workflow from real customer GUI importer `import_local.py` which prohibits demo provenance.
- Existing DB backup location returned as `backup` in JSON. If report failure occurs after DB writes, report `CLI_PARTIAL_OR_UNCERTAIN`, preserve backup and tell caller to inspect DB and report files instead of implying rollback. `cli.main` catches sqlite3.Error into local machine-readable FAILED JSON instead of an uncaught traceback. No new HTTP write endpoints.
- Added `backend/tests/test_cli_safe.py` with **9 declarative synthetic tests**: new assessment provenance, repeat backup state, legacy v1 migration only after backup, existing company mismatch refusal, failed backup no further write, report writer partial-failure warning + preserved backup, foreign non-SQLite file unchanged, concurrent new-file path guard, local JSON SQLite error output.
- Updated `backend/README.md`, `backend/ENGINE_POLICY.md`, NEXT_TASK.md, STATUS.md, HANDOFF.md and START_HERE.md.

## Verification boundary
Live private GitHub authenticated readback found readonly preflight + backup-before-writes + pinned profile version + provenance DDL + exclusive new file guard in actual source; nine additional tests *defined*. Total **199 Python test functions across 15 files**, NOT run as current full suite in assistant. Historical user Windows P2-10 ran 137 tests and hit 18 WinError 32; subsequent repairs remain unverified on Windows. GitHub workflow history for this feature branch showed 0 runs, so no automated hosted PASS. Do not claim Python current PASS, native Windows, complete backup/restore, PDF font, 10k benchmark, or sale readiness. Prior overall BASIC+PRO+PREMIUM/install estimate about 40% subjective, not recalculated.

## Next P2-18 priority
- Harden existing DB open/create race in `BidOwlStore` (opt-in require-existing SQLite mode=rw + no implicit blank DB initialization); legacy CLI and real importer should use it on existing paths to guarantee no silently recreated DB after preview. Add safe synthetic tests. If no safe and backward-compatible path, make other BASIC workflow improvements.
- Improve first-use saved report export/backups, data migration and real onboarding, with accurate regression QA.
- Eventually run authentic native Windows full suite, browser Excel/PDF + locale/fonts + 10k timings. Do not send routine manual commands to user on ㄱ. PRO official customer-key data API/PREMIUM AI, installer, trademark + paid sales are later and not verified.

---
## Prior task history

# BID OWL NEXT — P2-16 engine fingerprint auto-invalidation complete in source (2026-10-27 KST)

**Next ㄱ => P2-17 autonomous.** User explicitly does NOT want repeated ZIP downloads and manual PowerShell tests. Work directly in connected private GitHub `hibi89/Bid_Owl` feature/bid-owl-v1-basic-mvp, preserve main + legacy Vercel, no paid runner/customer data/API keys. Read START_HERE/HANDOFF/STATUS/AGENTS/REQUIREMENTS first and verify latest feature/main heads.

P2-16 code:
- `backend/bidowl/engine_identity.py`: deterministic SHA-256 fingerprint over local eligibility.py, schema.py, profile.py, store.py (source behavior and storage logic). Missing policy source fails closed for new writes; viewer displays UNKNOWN.
- `backend/bidowl/store.py`: fresh v1 DB gets additive `assessment_engine_provenance(assessment_id,engine_hash)` without changing PRAGMA user_version=1; new assessment and corresponding fingerprint recorded in SAME SQLite write transaction, rollback on provenance insert failure. Legacy v1 DB opening never silently creates provenance.
- `backend/import_local.py`: existing v1 DB gets provenance table only AFTER consistent non-overwriting SQLite backup; snapshots without hash or with different hash are NOT reused. Automatic re-assessment, plus P2-15 bid/profile version and deadline tests still apply, CLI `--force-reassess` remains available as optional override. New stored current hashes only, never retroactively label old PASS as current.
- `backend/profile_workflow.py`: company profile `--apply` upgrades legacy provenance metadata only AFTER mandatory backup and records hashes on new reassessments. Legacy CLI paths without upgrade retain unproven snapshots.
- `backend/viewer.py`: readonly SQL shows historical `snapshot_status` but current `status=UNKNOWN`, `requires_human_review=true` on old/missing/stale engine hash. No database mutation from browser, source files absent => UNKNOWN, not PASS; also guard against **both absent fingerprint values appearing equal (NULL/None)**.
- Tests: +12 declarations: test_engine_identity.py 3, test_import_local.py +2, test_viewer.py +4, test_store.py +2, test_profile_workflow.py +1. GitHub live source inventory = **190 test methods / 14 modules**, NOT 190 PASS. Isolated SQLite grammar for viewer legacy v1, viewer provenance join, reuse query **3/3 PASSED** using in-memory synthetic DB; does NOT execute whole project. Full private repo Python suite and native Windows acceptance still not run by assistant. Prior real Windows 137-test run had 18 WinError32 errors before P2-11 remediation; no measured confirmation since.
- Docs: backend/ENGINE_POLICY.md and backend/IMPORT.md explain fail-closed behavior, additive migration and packaging/source resource limitation. No payment or sensitive data involved.

P2-17 next: (1) review legacy `cli.py` writer and optional schema-provenance upgrade after secure backup so all application entrypoints can emit fresh engine hashes, or improve BASIC guided report export/backup-restore, (2) prove native Windows 190-suite+loopback/UI+Excel/PDF, (3) packaging source resources for fingerprint (PyInstaller/EXE source files missing must fail-closed, do not claim packaged). Actual tested speed and sale-readiness still open. Previously re-estimated overall subjective approx **40%**; do not arbitrarily increase without milestone evidence.

---
## Prior task history

# BID OWL NEXT — P2-15 implemented; P2-16 autonomous (2026-10-27 KST)

Resume rule: user `ㄱ` = continue most important feasible source task on `feature/bid-owl-v1-basic-mvp`, no routine request to download ZIP or rerun tests on their PC. Auth GitHub heads, HANDOFF.md, STATUS.md, AGENTS.md, REQUIREMENTS.md, START_HERE.md and this file must be read first. Main and legacy Vercel protected; no public service, private customer data upload, paid runner, customer API/AI keys without approval.

P2-15 source changes:
- `backend/import_local.py` now avoids duplicate SQLite assessment rows on unchanged repeat CSV import: exact source/bid/profile, saved bid_revision==latest_revision, saved profile_version==latest profile revision, and recorded expiry flag==current expiry. If any mismatch, evaluate and save new immutable snapshot, ensuring deadline crossing forces reevaluation. Profile drift during reused lookup is rejected. Uses parameter-bound SQL. Existing backup before any DB modification remains mandatory.
- `apply_import(plan, force_reassess=False)`: new `assessments_saved` (new only) and `assessments_reused`, counts cover all processed bids. GUI displays both counts and has user-selected re-evaluate checkbox. CLI explicit `--force-reassess` with `--apply` for known rule-engine changes, preserving historical snapshots. **Known limitation:** rules-engine source changes not auto-detected, so manual full reevaluation needed after app upgrade; build safe automatic invalidation in P2-16.
- `backend/tests/test_import_local.py` new +8 (total 26) scenarios including unchanged SQL identity, revised bid, expiry transition, company profile revision, concurrent mid-import company version drift + backup preserved, forced reassessment (CLI & direct), and invalid option type.
- `backend/IMPORT.md` updated with reuse and override behavior. `STATUS/HANDOFF/NEXT_TASK/START_HERE` updated.
- **Verification:** source readback and static guard checks; four small isolated SQLite SQL contract checks actually passed in Python sandbox (not full GitHub import run). Current GitHub **178 Python test_* declarations across 13 modules**, not 178 execution PASS. Old actual 137-test Windows run had 18 WinError32 errors, no new full Windows confirmation of fixes.

P2-16 implementation priorities:
1. Engine-code version/fingerprint invalidation: track which eligibility policy/logic version produced a reusable assessment. MUST not mutate existing SQLite v1 before taking required backup; existing snapshots without engine provenance must be reevaluated. Do not silently treat code-upgrade old PASS as current. Add tests for old-version and current-version cache states.
2. Backup/recovery user-facing support: verify SQLite backup read-only and create safe opt-in restore plan with explicit backup of current DB before any swap, no automatic replacement without dedicated confirmation; or report launcher to reduce BASIC CLI friction.
3. Full native Windows release validation remains future gate. Avoid source-test-count "PASS" exaggeration, 10k unmeasured benchmark, paid CI or user burden.

Progress: previous subjective global BASIC/PRO/PREMIUM/etc estimate ~40%, no objective recalculation from this iteration alone. Continue P2-16 source delivery then record exact remote SHAs and modified paths.

---
## Historical P2-14 and older notes retained
# BID OWL NEXT — P2-14 real CSV/company onboarding implemented · 2026-10-27 KST

**On next ㄱ continue P2-15 automatically.** Private `hibi89/Bid_Owl` working branch `feature/bid-owl-v1-basic-mvp` only. Fetch current feature/main heads + latest HANDOFF/STATUS/AGENTS/REQUIREMENTS/START_HERE. User expressly does not want repeated ZIP downloads/PowerShell QA; do ALL reasonable development, source verification and documentation autonomously. Protect main and original Vercel, no external paid CI, no customer data or keys.

## New P2-14 committed source
- `backend/import_local.py`: Python 3.11+ stdlib Tkinter desktop onboarding plus headless CLI. Zero-args GUI picks CSV, accepts company inputs or optional previously downloaded JSON, previews count/company/source/DB/backup necessity, then asks explicit `messagebox.askyesno` confirmation. After successful import can open **read-only** `viewer.make_server` on random 127.0.0.1 port; no new HTTP write endpoints, no public service, no ReportLab dependency. Unspecified profile fields stay None/UNKNOWN.
- `prepare_import(...)` first validates COMPLETE <=10MiB CSV via `parse_csv(...).require_valid()`, source ID (1-300 chars), company profile and real-vs-synthetic provenance; checks an existing DB using readonly `viewer.open_database` and full schema. Existing same-profile ID with changed contents is **rejected**, directs to `profile_workflow.py` CAS edit. No DB or backup created during preview.
- `apply_import(plan)`: rechecks CSV SHA-256 and DB/profile state; if NEW DB reserves destination using `path.open('xb')` to prevent a concurrent other process creating a file and being silently adopted. If EXISTING DB, always makes exclusive fresh `backups/<db>_<UTC>_<random>.sqlite3` SQLite backup **BEFORE writes**. Saves new profile with `expected_version=0`, imports bids using existing revisioned `import_bids`, evaluates each with `expected_profile_version` CAS, reports accurate PASS/FAIL/UNKNOWN counts and inserted/revised/unchanged. Already identical profile retained. Each import+assessment uses separate transactions; on mid-flight error emits `IMPORT_PARTIAL_OR_UNCERTAIN` and **preserves** backup (no automatic restore), no claim of full cross-operation atomicity.
- CLI `python import_local.py --csv FILE --profile JSON --source-id ID [--db PATH]` dry-runs by default and prints `PREVIEW_NO_WRITE`; `--apply` commits explicitly. GUI no-args requires Tkinter. Company JSON uses existing `profile_workflow.load_profile_file` 64 KiB boundary; GUI-built profiles enforce 300 char/100 item caps. Synthetic demo `DEMO-`/source `DEMO_ONLY` or company `SYNTHETIC-` cannot enter real DB.
- Windows root `START_BID_OWL_IMPORT.cmd` delegates to `backend/START_IMPORT.cmd`; GUI launcher Python py -3/standard python, no install fees or cloud. Existing demo launcher remains independent.
- `backend/tests/test_import_local.py`: **18 new test method definitions** for strict readonly preview, first insertion+evidence, existing DB consistent backup and unchanged revision, mismatched profile, malformed CSV, fake/demo provenance, foreign existing file, post-preview data/profile race, backup on exception, unknown fields, CLI preview+explicit apply, filename/path launchers, bounds and exclusive DB create.
- `backend/IMPORT.md`, `README.md`, `backend/README.md`, `START_HERE.md`, `STATUS.md` and `HANDOFF.md` updated with operating/safety boundaries. 13 test modules now declare **170 Python test methods** (previous 152 +18): 170 is a static count, **NOT 170 PASS**. Authenticated GitHub source inspection confirmed no HTTP write handler, source checks, file-exclusive new DB, backup call before import, CAS on profile & assessments. No full current-branch Python suite or native Windows GUI executed in assistant authoring environment.
- Earlier user's authentic Windows P2-10 run: 137 cases, 18 Windows SQLite WinError32 cleanup ERRORS, 119 other tests without errors; 0 assertion failures, JS syntax PASS. P2-11/12 patched handle lifetimes and regressions, but no subsequent native Windows full suite run. Do not claim WinError 32 resolved until actual measurement. All-tier previous subjective progress estimate ~35%, no evidence-based recalibration yet.

## P2-15 next autonomous tasks (do not bother user)
1. Review real importer partial-failure handling, usability and data integrity: avoid duplicate assessment recomputation on unchanged imported bids if possible, make safe report export first-use, secure customer backup/restore guided flow. Keep actual changes deliberate, no write HTTP. Add targeted regression tests, source/static verify.
2. Decide if full QA can be genuinely executed from an authorized private checkout without customer effort, paid GitHub runner or 3rd-party private source transfer; if not, continue source-level implementation and explicitly list Windows/browser QA as commercial-release blocker.
3. BASIC GUI native Windows/Excel/PDF, 7-theme responsive, package/install and speed gate, then PRO official customer-key procurement API, PREMIUM opt-in AI, trademark/KIPRIS/pricing clearance and sale readiness. No real business data to public GitHub.

---
## Prior P2-13 historical notes

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
