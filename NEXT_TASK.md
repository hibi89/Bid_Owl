# P2-23 완료 / 다음 P2-24 (2026-10-27 KST)

사용자 지시: **백엔드 우선, 프론트엔드 디자인 보류**. ㄱ = 묻지 않고 다음 작업 진행. 개인/고객 데이터 업로드 금지, 유료 CI 금지, main/Vercel 변경 금지. 작업 브랜치 feature/bid-owl-v1-basic-mvp 유지.

**이번 발견/수정:** 기존 viewer는 공고/프로필 버전과 엔진 지문만 확인해 과거 PASS/FAIL을 최신으로 표시할 수 있었다. 공고가 평가 후 마감됐거나 기한이 연장된 상황에서 이는 잘못이다. `viewer._latest_rows`와 `_status_for_candidate_keys` 모두 `assessments.is_expired`(DB v1 실제 컬럼)를 현재 마감 상태와 비교하며, 다르면 과거 `snapshot_status`는 보존하고 현재 상태는 UNKNOWN, 재판정 필요로 표시한다. 목록·상태 필터·상세에 동일 적용.

`backend/tests/test_viewer.py`: 실 DB 스키마에 맞춰 is_expired 추가 및 4곳 저장 예시 수정, 3개 마감 변동 회귀 테스트 정의. 전체 GitHub 원격 **248개 Python 테스트 함수/16개 파일**, 실제 전체 실행 PASS 아님. 별도 임시 sqlite3 실험에서 마감 전 PASS 유지 / 마감 후 UNKNOWN / 기존 만료 FAIL 유지 / 연장 후 UNKNOWN / 미평가 UNKNOWN **5/5 검사 통과**. 연결된 비공개 저장소는 로컬 실행 환경에서 다운로드/클론되지 않아 실제 테스트 248개는 실행하지 못했다. 과거 Windows 137개 중 WinError32 18개 문제의 수정 여부 미검증.

다음 P2-24: 백엔드 실제 테스트 실행 경로·오류 수정, 마감 동등 시각/시간대/손상된 날짜 처리, 사용자 반복 ZIP/PowerShell 테스트 요구 금지. UI 디자인 계속 보류. 전체 제품 추정치 기존 약 42%를 임의 상향하지 말 것.

---

# BID OWL NEXT — P2-22 status-filter backend query optimization (2026-10-27 KST)

**Next ㄱ => P2-23 BACKEND ONLY.** User explicitly rejects visual UI design and prefers backend work. Do not modify UI CSS/mockups until explicitly asked. User dislikes repeated ZIP downloads and routine manual Windows PowerShell QA; implement in connected private GitHub feature. Preserve main/Vercel, no paid CI, customer data, secrets, or public product release.

## P2-22 actual changes
- `backend/viewer.py`: `query_bids` now routes **every** list filter, including `status=PASS/FAIL/UNKNOWN`, through one metadata-first readonly snapshot. It parses bid metadata and applies casefold keyword, category, favorite keys, deadline before SQL assessment lookup. New `_status_for_candidate_keys` queries minimal latest assessment, bid version, company profile latest version and optional engine fingerprint with parameterized row-value IN in **batches of 200 (<=402 bind parameters)**. It reproduces original `_latest_rows` logic exactly for stale original bid, old/missing company, missing/old SHA256 policy, no assessment, and selected profile; anything unproven is UNKNOWN. Then only selected current page keys (<=100) load the complete assessment/provenance in `_latest_rows`. Uses same transaction and UTC expiry cutoff; returns unchanged JSON shape/category semantics. `query_detail` and static frontend files untouched.
- `backend/tests/test_viewer.py` +7 test methods: exact old/new state filter parity, SHA mismatch and removed provenance table/missing policy, 425-row 3-chunk query, browser favorites status, empty favorites, multiple profiles (newest regardless of profile vs explicit profile), preserving caller-owned SQLite read transaction. Prior 17-case combined differential parity test now exercises optimized status path. Previous expectation of old unbatched status lookup updated.
- `backend/benchmark_local.py --compare-full-scan`: additionally measures `legacy_status_pass_scan_ms` vs `status_pass_page_1_ms` and `legacy_status_unknown_scan_ms` vs `status_unknown_page_1_ms` with exact result equality on the same synthetic DB. `backend/tests/test_benchmark_local.py` has updated timing field assertions. This remains explicitly opt-in; no hidden 10k in ordinary unit suite.
- Docs: `backend/VIEWER_QUERY.md`, `backend/BENCHMARK.md`, `backend/README.md`, NEXT_TASK/STATUS/HANDOFF/START_HERE.
- Current GitHub source **245 Python test declarations in 16 test modules** (238+7). NOT 245 passing. An **isolated** Python/sqlite3 synthetic 10k-row status SQL run matched 10,000/10,000 expected classifications in 50 chunks; not an authenticated full BID OWL run or Windows speed guarantee. Full 245 Python suite/native Windows E2E/10k app benchmark not executed. Old authentic Windows run 137 tests, 18 WinError32 cleanup errors before fixes; no subsequent native confirmation.
- Overall all-tier estimated progress previously ~42%; do not use commit counts to invent percentage increases.

## P2-23 next
Prioritize **actual backend test execution and source-quality checks** in an authorized isolated environment without repeatedly asking the user to run QA, or further correctness of status result and indexing. Consider performance of metadata JSON decode/sort and SQLite assessment lookup index coverage, test real 10k exact code before promising gains. No external customer data or paid runner. Windows installer, PDF/XLSX native Korean fonts, browser acceptance, PRO government API/PREMIUM AI and brand clearance remain unavailable/unverified. Document blockers instead of claiming full QA.

---
## Earlier NEXT_TASK history

# BID OWL NEXT — P2-21 metadata-first read-only viewer pagination (2026-10-27 KST)

**Next ㄱ => P2-22 BACKEND ONLY.** User rejected two UI mockups and explicitly ordered backend-first; no CSS/design/UI image work until reapproved. User dislikes repeated ZIP and PowerShell manual testing requests. Only edit private `hibi89/Bid_Owl` feature branch `feature/bid-owl-v1-basic-mvp`; preserve main/Vercel; no paid CI, sensitive data transfers or public release. Fetch current GitHub feature/main, START_HERE, AGENTS, REQUIREMENTS, STATUS, HANDOFF.

## P2-21 implemented
- `backend/viewer.py`: Before change, `query_bids` calls `_latest_rows` for all bids and includes an expensive assessment-correlated subquery/provenance join even on page 1. Now queries just latest bid metadata for all bids, applies same Python casefold keyword, category, deadline, favorite selection and sorting, computes all categories/total, then executes ONE parameterized row-tuple `IN` query for only selected page (up to 100 keys) to load full current assessments, profiles and engine fingerprint provenance. Reorders rows to original page order and preserves output fields. The two stages share readonly SQLite BEGIN/ROLLBACK snapshot and UTC expiration cutoff; never writes the DB. `status`-filtered requests intentionally continue on old full-scan path until correctness-preserving indexed optimization proven. `query_detail` unchanged.
- `backend/tests/test_viewer.py`: +3 test methods (legacy full-scan parity over 17 different Unicode/keyword/category/expiration/page/profile/status/favorites combinations, verify fast assessment fetch uses only 2 page keys vs legacy status path, no all-row assessment scan for empty favorite/out-of-range page).
- `backend/benchmark_local.py`: optional `measure_viewer_baseline=True` and CLI `--compare-full-scan`; run same synthetic bid DB through current fast query and original full-assessment scan, verify exact matching full page items/categories/total and return separately measured `all_rows_page_1_ms` and `legacy_full_scan_page_1_ms`. No extra 10k workload unless explicitly requested; opt-in `--with-recovery` from P2-20 remains.
- `backend/tests/test_benchmark_local.py`: +2 synthetic tests for baseline parity on only 41 bids/7 assessments and invalid flag.
- `backend/VIEWER_QUERY.md`, `backend/BENCHMARK.md`, README, STATUS, HANDOFF, NEXT_TASK, START_HERE updated.

## Actual evidence vs unverified
- Authenticated GitHub source fetched/read; **238 Python test declarations across 16 modules** (233+5), **NOT 238 PASS**.
- Standalone Python/sqlite3 temporary synthetic DB test with 10,000 metadata rows proved parameterized row tuple 30-key IN, sorted page keys and readonly transaction work. This is NOT the full project's 10k benchmark and no target-PC latency is confirmed.
- Authentic full BID OWL Python 238 suite, Windows native WinError32 issue retest, HTML/Excel/PDF GUI and 10k full benchmark have NOT been run on complete private checkout. GitHub workflow test runs were previously absent. No release readiness claim.
- Previous all-tier subjective estimate ~42%. Do not automatically change it based on code/test definitions.

## Next P2-22 backend priority
- Optimize currently slow `status` filter with conservative SQL key restriction or cached assessment indexing, but preserve 100% evidence/stale profile+engine hash/UNKNOWN output correctness. Differential test all PASS/FAIL/UNKNOWN and no-profile, old metadata table, original expired state.
- Eventually instrument genuine synthetic 10k end-to-end on authorized native Windows without asking user to run routine tests. Packaging/installer, backups, Excel Korean font and original procurement API/AI tiers remain uncompleted. No frontend mockups.

---
## Historical task progress

# BID OWL — P2-20 backup evidence hash and optional 10k recovery benchmark (2026-10-27 KST)

**Next ㄱ => P2-21 BACKEND ONLY.** User explicitly suspended frontend/UX redesign after seeing unsatisfactory images. Do NOT alter visual UI/CSS or generate further mockups until asked. Work in connected PRIVATE GitHub `hibi89/Bid_Owl` on `feature/bid-owl-v1-basic-mvp`, protect main/Vercel, customer data, proprietary files, paid CI/cloud, releases. User does NOT want routine ZIP downloads/manual PowerShell QA.

## Implemented & committed P2-20
- `backend/backup_recovery.py`: Previously verified only v1 structure/FK/integrity and table counts. Added deterministic **whole-evidence SHA-256** hashing of all rows from profiles/profile_versions/bids/bid_versions/import_runs/assessments/rule_assessments and optional assessment_engine_provenance. Separate type tags for text/int/float/NULL/BLOB, fixed table names and rowid order. `RecoveryPlan.evidence_sha256` pins exact record-level digest from readonly preview; full v1 validation and evidence hash now share a readonly BEGIN snapshot. Rechecks source identity/raw byte SHA/metadata/evidence before copy and compares full evidence digest AFTER SQLite backup restore. A copied DB with the same counts but different row content fails closed. Source must be journal/WAL/SHM sidecar free both before and after snapshot/hash. No overwrite/activate of existing user DB or backup; O_EXCL destination remains.
- `backend/tests/test_backup_recovery.py`: 5 new synthetic tests (result digest, same-count target mutation detected and cleaned up, same-count source modification rejected, initial -shm sidecar refusal, WAL file appearing during hash refused).
- `backend/benchmark_local.py`: opt-in `measure_recovery=True` / `--with-recovery`, runs consistent SQLite backup + preview/full-evidence digest + new-file restore for synthetic data, stores independent ms timings `sqlite_backup_ms`, `recovery_validate_and_hash_ms`, `recovery_copy_verify_ms`, `recovery_verified`, `recovery_evidence_sha256`. Default speed benchmark remains unchanged, no hidden 10k in ordinary tests. `backend/tests/test_benchmark_local.py`: 2 new methods, small 31-bid/5-assessment recovery and invalid flag.
- `backend/RECOVERY.md`, `backend/BENCHMARK.md`, `backend/README.md` updated; STATUS, HANDOFF, START_HERE also update.

## Verification truth boundary
- Auth GitHub code readback: **233 Python test definitions across 16 test files** (previous 226 +7); not 233 PASS.
- Real isolated Python SQLite content-hash contract **5/5 PASS** (before/after backup, same-content stable, changed-record hashes differ). Separate container SQLite microbench ran 10,000 synthetic rows and 200 synthetic assessments; this is **NOT BID OWL project's authentic full 10k benchmark** and must not be cited as product performance/Windows timing.
- Actual GitHub private whole-repo unit run, Windows native GUI, SQLite WinError32 cleanup retest, real BASIC viewer+Excel/PDF, full program 10k benchmark, packaging/install still NOT EXECUTED in this iteration. Do not claim commercial-ready, full QA PASS or 10k performance.

## Next P2-21
Analyze measured 10k bottleneck in `viewer.query_bids` /`_latest_rows` (currently loads and JSON-parses all bid rows and filters/page sorts in Python; latency not measured on target PC). Implement conservative correctness-preserving optimization or index improvements with differential test fixtures across combinations of filter/category/status/deadline/favorites; continue backend and protect PASS/FAIL/UNKNOWN and engine-fingerprint semantics. Performance measurement must be actual and repeatable before increasing completeness estimate. Previous subjective all-tier completion ~42%—do not arbitrarily boost.

---
## Earlier NEXT_TASK history

# BID OWL NEXT — P2-19 safe offline SQLite backup inspection and restore (2026-10-27 KST)

**NEXT ㄱ => P2-20, BACKEND ONLY.** User explicitly rejected the current visual design and decided FRONTEND / UX REDESIGN IS DEFERRED. Do not make new UI mockups or CSS redesign; prioritize backend functionality, reliability, correctness and local recoverability. The existing browser UI stays as-is for functional smoke use. No manual ZIP/PowerShell testing requests on routine ㄱ.

Project: private GitHub `hibi89/Bid_Owl`, sole development branch `feature/bid-owl-v1-basic-mvp`. Check actual branch main/feature heads, START_HERE, AGENTS, REQUIREMENTS, STATUS, HANDOFF first. Protect `main` and original Vercel; no releases, cloud payment or customer data upload.

## Actual P2-19 source delivered
- `backend/backup_recovery.py` (new, stdlib SQLite offline only): `prepare_recovery(source, destination)` **read-only preview, no directory creation**; requires existing source file (SQLite URI mode=ro), v1 user_version, all seven required schema tables, full PRAGMA integrity_check, foreign_key_check, consistent counts of profiles/bids/assessments/import_runs, SHA-256 bytes and OS file identity. Refuses source with -wal/-journal sidecar; unverified raw WAL copies not promoted as good backups.
- `preview_summary`: `RECOVERY_PREVIEW_NO_WRITE`. `restore_to_new_file` verifies preview source identity+hash, reserves nonexistent destination via `open("xb")` (O_EXCL), uses SQLite mode=rw on that reserved output and Python SQLite Connection.backup to copy a consistent DB, checks source unchanged after copy, verifies restored v1 tables/integrity/FK/counts. **Never overwrites existing destination, never swaps live DB, never removes source or active customer DB, never automatically activates recovered DB.** On error attempts to remove only file provably reserved by invocation (dev/inode match, inode != 0); third-party path remains untouched. Concurrent changes after checks not fully excluded; no OS lock.
- CLI `python backend/backup_recovery.py --source BACKUP --destination NEW_DB` is preview by default; `--apply` explicitly creates NEW file and outputs `RESTORED_TO_NEW_FILE` with need for later manual activation. Corrupt/foreign schema, FK failure, changed/disappeared source, output collision fail closed as JSON `RECOVERY_FAILED`. Legacy v1 snapshot with no policy provenance retains historical records but UI displays old PASS as UNKNOWN.
- New `backend/tests/test_backup_recovery.py` **14 synthetic tests defined**: no-write preview and counts, verified restoration+live/original backup unchanged, overwrite and same-path refusal, corrupt/foreign schema refusal, legacy unproven PASS -> UNKNOWN, source changed/deleted postpreview, destination race no-overwrite, failure output cleanup, FK corruption, CLI preview/apply and error. Test SQLite handles explicitly closed for Windows cleanup safety.
- New `backend/RECOVERY.md` documents commands, scope, risk and activation. Remaining doc pointers updated.
- Authenticated live GitHub counts **226 Python test_* definitions in 16 modules (212+14)**; **NOT 226 PASS**. Separate stdlib Python/sqlite temporary-file backup-copy contract **8/8 PASS** (this is not current full private repo module test), with no cloud or paid runner. Actual Windows native 226-suite, installer, DOC/Excel/PDF, UI E2E, 10k performance and restore on OneDrive remains **unverified**. Earlier true Windows run 137 tests/18 WinError32; no subsequent full native measurement.
- Prior all-tier 42% subjective estimate, not automatically increased based on code/test definitions.

## Next P2-20 backend priority
1. Tighten backup source preview/copy verification and partial-cleanup/sidecar cases, improve offline 10k bid performance and data indexing based on measured local synthetic benchmark where real repo execution can be authorized without asking user repeatedly. Improve cross-process consistency; avoid promising complete filesystem locking.
2. Expand recovery to safe user-facing selection of new DB (e.g. explicit --db in existing reader) before any possible in-place restore; no overwriting active DB by default.
3. Need authentic Windows 226 suite, file locks, PDF Korean font, XLSX, loopback, installer and release safety gates later. PRO official customer-key API/PREMIUM optional AI unimplemented, branding/KIPRIS not cleared. UI aesthetic redesign explicitly deferred.

---
## Historical NEXT tasks

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
