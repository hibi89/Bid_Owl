# BID OWL STATUS — P2-25 BASIC MVP real customer-importer path wired, 2026-10-27

**User's development direction:** BASIC MVP **first**. Real flow: CSV -> company profile -> local rule screening -> SQLite -> read-only viewer/detail -> Excel/PDF reports. Once MVP passes, compare with full design, add missing features; security/stability and PRO/PREMIUM later. User has rejected current UI mockups and explicitly deferred aesthetic frontend work.

**Committed in GitHub private feature branch:** NEW `backend/mvp_smoke.py` drives the real customer importer `prepare_import/apply_import` (not just legacy CLI) using temp synthetic non-demo fixtures, then checks read-only query of two saved tenders/current rules/company profile, creates two actual local XLSX exports of saved assessments, validates Zip/OOXML and matching bid ID/status, tests second identical CSV import has prewrite SQLite backup and reuses two exact assessment IDs rather than creating another snapshot, and original reports remain byte-identical. `--require-pdf` optionally fails closed before DB writes if PDF dependency/font missing, and verifies PDF signature when available. `qa_runner.py` now requires BOTH legacy and real-importer E2E smoke PASS and fails on zero discovered unit tests. Added 5 MVP tests + 3 QA-runner tests, `MVP_ACCEPTANCE.md`, docs.

**QA truth:** **256 Python test functions defined across 17 files** (248 previous + 8). Authenticated GitHub code readback confirmed source and QA wiring. **FULL PYTHON 256 TEST RUN, new MVP smoke run, Windows native GUI/Excel/PDF and browser not executed in current session** (container lacks private repo network/clone access; no user-hosted CI). Do not claim actual `BASIC_MVP_SYNTHETIC_E2E_PASS`, Windows PASS, app performance or commercial readiness. Previous local Windows 137 test run had 18 WinError32 cleanup errors before source fixes, no documented native rerun. Product overall all-tier prior ~42% subjective, unchanged pending measured release QA.

**Next P2-26:** obtain genuine allowed end-to-end run and fix real failures; simplify BASIC first-run onboarding/export without redesign, test optional PDF/Korean font; maintain main and Vercel unchanged; don't ask user to repeat manual ZIP/PowerShell QA on ㄱ.

---
## Previous STATUS snapshots

# P2-23 (2026-10-27 KST) — 마감 시점 변경에 따른 판정 무효화

**실제 코드 변경:** `backend/viewer.py`의 일반·상태별 공고 검색에서 저장된 `assessments.is_expired`와 현 시점 마감 상태를 비교하도록 수정. 공고 및 프로필 버전·규칙 엔진 해시가 같아도 평가 이후 공고가 마감되거나 기한이 연장되어 상태가 달라지면 PASS/FAIL을 현재 결과로 표시하지 않는다. 과거 `snapshot_status`와 근거는 유지, 현재 상태 UNKNOWN/수동 재검토/상세 evidence_is_current=false. 기존 200건 상태 일괄 조회에도 동일 조건 적용.

**검증:** 실제 BID OWL v1 컬럼에 맞게 `tests/test_viewer.py` 가상 평가 스키마/INSERT를 보정하고, 마감 전후·연장 전후 회귀 테스트 3개 추가. GitHub 원격 테스트 정의 총 **248개/16파일**, 전수 테스트 **미실행**. 별도 독립 Python/sqlite3 5/5 조건 통과(이것이 프로젝트 전체 테스트 통과를 의미하지 않음). 현재 컨테이너에서 GitHub private clone/DNS 불가; 전체 Python 실행과 Windows WinError32 재확인 보류. 기존 42% 추정치 유지, BASIC 판매 준비 검증 완료 아님.

**다음 P2-24:** 백엔드 코드 실제 테스트/날짜 경계 추가 검수. 사용자가 디자인을 보류했으므로 프론트엔드 변경 금지. 개발은 private `hibi89/Bid_Owl` feature 브랜치만, main/Vercel 보존. 고객 데이터/키/유료 러너 사용 금지. 사용자의 ㄱ은 다음 작업 진행 신호.

---

# BID OWL STATUS — P2-22 backend PASS/FAIL/UNKNOWN fast filtering (2026-10-27 KST)

**Implemented in private feature branch:** `backend/viewer.py` status filters now share metadata-first paging. Keyword/casefold/category/deadline/favorites filter the metadata before fetching lightweight newest assessment/currentness rows in bounded SQL batches of 200 bids. Policy fingerprint, company version, bid revision and missing evidence conservatively determine PASS/FAIL/UNKNOWN. Only page-selected <=100 bids fetch full assessment + provenance data. Single readonly DB transaction and UTC expiration cutoff maintain consistent page results. No frontend aesthetic/JS/CSS changes, database writes, customer uploads or main/Vercel edits.

**Tests/measurements:** 7 new viewer test methods, including 425-row multi-batch synthetic, explicit profile selection, old DB lacking engine hash, misdated/stale bid evidence, favorite status, empty favorites, caller-owned transactions. Previous 17-case exact legacy parity test now applies to status fast route. Opt-in `benchmark_local.py --compare-full-scan` additionally measures and asserts PASS/UNKNOWN fast-vs-old pages on same temporary dataset. Total **245 Python test method definitions across 16 files** per GitHub remote inventory. NOT 245 executed PASS. Standalone python sqlite3 test on synthetic 10k status rows (50 batches) yielded exactly 10,000 expected statuses; this is a SQL contract, NOT full private BID OWL app benchmark/Windows timing. No full branch Python 245-run or target native Windows pass. Historical old Windows suite 137 ran with 18 file-lock errors, no verified rerun.

**Next P2-23:** pursue actual complete source backend QA and measurable 10k app performance or indexed retrieval optimization; keep UI visuals on hold. Prior all-tier subjective ~42% estimate not objectively re-scored. BASIC still not commercially validated; installer, fonts/Excel/PDF, end-to-end real company registration, genuine performance, PRO/PREMIUM remain pending. User requests autonomous GitHub work without repeated local manual QA.

---
## Prior STATUS

# BID OWL STATUS — P2-21 faster metadata-first local viewer (2026-10-27 KST)

User directive: front-end visual design deferred; BACKEND ONLY.

**Implemented on feature branch:** `backend/viewer.py` normal listing/search/category/deadline/favorites no longer loads correlated saved assessment/provenance for every stored bid. It reads latest bid metadata, uses the original Unicode Python casefold and exact filters/sort, selects page keys, then joins full assessment/provenance for only those keys with a single parameterized IN query. A single readonly transaction prevents mixing bid metadata and assessments from different commits. Existing result shape, engine-fingerprint checks, UNKNOWN-first semantics and status-filter fallback preserved. No UI markup/CSS edits, database schema migration, secrets or network writes.

**Tests and benchmark:** `test_viewer.py` +3 test methods covering parity vs historical full scan across 17 filter scenarios and bounded assessments; `test_benchmark_local.py` +2 small synthetic comparison tests. `benchmark_local.py --compare-full-scan` is optional and separately times fast vs legacy page 1 on same synthetic input, failing if results differ. Docs `backend/VIEWER_QUERY.md` and `backend/BENCHMARK.md` explain behavior. Total private GitHub **238 Python test method definitions/16 modules**, not actual suite PASS.

**Verification actually performed:** isolated Python `sqlite3` with 10,000 synthetic bid metadata rows demonstrated tuple parameter binding for page of 30, nonmutating readonly transaction and sort. It was **not** the true BID OWL complete program run, and no speedup percentage or Windows performance can be claimed. Real Python suite, Windows GUI/Excel/PDF, 10k actual benchmark, installer, prior WinError32 regression fixes remain unverified. Prior 137 executed Windows tests had 18 WinError32 cleanup errors. BASIC still not commercially validated, PRO/PREMIUM unimplemented. Previously overall ~42% subjective, unchanged.

**Next P2-22:** backend status-filter performance correctness and actual measured QA. Frontend remains deferred, main/Vercel untouched, no customer data/cloud costs or routine user-run commands.

---
## Prior status snapshots

# BID OWL STATUS — P2-20 (2026-10-27 KST)

Frontend aesthetics deferred at user's request; this stage changed backend and tests/docs only.

**Implemented:** `backend/backup_recovery.py` now hashes full local immutable procurement evidence (all v1 profile/bid/version/import/assessment/rules and optional policy fingerprint rows) as `evidence_sha256`. Source preview and copy verify record equality, not just row counts, and reject WAL/journal/SHM sidecars appearing between checks. SQLite read transaction keeps counts and evidence hash from a single snapshot. Existing active DB and backup remain unmodified; recovery still creates only a new, non-overwriting DB.

**Opt-in performance measurement:** `backend/benchmark_local.py --with-recovery` now separately measures synthetic SQLite backup, full validation/hash and verified new-DB recovery; ordinary tests unchanged. New five backup tests and two benchmark tests added. GitHub remote source inventory: **233 Python test methods across 16 modules**, NOT 233 passed executions.

**Executed evidence:** Separate isolated Python/sqlite3 content-hash behavior 5/5 PASS and isolated fake 10,000-bid+200-assessment SQLite microbenchmark in model container. Neither runs the actual private GitHub full application, Windows runtime or complete 10k viewer/performance script; no claim that full project 10k benchmark passes. Windows WinError32 original 137-suite/18 cleanup failures still need native re-run after previous source fixes. Native 233 test execution, browser, PDF/Excel, installer, recovering real user data, legal name and PROD performance remain outstanding. Product subjective overall ~42% prior estimate, not independently rescored by commits.

**Next P2-21:** index/filter/query correctness and actual measurable 10k speed improvements in backend; keep frontend postponed, no customer data/API/paid runner/main/Vercel modifications, no routine user ZIP QA requests.

---
## Historical statuses

# BID OWL STATUS — P2-19 backup integrity and non-overwriting recovery (2026-10-27 KST)

**Backend-first direction confirmed:** User dislikes both generated UI concepts. FRONTEND VISUAL REDESIGN IS ON HOLD until explicitly resumed; do not spend subsequent ㄱ calls on mockups/visual design. Focus on backend safety, correctness and data recovery. Work only in private `feature/bid-owl-v1-basic-mvp` and leave main/Vercel untouched.

**Actual implementation:** New `backend/backup_recovery.py` provides readonly SQLite v1 backup integrity/FK/schema/count/hash preview, optional explicit --apply SQLite backup-based restore to a **never-overwritten new DB file**, source SHA/identity rechecks, result verification and careful cleanup limited to invocation's reserved file. Existing live DB/backup not modified or activated. Original/legacy assessments kept intact; missing engine provenance still UNKNOWN on current viewer. New `backend/tests/test_backup_recovery.py`: 14 declared synthetic unit/integration tests. New `backend/RECOVERY.md`: operator usage and limitations.

**Measured test evidence:** Isolated Python sqlite3 source → backup → exclusive new target copy and integrity contract 8/8 PASS. **226 test functions defined in 16 GitHub test modules, NOT executed as complete real private repo suite**. No genuine Windows QA pass, no Windows WinError32 closure confirmation, no full report/browser/PDF/Excel native E2E, no 10k benchmark, no paid CI. Historical authentic 137 Windows suite encountered 18 cleanup WinError32 before repairs.

**Honest limits:** Restoring to original live path is NOT implemented (intentionally non-destructive). Existing WAL/journal sidecars are rejected. File id and SHA checks mitigate but do not eliminate concurrent edits/OneDrive/file race; recovered DB needs explicit selection after stopping apps. Backup integrity does not prove procurement correctness. BASIC cannot yet be called fully sellable; PRO and PREMIUM not implemented, installer and legal trademark clearance pending. Overall all-tier ~42% previous subjective estimate (no new objectively scored %).

**Next P2-20:** backend recovery robustness, controlled local restore verification/10k synthetic performance, reduce genuine native acceptance blockers; frontend postponed. No customer files/keys/fonts/PDF uploaded, no GitHub main/Vercel deploy or paid service.

---
## Historical STATUS

# BID OWL STATUS — P2-18 SQLite original-file preservation (2026-10-27 KST)

**Implemented, feature branch only:** DB writer can now require existing `mode=rw` SQLite and strictly validated v1 schema; caller pins dev/inode/size/mtime file identity after readonly preview. `BidOwlStore` validates expected identity before and after SQLite connect. New DB initializations must first reserve file with `xb` and pass its exact expected file identity. Integrated into real GUI `import_local.py`, legacy report CLI `cli.py`, company edit `profile_workflow.py`. Mode=ro viewer remains untouched. Never treat deleted existing path as a reason to create a blank DB, or silently write to a swapped foreign DB. Backups still precede mutations and are not overwritten.

**New regression sources:** six `test_store`, three `test_import_local`, two `test_cli_safe`, two `test_profile_workflow`: +13 methods, **212 Python test methods defined across 15 modules** total. Real stdlib `sqlite3` isolated temp-directory contract **4/4 PASS**, not full repo. No native Windows full suite/browser/report/installer/10k measured; historical 137-case Windows run had 18 WinError32 before prior fixes. Full current 212-suite NOT executed, no claim that it passes. No private-code deployment, no customer content/keys or paid runner used.

**Important limitation:** This is not an OS file lock or complete multi-process race protection. Path can mutate after checks, inode can be reused, WAL/OneDrive/network paths have different behavior; release needs authentic Windows isolation/recovery QA. Product overall previously ~42% subjective estimate; BASIC+PRO+PREMIUM+packaging, no arbitrary progress inflation. BASIC production sale remains blocked by native installer, real E2E, font/Excel, backup restore, reliability and legal clearance. Next P2-19: safe guided backups and manual restore options.

---
## Earlier STATUS history

# BID OWL STATUS — P2-17 legacy CLI prewrite safety source (2026-10-27 KST)

Implemented on private feature branch `feature/bid-owl-v1-basic-mvp`: historical `backend/cli.py` report-producing writer now validates before write, preflights existing v1 SQLite in readonly mode, refuses same-ID company changes, backs up existing DB non-destructively BEFORE migrating policy metadata or importing bids, pins profile versions and writes new current-engine-hash assessments, reserves new DB with exclusive file creation. Report failure after writes raises explicit `CLI_PARTIAL_OR_UNCERTAIN` and preserves backup; SQLite errors from main become JSON `FAILED` with code 2. No HTTP write or public data transmission. Old synthetic CLI reports and BASIC GUI importer remain distinct. `backend/tests/test_cli_safe.py` added **9 synthetic tests defined**, covering backup, policy provenance, legacy table migration, errors, foreign data protection and races. Documentation updated.

**Verification:** Current GitHub source fetched and structurally inspected; **199 Python test method definitions / 15 modules** (previous 190), not executed as current full suite. Private feature branch GitHub workflow run history returned **0 runs**. No native Windows rerun, no 199/199 PASS, no browser/Excel/PDF native or 10k performance measurement. Historical user Windows run had 137 tests/18 WinError32 errors before prior fixes. P2-17 code has NOT been independently executed in genuine full private checkout. Full product BASIC+PRO+PREMIUM/packaging subjective prior completion ~40%, unchanged pending objective release QA.

Legacy CLI still has a limited existing-DB path race where a DB deleted/replaced after readonly preflight may be newly initialized by `BidOwlStore`; `NEXT_TASK.md` prioritizes opt-in must-exist mode with non-initialization in P2-18. No assertion of full atomic multi-report transaction/automatic restore. All existing-DB backup files remain local to user; no customer files, PDF font, secrets, API keys or production main/Vercel actions.

Next P2-18: close SQLite DB path recreation gap, strengthen restored backup usability and effective BASIC Windows release testing via assistant-controlled approved means. User should not be asked to rerun ZIP/PowerShell QA on ordinary ㄱ.

---
## Previous statuses

# BID OWL STATUS — P2-16 policy fingerprint & fail-closed viewer source (2026-10-27 KST)

Private `hibi89/Bid_Owl`, branch `feature/bid-owl-v1-basic-mvp`, main protected. P2-16 added verifiable local source-based SHA-256 policy fingerprints, transactionally attached them to newly recorded assessments, automatically refuses reuse of old/different policy evaluations, and displays legacy historical PASS as current UNKNOWN until rechecked. DB v1 preserved; migration of engine metadata in `import_local.py` and `profile_workflow.py` occurs only after successful existing-DB SQLite backup. Browser remains readonly. Engine resources missing => new assessment fails closed and viewer UNKNOWN.

Modified/new: backend/bidowl/engine_identity.py, backend/bidowl/store.py, backend/import_local.py, backend/profile_workflow.py, backend/viewer.py; tests/test_engine_identity.py, tests/test_import_local.py, tests/test_store.py, tests/test_viewer.py, tests/test_profile_workflow.py, backend/ENGINE_POLICY.md, backend/IMPORT.md and handoff/status docs.

**Verification**: live GitHub source retrieved/inspected; isolated Python sqlite3 in-memory SQL contract 3/3 PASS for missing provenance, matching provenance, and current-reuse query grammar. **190 test methods defined in 14 modules, NOT executed as current full Python suite**; no native Windows retry, no installer, browser visual check or current 10k performance. Prior authentic Windows P2-10 137-run = 119 without error, 18 WinError32 cleanup errors, JS syntax PASS; P2-11 fixes not Windows reverified. Overall product BASIC+PRO+PREMIUM+installer subjective ~40%, not a measured completion metric. BASIC remains not sale ready.

Do not request routine user QA on ㄱ. Next P2-17 legacy CLI provenance/backup integration or BASIC report/restore first-use. No customer data/keys/files/font uploads, no paid runner, no main/Vercel deployment.

---
## Earlier development history

# BID OWL STATUS — P2-15 assessment reuse + explicit rescoring, 2026-10-27 KST

## Current release/development state
Private `hibi89/Bid_Owl`, feature branch `feature/bid-owl-v1-basic-mvp`. Start HEAD `04b92e44faa0ec2e9197c7e6c0c53e2e30b5e05a`. Protected main previous `c888c795bef72734f3f7016e54013b82453f11d8` and unrelated legacy Vercel remain untouched. Whole BASIC+PRO+PREMIUM+installer+sale **~40% subjective estimate** re-scored in conversation after P2-14; not a measured percentage, do not imply QA gate has passed.

## P2-15 code actually written to GitHub
- `backend/import_local.py`: reusable assessment lookup uses parameterized SQL filtered by *source_id, bid_no, profile_id*, checks current bid version and latest saved assessment's bid version, exact profile version, and whether the saved `is_expired` matches the bid's present time-based expiry. On all matches, reuse unchanged saved assessment and skip new row; changing bid, profile version or expiry triggers new evaluation.
- Extra guard: if profile.latest_version changes during import (observed at candidate reused snapshot), fail closed instead of showing stale reused outcome.
- `apply_import(plan,force_reassess=False)`: explicit override always creates fresh assessments, for upgrades to the eligibility engine; UI Tkinter checkbox and CLI `--force-reassess` (only with CLI `--apply`) added. Old snapshots remain immutable. The engine code version is NOT automatically persisted/compared in the DB; after software/rule upgrades **force-reassess is required** until future automatic invalidation.
- Return adds `assessments_reused`, changes `assessments_saved` to only newly written evaluations; `eligibility_counts` counts all CSV rows, whether fresh or reused; GUI completion message distinguishes new vs reused. Existing consistent non-overwriting backup still created on an existing DB before import/audit write, even on no-op reimports.
- `backend/tests/test_import_local.py`: previous 18 methods + **8** regressions = **26**. Covers unchanged repeat with same assessment IDs, one revised bid selected, artificial expiration flag crossover, profile change and restoration at v3 requiring full re-eval, mid-import profile drift stopping reuse and retaining backup, force reassess and invalid flag, and CLI force reassess.
- `backend/IMPORT.md`: documents exact matching conditions, identity/expiry/engine caveat, CLI override, saved/reused response shape. Existing GUI writes remain explicit opt-in and local-only; no new HTTP write route.

## Measured checks vs not measured
- **Actual isolated SQLite SQL contract:** 4/4 PASS on model Python sandbox using matching query structure and synthetic in-memory DB: same revisions reuse, expiry difference refuses reuse, bid-version difference refuses, profile-version drift raises. This does NOT run the whole authentic GitHub product or its fixture/test modules.
- Authenticated GitHub source was read back for SQL and tests. Total **178 declared Python test methods in 13 test modules** (previous 170 +8). **NOT 178 PASS.** No full source Python integration run, no Windows Tkinter/native Excel/PDF or 10k measured workload this turn. User's earlier real Windows test (old source): 137 ran, 119 without error, 18 WinError32 SQLite file-lock cleanup errors, zero assertion failures; subsequent handle fixes never retested on Windows.
- User explicitly requested not to be burdened with ZIP downloading/manual tests. No new user action requested. No real data, API keys, private documents, paid CI, public deployment or main/Vercel changes.

## Next P2-16
1. Automatically track eligibility/rule-engine version or fingerprint per assessment so a code update cannot silently reuse logically stale snapshots; stale/legacy assessments must be recalculated safely. Needs thoughtful additive schema/backup ordering and compatibility with existing DB v1 before implementation.
2. Add read-only backup health inspection and careful guided local restore/recovery path **without** silent live DB overwrite; improve BASIC report export GUI/launcher. Keep actual customer DB strict and all writes explicitly consented/backed-up.
3. Eventually native Windows full 178+ case QA, GUI/Excel/Korean-font PDF, 10k benchmark, installer/security, official PRO user-key API, PREMIUM opt-in AI, trademark/pricing clearance. Sale readiness not yet confirmed.

---
## Earlier milestones (P2-14 and below)
# BID OWL STATUS — P2-14 local actual CSV/company onboarding · 2026-10-27 KST

**Branch/product:** private `hibi89/Bid_Owl`, `feature/bid-owl-v1-basic-mvp` (started P2-14 at `7718f34b1398d9e9309cd82a9dcb2e761778c7e7`). Main baseline `c888c795bef72734f3f7016e54013b82453f11d8` unchanged; legacy school Vercel untouched. Entire BASIC+PRO+PREMIUM/installer subjective ~35% last estimate, not recalculated by code completion alone.

**Implemented this turn:**
- `backend/import_local.py`: explicit local Tkinter GUI onboarding and CLI preview-first importer for user CSV and company profile. Validates entire CSV/contract and IDs and firm profile, refuses synthetic/demo files, checks SQLite schema and stored company **read-only** before writing; CLI defaults `PREVIEW_NO_WRITE`. Tkinter wizard shows source/count/company/backup summary and asks explicit confirmation.
- `apply_import`: guarded CSV digest and DB/profile recheck; existing DB always makes an exclusive, non-overwriting SQLite backup *before mutation*; brand new DB reserves file via exclusive `open('xb')` against creation race; profile create with expected_version=0; uses existing versioned import + pinned profile-version rule assessments; mismatch of existing company requires separate CAS-backed edit; local-only outputs honest counts. Partial failures retain backup and are not represented as atomic rollback.
- Root `START_BID_OWL_IMPORT.cmd` plus `backend/START_IMPORT.cmd` double-click entry. GUI may open existing readonly viewer on loopback after import; no HTTP write routes, external source or subscription. `backend/IMPORT.md` detailed usage/security, root/backend READMEs and START_HERE quickstart updated.
- `backend/tests/test_import_local.py`: **18 new declared test methods** including dry-run, first registration, saved evidence, existing DB backed-up reimport, profile mismatch no-write, foreign DB preservation, bad CSV/demo rejection, source bounds, after-preview CSV/profile and new-DB file-creation race, partial-write backup retained, missing profile fields UNKNOWN, CLI explicit apply, launchers. Full test inventory: **170 methods across 13 Python test modules**. This number is source count only.

**Verification actually obtained:** Authenticated GitHub source readback + static inspection found (a) preview opens DB in SQLite mode=ro; (b) backup_to invoked before import; (c) expected_version profile CAS; (d) expected_profile_version assessment CAS; (e) newly exclusive file reservation and Tkinter explicit confirmation; (f) 18 tests defined. **NO authenticated full source Python 170-case execution and NO native Windows GUI execution in this authoring environment**. Do not claim 170 PASS/Windows installer/BASIC sale readiness. Prior authentic user P2-10 Windows 137-case run returned 119 without error, 18 WinError32 cleanup errors, 0 assertion failures, JS syntax PASS. P2-11/12 fixes are in source but no real Windows rerun obtained; 10k timings and native Excel/PDF still unknown.

**Security & limitations:** No customer CSV/SQLite, API key, docs, fonts or PDF/XLSX uploaded, no external request, no paid runner, no main/Vercel or permission change. Existing DB backed up before write. Import/profile/assess spans multiple commits; on partial failure manual inspection and preserved backup, no unsafe auto-restore. Company edit of existing ID not silently permitted. Browser remains read-only on 127.0.0.1. Real upload, official API, opt-in AI, native installer/security/name clearance are later stages.

**Next P2-15:** autonomous source QA + import assessment idempotency/recovery and BASIC first-use/report usability; no routine ZIP/PowerShell instructions to the user. Final Windows 11 GUI/Excel/PDF/10k integration remains a separate release acceptance gate.

---
## Historical P2-13 and earlier status

# BID OWL STATUS — P2-13 disposable first-run demo, 2026-10-27 KST

## Stage / actual GitHub work
Repo: private `hibi89/Bid_Owl`; branch `feature/bid-owl-v1-basic-mvp` (started `6a7d1369c255936c01eaf6f1e51eed4720635c2a`). The protected `main` school demo and Vercel are unchanged. This iteration added an isolated **Windows one-click synthetic demo** to lower BASIC's first-use friction.

Implemented:
1. Root `START_BID_OWL_DEMO.cmd` forwards to `backend/START_DEMO.cmd`; Python 3.11+, no ReportLab/official API/key/cloud required.
2. `backend/demo_local.py` validates packaged `fixtures/sample_bids.csv` has only `DEMO-`/source `DEMO_ONLY` bids and `fixtures/sample_profile.json` has `SYNTHETIC-` profile. Builds assessments + 2 bids in a **fresh temporary SQLite**, with existing-file overwrite protection. Opens read-only loopback viewer on random local port, optionally auto-opens browser; Ctrl+C normal shutdown and temporary removal. Abnormal OS/process interruption may leave temp files; no deletion guarantee.
3. UI `backend/ui/index.html` + `ui.js` + `ui.css` displays synthetic warning in every 7-theme mode whenever rows from `BIDOWL_SYNTHETIC_DEMO` source appear; no new writable HTTP endpoint.
4. `backend/tests/test_demo_local.py` adds 8 synthetic tests: import/provenance/assessments, file overwrite guard, modified CSV marker rejection, changed company rejection, readonly HTTP loopback, temporary cleanup via fake server, invalid port, banner/launchers.
5. `backend/DEMO.md` + root README/START_HERE/backend README and status/next/handoff updated. Legacy root BID INSIGHT readme and historical QA data retained, explicitly distinguished.

## Verification: measured vs source-only
- Exact GitHub `backend/ui/ui.js` fetched and passed V8 JavaScript **syntax parse**. Static source inspection confirmed demo provenance sentinel, read-only viewer route, temporary DB context and guarded existing path; these are **not Python integrated test executions**.
- Python tests defined **152** in 12 test files after addition; **full current branch Python 152-run NOT EXECUTED**. Previous user Windows actual run (older 137-test source) was `137 ran; 18 WinError 32 cleanup errors; 0 assertion failures; 119 successful; JS syntax PASS; downstream smoke/10k SKIP`. P2-11 SQLite handle fixes plus P2-12 AST regression remain unconfirmed by a fresh native Windows suite.
- The new demo server, CMD double-click, Windows browser/Excel/PDF, 10k synthetic measurements and packaged installer were not run on user's Windows in this iteration. Do not claim runtime PASS, sale-ready BASIC or guaranteed temp file deletion.
- All-tier completion ~35% remains **subjective previous estimate**, not re-scored by adding a demo.

## Next
P2-14: reduce real BASIC CSV+company CLI friction with a safe explicit local wizard/importer while preserving backups, input validation, separate live/customer DB from demo and 127.0.0.1 read-only HTTP. User has requested AI perform routine work without repeated ZIP downloads/manual tests; continue GitHub source work and verifiable static checks. Final native Windows QA is a future release acceptance gate, not an immediate request.
No customer CSV/SQLite/PDF/XLSX/secret/keys/fonts uploaded, no paid CI or external service, no production/main action. Author/committer and final feature/main SHA must be queried after HANDOFF commit.

---

# BID OWL STATUS — P2-12 autonomous QA hardening, 2026-10-27 KST

**Latest live-source state:** 144 Python test method definitions in 11 files; **not yet executed as a current 144-case suite**. First real Windows P2-10 ZIP run: 137 ran, 119 without error, 18 WinError 32 locked SQLite temporary files, 0 assertion failures. Current code fixes from P2-11 and P2-12 not yet native-Windows-rerun. Overall all-tier subjective completion estimate remains ~35%.

**New P2-12 GitHub changes**
- `backend/tests/test_sqlite_handles.py`: new 4-method AST regression suite catches direct unsafe sqlite3/open_database context managers. Three isolated scanner cases executed PASS locally in Python; full tree condition unexecuted on authentic repo.
- `backend/tests/test_store.py`: +1 portable connection-spy test verifies SQLite backup destination is actually closed, even on Linux where deleted open files otherwise mask the WinError. Minimal stand-alone spy mechanism PASS in local Python, not integrated test result.
- `backend/qa_runner.py` and `backend/tests/test_qa_runner.py`: isolation semantics changed to continue real synthetic smoke and explicit opt-in 10k benchmark after unrelated unit/smoke FAIL while still returning overall FAIL; +1 test for independence, existing mock fixture revised.
- `backend/BENCHMARK.md`: explains independent stages and real Windows 137-run evidence. `NEXT_TASK.md`, `STATUS.md`, `HANDOFF.md`: updated.
- Remote source inspection of 25 Python files found **zero direct bare `with sqlite3.connect(...)` or `with open_database(...)` patterns**. Static scan does not cover aliases or arbitrary connection retention.
- No full Python suite, native browser, native Excel/PDF or 10k timing executed in this authoring environment due lack of authenticated mounted private checkout. Do not claim source pass equals Windows validation.

**Operating instruction:** User previously objected to repeated manual ZIP downloads/tests. Do NOT ask them for routine QA each ㄱ; continue developing autonomously on feature branch and distinguish code readiness from final Windows validation. No public deployment, paid CI, customer-data transfer, API key or main/Vercel modifications.

## Prior P2-11 factual result and background below

# BID OWL STATUS — actual Windows P2-11 test remediation, 2026-10-27 KST

## Actual measured quality signal
User executed current P2-10 downloaded GitHub ZIP on Windows PowerShell in backend (Python 3.11, ReportLab 4.5.1):
- `python qa_runner.py --benchmark`
- Python unittest **137 ran in 7.237s; 119 finished successfully, 0 assertion failures, 18 ERROR, 0 skipped**.
- All 18 ERRORs show `PermissionError: [WinError 32]` deleting temporary SQLite or backup files from `TemporaryDirectory.cleanup` on Windows. This is SQLite handle-lifetime/connection-close defect in production backup creation and test cleanup.
- JavaScript syntax PASS; dependent smoke_local and synthetic 10k benchmark SKIPPED (not PASS) after Python suite error.
- Local machine results saved in Git-ignored `backend/qa_results/bidowl_qa_20261026T174533Z_6780ada1.json` (user's observed JSON result). No user/customer data uploaded.
- This is the first current-branch measured Python suite result, replacing previous statements that no current full suite ever executed. **Never say 137 PASS**.

## Changes committed this iteration, pending user's Windows rerun
- `backend/bidowl/store.py`: `BidOwlStore.backup_to` now closes destination SQLite connection explicitly using `contextlib.closing`; previous `with sqlite3.connect(...) as target` committed but did **not** close, leaving backup files locked on Windows.
- `backend/tests/test_viewer.py`: seven read-only viewer SQLite contexts explicitly closed before fixture tempdir cleanup.
- `backend/tests/test_report_existing.py`: two snapshot-reader/Excel HTTP test SQLite contexts explicitly closed.
- `backend/tests/test_store.py`: 4 synthetic sqlite3 schema-check contexts now both commit and close using `with closing(sqlite3.connect(future)) as db, db:`; added Windows regression for immediate backup file deletion after integrity check (tests/source total 138).
- `backend/qa_runner.py`: future local JSON reports per-test last exception summary (`failed_test_errors`) to diagnose without uploading lengthy console logs.
- `NEXT_TASK.md`, `STATUS.md`, `HANDOFF.md` updated.

## Verification interpretation
Auth GitHub fetched live source and confirmed 138 declared Python test functions (benchmark3, eligibility27, importer21, profile12, runner3, report21, report_existing10, smoke1, store30, viewer10). The prior actual 137-test run is **FAILED**; the new 138-test current source has **NOT been run again** on Windows. Source inspection shows all plain `with open_database(..)` / `with sqlite3.connect(..)` patterns remaining in relevant tests converted to explicitly closed, target in backup_to closed. Minimal isolated Python syntax check of `with closing(sqlite3.connect(...)) as db, db:` succeeded, but no authenticated full checkout executing suite inside assistant container due private git/DNS/auth limitation.
Browser 7 themes, native Windows Excel/PDF, portable installer, PDF fonts and synthetic 10k timings still pending. Previous P1 96 PASS historical does not override observed P2 full-suite failure. Overall all-tier estimate ~35% subjective and unchanged.

## Repository restrictions
Private hibi89/Bid_Owl ID 1399359397; only branch `feature/bid-owl-v1-basic-mvp` changed. Previous feature SHA f2f408299abdf4402abd83a7a07376ee9cbc47b7; protected `main` baseline c888c795bef72734f3f7016e54013b82453f11d8. Existing 2025 school demo Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched. No public deploy, no real procurement data/API, no customer files/keys/fonts, no paid runner or privilege changes.

## Next action
User should download a **fresh feature ZIP** (old ZIP cannot reflect commits), extract, open backend PowerShell and run:
`python qa_runner.py --benchmark`
Python 3.11 and ReportLab already installed in previous run. Attach new `backend/qa_results/bidowl_qa_*.json` or new console output. New run should execute **138** tests if all discovered; resolve any actual failures instead of counting definitions. If full suite PASS, inspect real synthetic smoke and 10k timings; compare tested ZIP's branch/commit by provenance. Then validate Windows native XLSX/PDF/Edge and usability. BASIC not yet sale-ready; P3 PRO official API/P4 AI/installer/KIPRIS remain later.
