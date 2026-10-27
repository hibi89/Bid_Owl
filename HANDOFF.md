# BID OWL P2-28 HANDOFF — 2026-10-27 KST

1. **목표·용도·확정 요구·기술:** Windows 11 로컬 BID OWL BASIC (입찰 CSV·회사 프로필→PASS/FAIL/UNKNOWN 근거→SQLite 버전/판정 이력→읽기 전용 조회→Excel/PDF). Python/Tkinter/SQLite, PDF 선택형 ReportLab+한글 TTF. 이후 최초 설계 비교 → 품질/보안/설치 → PRO/PREMIUM. KIC 해외 공시라이트닝은 향후 독립 파생.
2. **이번 변경·근거:** `backend/import_local.py` GUI는 보고서 실패 이후 경고+성공 표시를 동시에 하던 혼동을 `import_completion_notice` 단일 메시지로 교정했다. SQLite 쓰기 성공과 XLSX/PDF 후속 실패 구분, 백업/완료 파일/평가 ID 보존 및 열람 선택 유지. `backend/tests/test_import_local.py`에 3개 회귀 테스트 작성. 주요 코드 커밋 `a4c1254e33f637e008f0698df6b3d269eb5ce0bc`, 테스트 커밋 `663d61d407289b4222c0c046f258b48f6b7a5402`.
3. **실행·검증:** GitHub API에서 `backend/tests/test_*.py` 17개 파일을 직접 읽고 `def test_*` **269개 정의** 확인. 독립적으로 기능 복사해 Python 3.13에서 3/3 PASS; 실제 레포 전체 테스트는 **0건 실행**, 소스 전체/Windows GUI/PDF/Excel/브라우저/성능 **미검증**. 실행 명령: `cd backend && python qa_runner.py`, `python mvp_smoke.py`; PDF 옵션 `python mvp_smoke.py --require-pdf`.
4. **작업 상태:** GUI 실패 표현 오류 수정·GitHub 반영 완료. BASIC 구성 코드 존재, 실제 E2E 수용 대기. 판매/설치/PRO API/PREMIUM AI 미검증 또는 미구현. KIC 파생 작업 미적용.
5. **차단·실패·대안:** 컨테이너에서 `git ls-remote` DNS 실패(`github.com` 호스트 확인 불가); 해당 방법 반복 금지. Branch GitHub Actions run 0건(무료 보장 없이 CI 변경 금지). 이전 사용자 Windows 137개 실행 중 WinError32 18건, 이후 수정 실기기 재확인 없음. 대안: 승인된 무료 전체 체크아웃 환경에서 직접 QA 실행/결과 확인; 접근 불가 시 코드 단위 수정으로 전환하고 통과 주장 금지.
6. **저장소·브랜치·SHA·경로:** private `hibi89/Bid_Owl`; `feature/bid-owl-v1-basic-mvp`. 시작 HEAD `ce5e59d7c64c260322049d51ef5a38f7d7fadce4`, 코드+테스트 후 `663d61d407289b4222c0c046f258b48f6b7a5402`; **이 문서 포함 최신 HEAD는 최종 조회**. `backend/import_local.py`, `backend/tests/test_import_local.py`, `backend/mvp_smoke.py`, `backend/qa_runner.py`, `backend/MVP_ACCEPTANCE.md`.
7. **Production/Vercel:** 레거시 프로젝트 `project08-bid-insight`, ID `prj_YcrN7OdOjKl6M457HelGIItLeeXZ`; Windows Python GUI는 Vercel **배포 비대상**. Production SHA/익명 브라우저/실제 URL 기능 검증 미확인, 설정 변경 없음. 실행은 `START_BID_OWL_IMPORT.cmd` / `python backend/import_local.py`.
8. **원본·백업·인증·금지:** 교육용 `main` 복원 SHA `2807a93a3e0deba98840712401fdd6025e6f5610`, 현재 main 보존. 기존 SQLite 수정 전 백업, CSV/원본 공고·회사 문서·키·개인 DB는 외부/API/GitHub 업로드 금지. GitHub 연결 계정 `hibi89`, 원본 main/Vercel/권한 무단 변경 금지.
9. **다음 우선순위·승인:** P2-29 실제 무과금 QA→실패 수정→Windows GUI/한글 PDF/Excel/WinError32 검증→MVP 요구사항 대조 → 품질·설치 → PRO/PREMIUM. 유료 CI, 공개 배포, 민감 파일 전송, 원본 수정은 승인 필요. 사용자 `ㄱ` 즉시 이어가기.
10. **갱신/검증 범위:** 2026-10-27 KST. GitHub 인증 연결로 소스·테스트·트리/커밋 확인, 환경 DNS 실패, 좁은 독립 함수 실행 3/3만 성공. 본 인수인계 기준 커밋 `663d61d407289b4222c0c046f258b48f6b7a5402` 이후 문서 커밋은 GitHub HEAD 조회. 실 데이터/Windows/Production 미확인.

---

# BID OWL — P2-27 HANDOFF / 2026-10-27 KST

1. **목표·확정 기술:** 로컬 Windows BASIC MVP (CSV→회사 정보→PASS/FAIL/UNKNOWN/근거→SQLite→읽기 전용 조회→Excel/PDF). Python 3.11+, Tkinter, SQLite, 선택 ReportLab. KIC 공시라이트닝은 해외 공시 어댑터를 별도 개발하며 **현재 제품에 병합하지 않음**.
2. **완료·변경:** `backend/import_local.py` GUI 보고서 폴더·형식 선택, 사전 PDF 검사, DB 저장 후 읽기 전용 보고서 내보내기. GUI/CLI 공용 `export_saved_assessments`, 부분 실패시 이미 저장된 DB·백업과 기존 보고서 보존·확실한 성공/실패 구분. UI 시각 재디자인 없음. 고객 유료 API/PRO/PREMIUM 미착수.
3. **테스트:** 독립 Python helper prototype 3/3 PASS (실제 repo 실행 아님). `backend/tests/test_import_local.py` 회귀 3개 추가; **266개 테스트 정의, 실제 프로젝트 테스트 전체 0건 실행**. 종합 명령 `cd backend && python qa_runner.py`; 빠른 필수 `python mvp_smoke.py`, 옵션 `python mvp_smoke.py --require-pdf`. 출력 경로 `backend/qa_results/` (로컬, GitHub에 원본 데이터 업로드 금지). GUI/브라우저/Excel/PDF Windows 실기기 **미검증**.
4. **단계:** 실제 BASIC 구성요소 코드 연결 및 GUI 보고서 사용 흐름 구현; 실행·진짜 E2E 수용 **대기**, Windows/상용 출시는 차단, PRO/PREMIUM 미구현, 기존 프론트 디자인 보류.
5. **실패·원인·재시도 정책:** 사설 저장소 `git ls-remote`는 github.com DNS 해석 불가로 실패; 같은 환경에서 재시도하지 않음. 과거 Windows 실행은 137건 중 18건 WinError32 임시파일 정리 문제, 수정 확인 전. 대안은 승인된 무료 실행 환경에서 실제 checkout+QA, 결과부터 검토; 통과 추정 금지.
6. **Repo/branch/SHA:** `hibi89/Bid_Owl` (private) / `feature/bid-owl-v1-basic-mvp`; 작업 시작 `6154604f9faa5b7b78c67060ab33771ba5129bdc`; 최신 코드·테스트 커밋 `868d9d34be4d59298f9e752f436a15bc07028858`. 중요: `backend/import_local.py`, `backend/tests/test_import_local.py`, `backend/mvp_smoke.py`, `backend/qa_runner.py`, `backend/MVP_ACCEPTANCE.md`. 최종 문서 HEAD는 다음 GitHub 재조회로 확인.
7. **Production/Vercel:** 레거시 Vercel `project08-bid-insight` (`prj_YcrN7OdOjKl6M457HelGIItLeeXZ`); 이번 브랜치의 Python GUI는 **배포 비대상**. Production URL, 최신 SHA 일치, 웹 실제 동작은 미검증. 코드는 로컬 `python import_local.py` 또는 `START_BID_OWL_IMPORT.cmd`.
8. **원본/백업·보안:** 학원 레거시 main 복구 SHA `2807a93a3e0deba98840712401fdd6025e6f5610`. 기존 SQLite는 수정 전 별도 백업, 보고서 기존 파일 덮어쓰기 금지. 고객 DB/API 키/회사정보/보고서는 커밋·외부 전송 금지. GitHub 연결 `hibi89` 계정 push 확인, 원본 main과 Vercel 설정 변경 금지.
9. **다음 작업:** P2-28 전체 QA 실제 실행 환경 확보 → 실제 실패만 수정 → GUI 저장/보고서 이중 실행/파일 충돌 검증 → PDF 한글/Excel/WinError32 실기기 → `REQUIREMENTS.md` 대비 BASIC 잔여 기능 → 출시형 보안·패키징 → PRO/PREMIUM. 유료 CI·배포·실데이터 전송·권한 변경은 사전 승인.
10. **갱신·검증 경계:** 2026-10-27 KST, GitHub 커밋 소스 직접 조회 및 코드 변경 반영 확인, 독립 3-test prototype 실행, 실제 사설 프로젝트 런타임 미실행. 본 문서 기준 **코드 커밋 `868d9d34be4d59298f9e752f436a15bc07028858`**, 문서 최종 HEAD는 조회 필요.

---

# BID OWL HANDOFF — P2-26 BASIC one-shot real importer + reports (2026-10-27)

## User directive
User plans eventual reuse of BID OWL as derivative **Disclosure Lightning** overseas regulatory-filings product for KIC hackathon. They explicitly said continue BID OWL's existing work, NOT to start overseas filing implementation now. Prioritize complete **BASIC MVP** (CSV/profile, PASS/FAIL/UNKNOWN, SQLite evidence, read-only viewer, XLSX/PDF), actual E2E execution over deep hardening. Frontend design mockups rejected; visual frontend changes deferred. User `ㄱ` means make real GitHub code commits autonomously, no repetitive user ZIP/PowerShell chores. Private repo `hibi89/Bid_Owl`, only `feature/bid-owl-v1-basic-mvp`, protected main/Vercel, no paid CI/cloud/customer data upload.

## P2-26 source and behavior
- `backend/import_local.py` `_reusable_assessment_status` selects saved `a.id AS assessment_id` and returns `(id,status)` when BID/profile/current policy SHA/deadline all match; `apply_import` records exact assessment ID and `reused` flag both when assessing fresh and when using saved snapshot in `assessments` result.
- `backend/import_local.py main` new explicit `--export-dir` (requires `--apply`) and optional `--report-format xlsx|pdf|both`. PDF dependency/font preflight occurs before DB write; report export from `report_existing.export_existing` uses read-only DB/snapshot, refuses replacing existing reports. On success returns `IMPORTED_AND_EXPORTED`, list of `reports` IDs/files and `assessments`. If export fails after DB import succeeds, returns `IMPORTED_EXPORT_FAILED` and exit 2, identifies previously completed reports, DB/backup preserved, does NOT mislabel as import failure or autoundo import. Defaults still import-only, plain preview no changes.
- `backend/mvp_smoke.py` synthetic smoke includes **separate** one-shot CLI import into isolated DB and XLSX export 2 reports, checks same IDs and valid ZIP. `test_mvp_smoke.py` verifies one-shot count.
- `backend/tests/test_import_local.py` +7: stored/reused IDs, XLSX OOXML and saved IDs, export failure status, report collision no overwrite despite repeat registration, PDF missing font before write, export without apply rejected, second report failure and earlier generated XLSX preserved.
- `backend/IMPORT.md`, `backend/MVP_ACCEPTANCE.md`, `backend/README.md` document CLI and next derivatives. Status/next/start also updated. `main` original static app untouched, no CSS work.
- Latest current GitHub **263 test definitions / 17 test modules** (256 before), NOT suite 263 PASS. No private full source real execution or native Windows, PDF font, Excel or browser QA. Older user Windows suite was 137 run, 18 WinError32 file cleanup issues, not proven fixed. Previous whole BASIC+PRO+PREMIUM/installer estimate ~42% subjective, unchanged pending objective run.

## Next P2-27
1. Obtain authorized local full checkout/test execution without imposing repetitive manual user work, fix actual current code runtime failures, record reproducible signed-off QA result. No private paid CI or public deploy.
2. Ensure first-use BASIC can access reports using new CLI and GUI/viewer functional buttons without visual redesign; consider minimal error handling and export discoverability.
3. Then integrated 10k/Windows release QA, actual font/rendering, packaging, spec gap check. KIC adaptation later and separate (foreign filing source adapter, independent type/policy; avoid carrying Korean tender-specific semantics into international disclosure).
4. On next `ㄱ` read repo heads and top docs and continue coding. Fetch final feature/main SHA now; never claim a guessed commit. Keep docs accurate.

---
## Previous handoffs

# BID OWL HANDOFF — P2-25 MVP-first acceptance, next P2-26

**User priority:** user explicitly asked "지금 mvp부터만드는거맞제" and agreed to proceed with ㄱ. Restore original plan: BASIC MVP functionality and true E2E before premium extensions/hardening. User rejected both UI images: **NO frontend aesthetic redesign** until explicit request. They want actual GitHub code committed, not repeated local manual scripts, ZIP downloads or PowerShell QA chores. Private repo `hibi89/Bid_Owl`, feature branch `feature/bid-owl-v1-basic-mvp` exclusively; main/Vercel protected, no paid private Actions/cloud, real customer data/keys or public release.

**P2-25 actual code changes:** Added `backend/mvp_smoke.py` using real `import_local.prepare_import/apply_import` and non-demo safe synthetic fixture copied to temp; preflight no-write; evaluate two real-contract bids with company profile; local SQLite version+evidence persistence; read-only `viewer.query_bids/query_detail/query_profile` and mutation refusal; `report_existing.export_existing` creates saved snapshot XLSX, verifies archive and XML and bid IDs/status; checks same CSV repeat import backup preserves 2 previous assessments, 0 saved/2 reused, report files unchanged; optional strict `--require-pdf` prechecks ReportLab & Korean font prior to DB writes and asserts PDF bytes. No customer path/default DB/network involved.
- NEW `backend/tests/test_mvp_smoke.py` 5 synthetic tests covering actual importer-to-report, CLI JSON, PDF prereq failure, failed importer cannot fake PASS, wrong require_pdf argument.
- UPDATED `backend/qa_runner.py`: existing synthetic smoke now runs both historical CLI smoke and new real importer MVP acceptance. Both must pass to return PASS, failures captured separately; unit suite with zero discovered tests now FAIL rather than false PASS.
- UPDATED `backend/tests/test_qa_runner.py`: 3 extra tests for both smoke stages required, new MVP broken while old CLI succeeds, and 0-tests discovered fail.
- New `backend/MVP_ACCEPTANCE.md`, updated `START_HERE.md`, `README.md`, `backend/README.md`, `NEXT_TASK.md`, `STATUS.md`, `HANDOFF.md`. Total **256 test_* definitions in 17 modules**, not 256 PASS. Feature branch started at `817b6b0b4fd2927815dd58ba8738a7d04448e457` (P2-24 wrote no GitHub commits due safety block). Main baseline `c888c795bef72734f3f7016e54013b82453f11d8`. GitHub writes worked this turn. Re-fetch final branch SHA and changed files.

**Potential remaining gaps:** New complete E2E source is not actually executed on private checkout; potential integration failures are not ruled out. Old `smoke_local.py` uses synthetic legacy CLI, new code tests actual customer's importer core. Actual Tkinter window, browser flow, strict PDF Korean font, Excel desktop open, native WinError32 lock, proper installer still not validated. Importer is multi-stage; report export is separate read-only step after saved DB and should NEVER be claimed atomic/auto-restored. Old P2-24 QA zip has a smaller standalone tester, but GitHub already had the stronger qa_runner; no need to duplicate it. PRO procurement API and PREMIUM AI not implemented. Overall old subjective ~42%.

**NEXT ㄱ => P2-26:** MVP-first: seek real test run with available permitted environment (no paid CI/unapproved deployment and no asking user to run repeated ZIP/PowerShell manually) then fix failures. If no actual test runner access, inspect/test integration boundaries conservatively, add a simple first-use BASIC CLI/user workflow with import success separate from export failures, and prioritize true operational MVP over more broad hardening. Keep docs and branch commits current and accurate, no UI visual work.

---
## Prior HANDOFF notes

# P2-23 (2026-10-27 KST) — 마감 시점 변경에 따른 판정 무효화

**실제 코드 변경:** `backend/viewer.py`의 일반·상태별 공고 검색에서 저장된 `assessments.is_expired`와 현 시점 마감 상태를 비교하도록 수정. 공고 및 프로필 버전·규칙 엔진 해시가 같아도 평가 이후 공고가 마감되거나 기한이 연장되어 상태가 달라지면 PASS/FAIL을 현재 결과로 표시하지 않는다. 과거 `snapshot_status`와 근거는 유지, 현재 상태 UNKNOWN/수동 재검토/상세 evidence_is_current=false. 기존 200건 상태 일괄 조회에도 동일 조건 적용.

**검증:** 실제 BID OWL v1 컬럼에 맞게 `tests/test_viewer.py` 가상 평가 스키마/INSERT를 보정하고, 마감 전후·연장 전후 회귀 테스트 3개 추가. GitHub 원격 테스트 정의 총 **248개/16파일**, 전수 테스트 **미실행**. 별도 독립 Python/sqlite3 5/5 조건 통과(이것이 프로젝트 전체 테스트 통과를 의미하지 않음). 현재 컨테이너에서 GitHub private clone/DNS 불가; 전체 Python 실행과 Windows WinError32 재확인 보류. 기존 42% 추정치 유지, BASIC 판매 준비 검증 완료 아님.

**다음 P2-24:** 백엔드 코드 실제 테스트/날짜 경계 추가 검수. 사용자가 디자인을 보류했으므로 프론트엔드 변경 금지. 개발은 private `hibi89/Bid_Owl` feature 브랜치만, main/Vercel 보존. 고객 데이터/키/유료 러너 사용 금지. 사용자의 ㄱ은 다음 작업 진행 신호.

---

# BID OWL HANDOFF — P2-22 status filter backend optimization complete, next P2-23 (2026-10-27 KST)

## User's current standing instructions
The user uses `ㄱ` to request actual continued coding on connected GitHub without repeated permission or manual Windows ZIP/PowerShell QA tasks. They strongly disliked the two earlier UI designs and explicitly chose **BACKEND FIRST, FRONTEND VISUAL REDESIGN ON HOLD**. Do not produce mockups, change UI theme/css/layout or deploy public assets. Repo PRIVATE `hibi89/Bid_Owl`, working branch `feature/bid-owl-v1-basic-mvp` only, protect main historic Vercel. No customer data in connector/API, no paid runner/releases/PRO API key use without approval.

## P2-22 actual implementation
- Source `backend/viewer.py`: user-chosen PASS/FAIL/UNKNOWN status list filtering no longer calls full correlated assessment/provenance query for ALL bids. Reuses the P2-21 `_query_without_status` metadata-first pipeline with optional status argument, fetching latest bid JSON metadata and applying old exact Python Unicode casefold search/category/favorite/deadline logic. Only metadata candidates are evaluated with newly added `_status_for_candidate_keys`. SQL processes up to **200 (source_id,bid_no) keys** per batch using parameterized row-value `IN` (402 bind vars), LEFT JOIN latest matching assessment (profile '' means any, profile explicit matches x.profile_id) and selected matching company profile and policy engine provenance. Uses same freshness condition as `_latest_rows`: assessment_id nonnull, current bid version, current company profile version, runtime fingerprint exists and equals saved SHA-256. Anything unverifiable => UNKNOWN. Old schema v1 without assessment_engine_provenance, missing policy sources, stale assessment/profile all conservative. Filter by requested status, sort metadata with old order and choose page, then fetch detailed assessment+provenance **only for page keys <=100** via original `_latest_rows(...candidate_keys,as_of)`. One readonly BEGIN/ROLLBACK transaction when caller not already in transaction. Avoids changing frontend/SQLite schema or HTTP write routes.
- `backend/tests/test_viewer.py`: +7 test methods, with expanded differential and page-bound existing test updated. New tests verify status PASS/FAIL/UNKNOWN+deadline/category/profile vs full _latest_rows, mismatch engine hash and missing provenance/source, 425-bid batch/parameter boundary, status favorites, no favorites short circuit, two profiles with newest any-profile vs explicit, caller-owned readonly transaction. The previous 17-case general differential test now covers new status route.
- `backend/benchmark_local.py`: existing `--compare-full-scan` opt-in now measures `status_pass_page_1_ms` and `status_unknown_page_1_ms`, compares to `legacy_status_pass_scan_ms` and `legacy_status_unknown_scan_ms` on exact same synthetic DB and asserts full result equality; `test_benchmark_local.py` updated for the four metric keys. Default benchmark unchanged and no 10k task in normal unit suite.
- Docs `backend/VIEWER_QUERY.md`, `backend/BENCHMARK.md`, `backend/README.md`, NEXT_TASK, STATUS, HANDOFF, START_HERE refreshed. No HTML/CSS/JS changes.
- Authenticated remote GitHub scan counted **245 Python test_* definitions across 16 modules**, previous 238, NOT current execution PASS. In assistant's isolated Python sqlite3 synthetic 10k database, the current status SQL design with 200-bid chunks mapped **10,000/10,000 expected statuses**, including 1000 saved cases and rest UNKNOWN, 50 batches. This is NOT code executing a private full BID OWL app checkout or target Windows speed benchmark. Actual Windows native full-suite 245, WinError32 retest, browser Excel/PDF, 10k app benchmark, installer/security still unverified.

## GitHub and future tasks
P2-22 started from `c179dd14c9df47c58a17312b4d9eaf6ddbeaaa7a` branch; old main `c888c795bef72734f3f7016e54013b82453f11d8`. After this docs commit, FETCH and report final feature/main heads, diff counts and author. Do not guess. Historical overall BASIC+PRO+PREMIUM+packaging estimate ~42% subjective, avoid arbitrary percentages without measured acceptance.

Next `ㄱ` => **P2-23 BACKEND**: pursue authentic automated/isolated QA for full private repo without burdening user, or further validated 10k optimization of JSON metadata scan/index/profile status join. Use differential correctness and fail-closed source currentness as priorities. Never claim an unexecuted full suite passed. Continue GitHub source updates and docs, no mandatory paid GitHub Actions. User's broader product PLAN: BASIC planned KRW 59k Windows offline CSV/profile, SQLite, readonly viewer, XLSX/PDF and seven color themes; PRO planned KRW 149k customer-key government API; PREMIUM planned KRW 299k opt-in AI; brand/trademark/prices and sales unvalidated; PRO/PREMIUM not implemented.

---
## Prior handoffs

# BID OWL HANDOFF — P2-21 complete, next P2-22 (2026-10-27 KST)

**Operating instruction:** User `ㄱ` = autonomous work in connected private GitHub `hibi89/Bid_Owl`, branch `feature/bid-owl-v1-basic-mvp`, inspect latest heads/START_HERE/NEXT_TASK/AGENTS/REQUIREMENTS/STATUS/HANDOFF; implement code, tests, docs and commits. Do not repeatedly request user ZIP download or PowerShell QA. User explicitly defers frontend aesthetics after rejecting 2 image mockups: DO NOT touch CSS/JS UI redesign or generate images unless requested. Protect main, historical Vercel, private customer files, API keys, no paid CI/public deployment.

## Current implemented source
1. `backend/viewer.py`: new `_query_without_status` metadata-first path for all `query_bids` without a status filter, including all ordinary browse/search/category/deadline/favorite routes. SQL reads `bids JOIN latest bid_versions` (no assessments) for all rows. Same Python `casefold`, date parsing, search/category/favorite/deadline criteria and lexicographic tuple sort; categories from *all* bids, before filters. After pagination (max page_size=100), `_latest_rows(...,candidate_keys=keys,as_of=now)` fetches only the chosen page's assessment/profile/policy provenance with safe row-value IN placeholders; result reorders to chosen page. Uses readonly SQLite BEGIN/ROLLBACK snapshot if not already in transaction; no HTTP write or schema change. Status-filter queries deliberately continue original full-scan `_latest_rows` to avoid stale/UNKNOWN semantic changes. Detail reader untouched.
2. `backend/tests/test_viewer.py`: +3 test declarations: compare output to original full scan across 17 filter combinations with 65 extra synthetic bids including Unicode Straße/AI Korean, old/open deadlines, pagination, favorites including empty and unmatched, statuses and profiles. Additional tests verify candidate keys exactly 2 and status path fallback, empty favorites and out-of-range page no assessment full scan.
3. `backend/benchmark_local.py`: new optional `measure_viewer_baseline` and `--compare-full-scan`; measures old full assessment scan and new metadata-first query on SAME synthetic 10k target when explicitly run, checks exact items/categories/total. Old P2-20 `--with-recovery` remains. `backend/tests/test_benchmark_local.py` +2 tests on only 41 bids/7 assessed and invalid boolean.
4. New `backend/VIEWER_QUERY.md` full query contract, limitations, correctness scope. Updated BENCHMARK/README and handoff docs. No frontend visual files modified.

## Evidence limits
GitHub authenticated readback counted **238 Python test methods across 16 modules**, NOT 238 executed PASS. Separate Python/sqlite3 temporary synthetic 10k metadata and 30-bound-key experiment returned success, but did not execute actual BID OWL code or Windows. No target machine timing, no genuine complete private 238-test run, no Windows WinError32 fix confirmation, no GUI/Excel/PDF/integrated 10k/installer release gate. Historic user Windows 137-suite had 18 WinError32 cleanup errors. Product entire BASIC+PRO+PREMIUM/install previous ~42% only subjective. Protected main baseline `c888c795bef72734f3f7016e54013b82453f11d8`. Feature began at `112c371cc4861eb828adf4cb2ab12b4b08468f21`; fetch real latest feature HEAD after HANDOFF commit and compare changed paths.

## Next P2-22
Optimize status-filter path safely without changing PASS/FAIL/UNKNOWN and rule-engine currentness or profile version checks. Build differential tests with old metadata v1, no provenance, changed policy hash, expiry and favorites. Or source QA of metadata-first path; preserve exact sorting, categories. Need true 10k speed measurement and native Windows full test execution when authorized without repeatedly asking user. Avoid frontend design until user explicitly resumes.

---
## Previous handoff history

# BID OWL HANDOFF — P2-20 complete, next P2-21 (2026-10-27 KST)

## User policy
User says `ㄱ` to autonomously continue private GitHub feature development and dislikes repetitive manual ZIP/Windows PowerShell testing. User explicitly deferred frontend/visual design after rejecting two mockups. **DO NOT touch UI aesthetics or regenerate images** absent explicit request. Protect `hibi89/Bid_Owl` main and historic Vercel. Only work in `feature/bid-owl-v1-basic-mvp`; no paid GitHub CI, public launch, customer DB/API keys or fonts in repo.

## P2-20 changes
1. `backend/backup_recovery.py`: added full evidence content SHA-256 over 7 mandatory v1 tables (`profiles,profile_versions,bids,bid_versions,import_runs,assessments,rule_assessments`) plus optional `assessment_engine_provenance`. Hash is deterministic with per-cell type tags (including NULL and BLOB), table labels and rowid ordering. The readonly source inspection executes `BEGIN`, full integrity and foreign-key check, table counts and streaming evidence hash in one snapshot, then releases read transaction. Checks raw backup file SHA and filesystem identity and journal/WAL/SHM sidecars before and after. `RecoveryPlan.evidence_sha256` is checked on re-preflight and after SQLite backup restore; a new DB with identical counts but different values is rejected. Existing customer source and active DB are not touched, new destination uses exclusive creation, no in-place replacement or automatic activation. This is best-effort consistency, not a cryptographic signature/authenticated backup or cross-process locking.
2. `backend/tests/test_backup_recovery.py`: +5 definition tests (hash preserved on normal restore, changed destination field with same record counts caught/cleaned, changed source field with same counts blocked, existing -shm sidecar refused, -wal appearing while hashing refused).
3. `backend/benchmark_local.py`: new `run_benchmark(..., measure_recovery=False)` and CLI opt-in `--with-recovery`. Extends 10k synthetic benchmark by timing `sqlite_backup_ms`, `recovery_validate_and_hash_ms`, `recovery_copy_verify_ms` and checking recovered row counts and evidence hash. Only opt-in, no 10k hidden in normal unit tests. `backend/tests/test_benchmark_local.py`: +2 tests (31 bids/5 assessments full recovery, non-bool flag rejection).
4. Backend docs `RECOVERY.md`, `BENCHMARK.md`, `README.md`; NEXT_TASK, STATUS, HANDOFF, START_HERE updated. No frontend code changed.

## Verified vs unverified
Authenticated private GitHub source reread and counted **233 Python `test_*` definitions in 16 modules** (before 226). This is a declaration count, NOT 233 actual tests passing. Local standalone Python/sqlite3 contract content-hash tests **5/5 PASS**, plus microbenchmark of 10,000 synthetic SQLite rows+200 simple assessments in an isolated model Linux sandbox, NOT the actual full private BID OWL app and NOT Windows. No full current branch test suite, Windows file lock retest, program 10k import/viewer/backup test, PDF/Excel real fonts, installer/packaging or name clearance executed. Historical user Windows suite was 137 run, 18 WinError32 temp cleanup errors, no assertion failures; source fixes since remain unverified there. Subjective all-tier product estimate ~42%; don't inflate artificially.

## GitHub and continuation
P2-20 began feature `e8cef0769c969cf172c77191c7ea175a1500a4ee`; original main `c888c795bef72734f3f7016e54013b82453f11d8` and legacy Vercel remain protected. AFTER writing this HANDOFF, fetch feature/main heads and compare changed paths; do not guess current SHA. Next `ㄱ` => **P2-21 BACKEND ONLY**: analyze viewer `_latest_rows/query_bids` full 10k scan + JSON load and implement safe performance/correctness improvements, with differential filtered/favorites/expiry/profile-status tests. Genuine 10k performance and Windows acceptance still needed but user not asked for routine QA.

---
## Previous handoffs

# BID OWL HANDOFF — P2-19 safe backup validation and new-file restore, 2026-10-27 KST

## User's immediate decision and work policy
User finds proposed UI designs visually unacceptable. **Do NOT redesign frontend, generate UI mocks or touch CSS on next ㄱ**; user explicitly says frontend will be resolved later, backend matters now. User's ㄱ signals autonomous GitHub code/test/doc work, no repeated ZIP download/PowerShell QA demands. Continue private `hibi89/Bid_Owl`, branch `feature/bid-owl-v1-basic-mvp`, protect main and Vercel, no paid runner, customer file/API key exposure, public release/production mutation.

## New P2-19 code
- `backend/backup_recovery.py`: new standalone Python stdlib offline CLI; `prepare_recovery(source, destination)` validates *already-existing* SQLite backup with ro URI, BID OWL schema v1 user_version and all 7 tables, PRAGMA full integrity_check, FK check, counts of 4 key tables, SHA-256 and OS identity. Preview has **no filesystem writes** to destination. Refuses backup with '-wal' or '-journal' sidecar to avoid raw inconsistent copies. Return dataclass `RecoveryPlan` pinning source identity+SHA+counts.
- `restore_to_new_file(plan)`: explicit only `--apply`, re-preflight, refuses overwrite and source==destination, calls destination.open('xb') to reserve never-existing path, destination SQLite mode=rw, SQLite Connection.backup source -> target, postcopy source checksum+identity and restored file integrity/FK/count/provenance verification, no original file changes, automatic in-place activation/overwrite NEVER. On exception may remove only original reserved output if device/inode still match and inode !=0; if can't safely determine path owner, leaves file for manual inspection. No OS-level serialization promise.
- CLI command: `python backup_recovery.py --source BACKUP --destination NEW_SQLITE` = JSON `RECOVERY_PREVIEW_NO_WRITE`; append `--apply` = `RESTORED_TO_NEW_FILE`; failures `RECOVERY_FAILED` exit 2.
- Tests `backend/tests/test_backup_recovery.py`: 14 methods, fake packaged CSV and company, old-v1 missing provenance => UNKNOWN, unsafe existing output refusal, corrupt/foreign schema, changed source, cleanup/error/race, foreign key, CLI. Explicit contextlib.closing(SQLite) to avoid Windows handle leaks.
- Docs `backend/RECOVERY.md`, project NEXT_TASK.md / STATUS.md / HANDOFF.md / START_HERE / backend README updated. Development branch starts P2-19 at `1553950c3eb264eec1588c7243fc059737a22658`, main baseline `c888c795bef72734f3f7016e54013b82453f11d8`.

## Validation and remaining work
GitHub authentically checked **226 test definitions across 16 files**, not actual 226 PASS. Separate local stdlib Python SQLite recovery behavior 8/8 PASS on synthetic tmp DB, NOT the full private GitHub module. No native Windows rerun; previous real 137 tests had 18 WinError32 handle/TemporaryDirectory cleanup errors; fixes unverified. Need genuine recovery tests, 10k scaling, Windows locks / XLSX/PDF / installer, then customer API PRO, AI PREMIUM and KIPRIS brand checks. Last all-tier estimate ~42% subjective; do not raise without evidence.

## Next ㄱ
P2-20 BACKEND ONLY. Improve backup recovery robustness, measured synthetic 10k performance and data consistency, or closed gaps in existing SQLite WAL and concurrency. Keep original database safe; do not auto-replace it. Follow user instruction no frontend redesign. Refresh GitHub feature/main HEAD, handoff docs before action.

---
## Historical HANDOFF

# BID OWL HANDOFF — P2-18 strict file identity and no-create writer (2026-10-27 KST)

User's `ㄱ` means autonomously continue source dev in connected private GitHub `hibi89/Bid_Owl`, `feature/bid-owl-v1-basic-mvp`. They explicitly dislike repeated ZIP downloads/PowerShell testing. Do NOT ask user to run routine QA; make GitHub commits and perform feasible isolated/static tests yourself. Protect main/legacy Vercel, privacy, API keys, no paid runner/public deploy.

**P2-18 actual code changes**
- New `database_file_identity(path) -> (st_dev,st_ino,st_size,st_mtime_ns)` in `backend/bidowl/store.py`. Store supports optional `must_exist=True` (SQLite URI mode=rw, no CREATE, schema version1 only) and `expected_identity` (same exact preflighted physical file, check before+after connect). Old callers with no flags retain explicit/new DB creation default. Fresh `open('xb')` reserved DB uses expected_identity without must_exist to initialize only that intended file, not an accidentally created/replaced path. Missing/wrong-type file fails before schema creation.
- `backend/import_local.py`: `ImportPlan.db_identity` captured during preview and checked against second preflight, then passed to writer; existing must_exist, new reserved identity. Both existing and newly reserved DB are opened with mode=rw (not auto-create). Existing DB backup remains mandatory before first mutation.
- `backend/cli.py`: captures initial stat before readonly preflight, compares after; uses must_exist+expected_identity for existing, exclusively reserves and pins expected identity for new; preserves P2-17 consistent backup, CAS profile/version checks and report partial-failure signaling.
- `backend/profile_workflow.py`: full existing-only identity pin across readonly preflight and writer open, backup-first semantics unchanged; readonly previews unchanged.
- Synthetic code tests +13: `tests/test_store.py` +6, `test_import_local.py` +3, `test_cli_safe.py` +2, `test_profile_workflow.py` +2. Current GitHub test declaration count **212 methods/15 modules**, not verified executions.
- Isolated `python` sqlite3 temporary-file check 4/4 PASS for URI mode=rw no create, unchanged missing path, empty version 0, and os.replace differing dev/inode/size/time tuple. NOT authentic integrated GitHub 212 suite.
- New doc `backend/DB_FILE_SAFETY.md`, README and status/handoff/next/start updated. Feature started HEAD `dd6536cd9be340e503deb92e030405b8c9ab9d0e`; fetch final SHA and verify main remains `c888c795bef72734f3f7016e54013b82453f11d8`. Only feature commits.

**Limitations & safety:** No cross-process exclusive lock, inode collision/reuse and post-open path changes are not fully stopped. SQLite writer still runs multi-stage operations in separate transactions and retains backups rather than auto-restores. No malicious DB tampering authentication. Browser still localhost read-only. Real Windows cleanup locks 18 errors on 137-case P2-10 old run not proven fixed by rerun. No Windows GUI, real PDF font/Excel or benchmark execution in P2-18. No app installer, official procurement PRO or opt-in AI PREMIUM; full product prior estimate ~42% subjective (not measured).

**Next P2-19:** user-friendly backup validation and safe restore plan, optional controlled local restore only after separate backup of active DB and explicit approval. Prioritize avoiding customer data loss, no silent overwrite. Then native Windows installers, 212 suite and browser/PDF/Excel/10k authentic QA (approved local or other authorized no-fee mechanism). Do not ask user to do repeated QA. Handoff stays in GitHub for new chat.

---
## Earlier HANDOFF history

# BID OWL HANDOFF — P2-17 legacy CLI upgrade and next P2-18 (2026-10-27 KST)

**User intent:** `ㄱ` means autonomous GitHub source work; user has objected to repeated manual ZIP download and Windows test requests. Private repo `hibi89/Bid_Owl` branch `feature/bid-owl-v1-basic-mvp` only; main and legacy Vercel protected. No paid runner, external customer file transfer, public deploy or real APIs without approval.

**P2-17 actual changes:** `backend/cli.py` old CSV -> SQLite -> XLSX/PDF workflow had NO existing DB backup, and `save_profile(company)` could implicitly update saved company content. Replaced with (1) PDF font preflight if used, strict CSV and 64KiB company JSON validation, source ID guard, complete validation before writes; (2) existing DB readonly `viewer.open_database` schema/profile preflight, same-ID profile exact-match check; (3) new DB exclusively reserved `open('xb')`, existing DB consistent non-overwriting backup via `BidOwlStore.backup_to(_new_backup_path)` BEFORE any DDL/DB mutation; (4) after backup, additive `assessment_engine_provenance` table migration for old v1 DB, never retroactive stamp old assessments; (5) version-pinned company profile creation/new assessments (`expected_version=0`, `expected_profile_version`); (6) XLSX/PDF report export compatibility preserving historical fixture CSV through `cli.py`, without using GUI importer which rightly refuses synthetic DEMO- data; (7) result JSON reports `backup`, and any failure after modifications reports `CLI_PARTIAL_OR_UNCERTAIN` and preserves backup. Main catches sqlite3 errors into FAILED JSON code 2.
- New `backend/tests/test_cli_safe.py`: **9 test methods defined** for new DB hashed provenance, second-run backup of original state, old v1 migration only post-backup, changing company refused prewrite, backup failure, report writer error + backup retained, foreign/invalid DB not clobbered, new file race, JSON DB error handling. All synthetic tempfiles.
- Updated `backend/README.md`, `backend/ENGINE_POLICY.md`, `NEXT_TASK.md`, `STATUS.md`, `HANDOFF.md`, `START_HERE.md`.
- Current total **199 Python test_* methods in 15 modules** read from GitHub; this is a count of test source, NOT actual suite result. Authenticated current source checks verified backup call before SQL change, readonly preflight, version pinning, SQLite errors covered. Last authentic Windows user test 137 ran, 18 WinError32 temp DB cleanup errors; no native rerun. GitHub Actions feature branch had 0 observed runs; no CI PASS. No full private repo local execution via model container.
- P2-17 starting feature SHA `8ac132d79bcfa7566a2d59046c3da37e079c6055`; main initial SHA `c888c795bef72734f3f7016e54013b82453f11d8`, unchanged. Fetch final feature HEAD after these docs; never guess current SHA.

**Remaining limits & next P2-18:** Existing DB may be deleted/replaced after readonly check but before `BidOwlStore` opens it, which could auto-initialize a blank DB even though the caller expected an existing v1. Add optional strict existing writer mode SQLite URI `mode=rw` and schema-v1 requirement without auto-initialization; use it for pre-existing paths in `cli.py` and `import_local.py` (and profile_workflow if viable). Add tests protecting foreign/vanished DB and race scenarios. No full cross-operation atomicity; backups preserved for manual restore. Real user CSV GUI/PDF/Excel, Windows installer, browser, 10k, source-packaged rule fingerprint, legal trademark/KIPRIS and sale readiness still pending. Product prices historically proposed BASIC 59k, PRO 149k, PREMIUM 299k KRW; none market validated, PRO and PREMIUM not implemented. Existing subjective total ~40%. Do not make user run routine QA.

---
## Previous handoff history

# BID OWL HANDOFF — P2-16 completed as source, next P2-17 (2026-10-27 KST)

## Continuation and user instruction
User `ㄱ` = autonomously implement on PRIVATE `hibi89/Bid_Owl`, `feature/bid-owl-v1-basic-mvp`, inspect latest GitHub heads/source and NEXT_TASK/STATUS/AGENTS/REQUIREMENTS/START_HERE. User firmly dislikes repeated manual ZIP/PowerShell tests. No changes to main, old Vercel, paid services or exposure of user/local customer data/API keys.

## P2-16 exact work
1. New `backend/bidowl/engine_identity.py`: `engine_fingerprint()` SHA-256 over files eligibility.py, schema.py, profile.py, store.py with names + lengths. No customer input or external calls. Source unavailable: raise, fail-closed; packaged EXE must bundle these files or use verified manifest in future.
2. `backend/bidowl/store.py`: fresh SQLite v1 creates additive `assessment_engine_provenance` table with assessment ID FK and engine_hash. `assess_and_record` computes current fingerprint pre-transaction; inserts hash atomically alongside immutable assessment/rule evidence when metadata table exists. Hash insert failure rolls back whole assessment; older DB with no table does NOT get silently mutated by open/write.
3. `backend/import_local.py`: existing v1 DB backed up first; then CREATE TABLE IF NOT EXISTS. `_reusable_assessment_status` joins latest assessment provenance and requires hash == runtime SHA (plus same bid/profile revisions, expiry flag). Unknown/old hash causes new assessment and preserved old history. `--force-reassess` still optional. Fresh missing source files cause failure before writing.
4. `backend/profile_workflow.py`: after mandatory successful backup, create optional metadata table in legacy DB, new reassessments hashed. No metadata before backup; no backfill of old PASS.
5. `backend/viewer.py`: readonly query detects whether provenance table exists; missing table/hash or changed engine => current `UNKNOWN` and human-review reason; `snapshot_status` retains historical PASS/FAIL. Missing engine source => viewer UNKNOWN instead of false PASS. Additional guard prevents a missing source hash and missing DB hash (both None) from comparing equal and incorrectly showing PASS. No HTTP write route.
6. Synthetic tests: `backend/tests/test_engine_identity.py` (+3), `tests/test_import_local.py` (+2), `tests/test_viewer.py` (+4), `tests/test_store.py` (+2), `tests/test_profile_workflow.py` (+1). Total current verified remote definition count **190 across 14 files**, NOT 190 PASS.
7. Docs `backend/ENGINE_POLICY.md` and `backend/IMPORT.md`, NEXT_TASK, STATUS, HANDOFF plus pointers updated.

## Verification evidence
Live code fetched from GitHub: conditional viewer JOIN syntax, old v1 schema avoidance, backup-then-DDL, policy hash on write and compare on reuse. Ran only a separate **3/3 synthetic in-memory sqlite3 SQL contract** in author environment (viewer no-provenance, viewer provenance, reuse join), not exact private GitHub suite. No actual integrated 190 tests, Windows GUI, browser, Excel/PDF, packaging or 10k performance execution verified this iteration. Earlier user Windows P2-10 run had 137 Python cases, 18 WinError 32 cleanup errors; P2-11 code fixed SQLite connection closes but not remeasured. Do not claim full PASS.

## Product and stage
BID OWL BASIC planned KRW 59k CSV profile snapshots Excel/PDF seven theme offline read-only browser; PRO planned 149k official government API using customer's own key; PREMIUM planned 299k opt-in AI and profitability. Pricing, brand KIPRIS, native installer, official procurement integration and sales eligibility unverified. Overall previous completion guess ~40% remains subjective. No external deployment/customer data/payment. GitHub repository ID 1399359397, main preserved baseline `c888c795bef72734f3f7016e54013b82453f11d8`. Feature branch was `b392983ccd5ef36bc27a8bdcf98dd5a82b5376fe` before P2-16; after writing HANDOFF verify newest SHA and main, author and compare.

## Next P2-17
Improve `backend/cli.py` compatibility with metadata on old v1 DB: existing CLI lacks backup on mutate, so must add explicit safe prewrite backup before upgrading legacy DB, or use safe readonly importer; no silently writable browser. Also improve guided backup restore/report workflow while maintaining immutable evidence and fail-closed rule engine policy. Real Windows 190-suite + native Excel/PDF/browser is a release blocker, not routine user task. `ㄱ` goes next.

---
## Earlier P2-15 and prior historical handoff

# BID OWL HANDOFF — P2-15 idempotent local eligibility decisions, 2026-10-27 KST

## 1. Project and user workflow
Private `hibi89/Bid_Owl` is Windows-local SME Korean procurement pre-screening; BASIC CSV+company profile+SQLite+conservative PASS/FAIL/UNKNOWN+evidence+local viewer/XLSX/PDF, PRO planned official procurement API via customer's key, PREMIUM optional AI/profitability, Windows installer and sales gating. Working branch **feature/bid-owl-v1-basic-mvp**. User has said they do NOT want repeated ZIP/PowerShell QA chores. Each ㄱ authorizes autonomous GitHub source/docs/testing work; do not ask for routine manual tests. No main/demo/Vercel changes, private customer files/keys uploads, paid third-party runners, unsolicited public deployment.

## 2. P2-15 implementation and files
- `backend/import_local.py`: Adds `_reusable_assessment_status(store, source_id, bid_no, profile_id, profile_version, is_expired)` with bound SQL that selects latest matching saved assessment for that specific source/bid/company. Reuse only if saved assessment's bid_version equals current bid latest_version, saved profile_version equals known profile current_version, status is PASS/FAIL/UNKNOWN and saved `is_expired` equals actual current deadline condition. If profile.latest_version changed mid-import compared to known version, raise before returning stale reuse. On mismatch or no assessment, call existing `store.assess_and_record(...,expected_profile_version=...,checked_at=...)` and store new immutable snapshot; count both fresh/reused. Does not overwrite historical assessments.
- `apply_import(plan, force_reassess=False)`: New optional explicit full reevaluation. GUI Tkinter Checkbutton "저장된 판정도 모두 재평가 (규칙 엔진 업데이트 후 권장)" and CLI `--force-reassess` with `--apply`. GUI completion message shows fresh/reused counts. Return `assessments_saved` means newly saved only; `assessments_reused` counts unchanged reused saved snapshots; eligibility_counts includes all CSV bids. Existing DB still takes exclusive SQLite backup before modifying import audit or assessments on EVERY import, even no-op. New DB still reserves exclusive path and creates new profile with CAS.
- `backend/tests/test_import_local.py`: +8 tests (18→26) for unchanged repeated import preserving IDs/zero new assessments, one revised bid gets one new assessment, expiry crossing gets one new assessment, changed-then-restored profile revision v3 invalidates old snapshots, mid-import profile version drift fails and retains backup, forced regen, nonbool flag, CLI --force-reassess.
- `backend/IMPORT.md`: reuse conditions, response semantics, manual force note and corresponding command.
- `STATUS.md`, `NEXT_TASK.md`, `START_HERE.md`, `HANDOFF.md`: refreshed with exact caveats and next step.

## 3. Measured evidence vs remaining unverified
Actual isolated Python sqlite3 SQL contract test: **4/4 PASS** on synthetic in-memory DB (status reuse, expired flag mismatch, bid_version mismatch, and changed latest company revision raising). This tests SQL shape/guard, not a running authentic checked-out project or current full tests. Authenticated GitHub source fetched/read back and direct SQL/conditional code inspected, no new web frontend JS modifications.
Remote GitHub inventory **178 declared Python test methods in 13 files**, not 178 PASS; no current checkout entire suite, GUI, Windows report/Excel/PDF, live customer data or 10k benchmark actually executed. Historical user test was 137 actual cases/18 WinError32 temporary SQLite cleanup errors/119 without errors/0 assertion failures in older code. P2-11 patched underlying leak and P2-12 added regression, but no authentic native Windows rerun. Do not state Windows failure resolved or product sale-ready. No actual customer data used in this stage.

## 4. Safety caveat
**IMPORTANT P2-16 BLOCKER: the eligibility rules ENGINE VERSION is NOT stored or compared.** A code upgrade can change evaluation even when bid/profile revisions and deadline remain identical, so cached old PASS may be logically stale. Current UI/CLI offers **manual force-reassess**, and docs instruct to select it after software/policy upgrades, but **automatic version invalidation remains unimplemented**. P2-16 should solve this before commercial release: engine fingerprint/version per reused assessment, backward compatibility with schema v1, older provenance-less assessments should be invalidated (re-evaluated), and initial backup BEFORE modifying an existing DB. Avoid migration corrupting old data or silently altering historical evidence. Design could use additive table created only after backup, or store-level versioned migration, but must preserve full history. Regression tests for old baseline and upgraded engine required.

## 5. Repo/commit identity, originals and production URL
Private repo `hibi89/Bid_Owl`, id 1399359397. P2-15 began feature SHA `04b92e44faa0ec2e9197c7e6c0c53e2e30b5e05a`; key commits include `2476c8633626d7ac437748b6537023a44b45f11e` reusable logic; `6a211aae258a9d0631c473962f2421df5dd5951d` tests; `fc25209fc5840a1464ea08fc5cae6f211cd7001f` profile revision drift; `ebff848a40e3d241758a4d784d3b5381cfeea214` drift regression; `58b4df019bae47235f7e09eb8219607d1a96004a` force GUI/CLI; `2f8fcc57d70dd4811323fd3461263a5f482f806f` flag tests; `b9389d5ee54e20289d53ae106a05cb32166b8ec5` docs; later STATUS/NEXT_TASK/START_HERE and this document. After this HANDOFF commit, query **live** final feature SHA, main SHA and compare file list, author/committer. Protected main last `c888c795bef72734f3f7016e54013b82453f11d8`; original 2025 static BID INSIGHT school demo and Vercel project project08-bid-insight/prj_YcrN7OdOjKl6M457HelGIItLeeXZ unchanged.
New Python BASIC app is not deployed publicly. Existing localhost viewer `python viewer.py --db ./demo.sqlite3 --port 8765` binds 127.0.0.1 readonly, UI no write route. Separate root launchers `START_BID_OWL_DEMO.cmd` (fake only), `START_BID_OWL_IMPORT.cmd` (user CSV with explicit confirmation); local run details in backend/DEMO.md and IMPORT.md. No externally reachable product URL/new production build. No uploaded API secrets/data/fonts or customer documents, no fee incurred.

## 6. Completion/next actions
Current user-facing subjective whole BASIC+PRO+PREMIUM+installer+safety+sale progress estimate **around 40%**, not an audited work-breakdown or test pass ratio. BASIC first-run and assessment cache improved, but code is not commercial release-ready.
Next user ㄱ = P2-16 automatically: build safe engine-version-aware invalidation for cached assessments (latest code version), preserve source/provenance, apply backup-first additive marker or migration, add tests. Secondary safe backup inspection/restore plan and native Excel/PDF/report UX. Do not ask user to run source tests; continue source changes with honest static/isolated checks and note final Windows QA release gate.
 
## 7. Earlier history
Historical P2-14, 13, 12, 11 handoffs are appended below for preservation. The latest source/checkpoint is this top section.

---

# BID OWL HANDOFF — P2-14 real local CSV/company onboarding · 2026-10-27 KST

## 1. User goal, product and decision authority
The user's minimal `ㄱ` means continue development in connected private GitHub **without repeatedly asking them to download a ZIP and run Windows PowerShell**; user previously objected to those manual steps. The user approves ordinary project development/commits, not public deployment, paid services, private customer data transfer or main rewrite. Project BID OWL / 비드아울: local-first Windows procurement screening, BASIC planned KRW 59,000 CSV, company rules PASS/FAIL/UNKNOWN with original evidence, versioned SQLite, readonly local UI, XLSX/PDF; PRO planned KRW 149,000 customer-key official procurement API and PC-on sync; PREMIUM planned KRW 299,000 optional external AI/profitability. Prices, real legal correctness and brand/KIPRIS not verified. The P2-13 one-click synthetic demo is SEPARATE from real customer DB.

## 2. New P2-14 code, files and behavior
- New `backend/import_local.py` (stdlib, no ReportLab/API required): `ImportPlan`, `prepare_import`, `plan_summary`, `apply_import`, `run_gui`, `main`. For real user CSV+company profile, validates bounded 10 MiB strict CSV via `bidowl.parse_csv(...).require_valid()` and validated CompanyProfile, source ID <=300, refuses fake `DEMO-` and `DEMO_ONLY` and `SYNTHETIC-` company and reserved demo source ID. `prepare_import` uses SQLite `viewer.open_database` **mode=ro** and full schema checks for an existing DB, checks existing company's stored profile match; any differing same-ID profile must go to explicit CAS-backed `profile_workflow.py` editor. Readonly preview creates no DB or backup.
- `apply_import(plan)` rechecks raw CSV SHA256 + <=10 MiB, existing DB presence/profile version/content; for NEW DB `path.open('xb')` reserves exclusively (avoids another process creating file between readonly preflight and sqlite3.connect), for EXISTING DB `BidOwlStore.backup_to` first creates an exclusive consistent backup under `db.parent/backups/<db>_<UTC>_<random>.sqlite3` **before any mutation**. Creates profile using `save_profile(...,expected_version=0)` if new, preserves identical profile unchanged if existing, imports all bids under source ID with file digest/versioning, records one new assessment per imported bid with `expected_profile_version` guard. Accurate inserted/revised/unchanged and PASS/FAIL/UNKNOWN counts, original evidence saved. Import/profile/assessment are separate transactions, so postwrite errors report `IMPORT_PARTIAL_OR_UNCERTAIN` with preserved backup, never pretend atomic or auto-restore. New DB has no prior backup; a partially initialized new file can remain after failure. Browser HTTP remains readonly.
- CLI `python import_local.py --csv FILE --profile JSON --source-id ID [--db PATH]` **preview-only** by default; `--apply` explicit save. GUI when invoked no CLI args: Tkinter chooses CSV, company profile fields (or import existing JSON), validates before confirmation, asks user in native messagebox, applies and optionally opens readonly viewer on loopback random port. Missing numeric fields -> None UNKNOWN, NOT zero/PASS. GUI form may be unresponsive during large imports (not yet performance-verified).
- New Windows double-click launchers `START_BID_OWL_IMPORT.cmd` at root and `backend/START_IMPORT.cmd` in backend; Python py -3 fallback to python, no payment/install service/API. Prior `START_BID_OWL_DEMO.cmd` remains disposable fake-only.
- New `backend/tests/test_import_local.py` **18 declared test methods**: readonly dry run, real-like synthetic temporary fixture first import, SQLite profile/rule assessments, fresh existing DB backup and repeated import unchanged version, profile conflict refusal, bad CSV/foreign DB/demo refusal, bounded source/profile, preview-to-apply CSV/profile race, new DB exclusive-create race preserving competitor file, error preserves backup, unknown company field semantics, CLI preview vs --apply, GUI launcher paths/no HTTP write. Test fixtures derived from packaged dummy bid CSV with changed fake identifiers and `source_ref=SYNTHETIC_TEST`, NEVER actual customer data.
- New `backend/IMPORT.md` details GUI/CLI usage, safety limitations. Root `README.md`, `backend/README.md`, `START_HERE.md`, `NEXT_TASK.md`, `STATUS.md`, `HANDOFF.md` updated.
- After new +18, authenticated GitHub inventory **13 test modules / 170 declared Python methods**. This is a static test count, NOT 170 PASS. Source inspected for readonly preflight, exclusive reservation, backup before writes, CAS, no do_POST in new importer.

## 3. Evidence: actual tests vs unverified
New code read back through GitHub connector and checked structural guards. **Did not execute current entire Python 170-case suite, new Tkinter GUI, new import CLI, native Windows installer, 10k performance or Excel/PDF** in this tool session; private GitHub checkout could not previously be mounted in assistant Python environment due DNS/auth. Do not call source inspection a real runtime PASS. User's prior authentic Windows P2-10 test on older source: 137 tests executed in 7.237 s, 119 without error, 18 `PermissionError [WinError 32]` temporary SQLite locks, zero assertions FAIL, JS syntax PASS, downstream smoke/benchmark skipped. P2-11 fixed observed leaked backup and test connections; P2-12 added AST and platform-independent handle tests; no new full Windows run since. There is no known authentic 170/170 PASS. No user work requested in this iteration.
P2-13 latest ui.js V8 parse had PASSED, **P2-14 does not modify ui.js**.

## 4. Branch, commits, originals and current status
Private `https://github.com/hibi89/Bid_Owl` (repo ID 1399359397), work **feature/bid-owl-v1-basic-mvp**. P2-14 starting HEAD `7718f34b1398d9e9309cd82a9dcb2e761778c7e7`. Main original educational static `c888c795bef72734f3f7016e54013b82453f11d8`, legacy backup SHA `2807a93a3e0deba98840712401fdd6025e6f5610`. No main/Vercel or public deployment changes. Key feature commits: `63e9050724d75d1c6c607bfba15321c5c717d6cb` import_local.py, `c40dd53c6eaa83419ce7ce8f97bdff41e7f42fa5` backend Windows launcher, `490f2f5a276e7a3d9727a69c750cffe6f8463264` root launcher, `0c5ae37ecce4ae4f4639b2ef71c9be0ada756312` importer tests, `e2c7cb8ee8a3d76d2196a687445719fdf118970b` input guard, `f029d21bd8c6356be425365d6b7846322326e9cb` additional guard tests, `636c26ccdab4f9ff1a0c5f92880732eb4180305f` exclusive DB reservation, `9b25ad59e4d5d3354c3b27388a4d198f71cda524` exclusive race test, `57c05947b26b4af1e3ba4baca8e1245417cb657a` importer docs; later README/START_HERE/status etc. After this HANDOFF update, **fetch final HEAD/main SHA, author/committer and compare changed file list**, do not guess.

## 5. Privacy, safety, backups and production
No customer CSV, SQLite, report, PDF/XLSX, key, .env or fonts were accessed/uploaded to GitHub; all code and mock tests only. Existing DB backup is local, exclusive and source versioned; manual inspection/restore only, no silent overwrite. Unknown qualification never converted to PASS by missing company data. Desktop registration uses OS GUI and readonly localhost viewer; no POST write endpoints or external network. No paid service, official API, production deployment or public sale. Old Vercel school demo (project08-bid-insight/prj_YcrN7OdOjKl6M457HelGIItLeeXZ) untouched. Local URLs dynamic `http://127.0.0.1:<random_port>/`; new Python app not publicly hosted. KIPRIS trademark clearance outstanding.

## 6. Approx completion and autonomous P2-15 next
Earlier overall BASIC+PRO+PREMIUM+installer/sales subjective completion estimate **~35%**, not objectively recomputed by this implementation, despite improved BASIC first-run usability. Not sale-ready: full actual Windows 170 test execution, native GUI, Excel/PDF Korean font, customer CSV schema reality, 10k speed, safe backup restore, installer/security, legal name and sales confirmation pending.
P2-15 next: improve **idempotent/skip redundant same-bid assessments** when existing source version and profile version unchanged; current importer always writes a new assessment for each row, including unchanged. Preserve historical evidence and evaluate with correct profile version. Add regression tests and backup/recovery/first-use report UX. Or other most valuable safe BASIC source task, without asking user to manually run Windows tests. Never merge main/deploy or use paid third-party CI without approval. Keep explicit truth boundary.
 
## 7. Resume instruction
2026-10-27 KST, next user `ㄱ` or `[Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]` = read latest GH source and docs, implement P2-15 autonomously, commit and report real SHA + verified vs unverified. Earlier historical handoffs appended below.

---

# BID OWL HANDOFF — P2-13 local synthetic demo, 2026-10-27 KST

## 1. User goal / permissions / product specification
Private local-first BID OWL, SME public-procurement eligibility screening product: BASIC planned KRW 59,000 (validated CSV, company profile, versioned local SQLite, PASS/FAIL/UNKNOWN with source evidence and human confirmation, local web UI/seven themes, Excel/PDF); PRO official government procurement API using customer's key, planned 149k; PREMIUM optional AI/profitability, planned 299k. Prices and brand clearance unvalidated. The user wants AI to handle development, GitHub commits, tests and docs autonomously, **not repeatedly require user ZIP downloads/PowerShell QA**. Never claim real-world legal authority or real tender data for a synthetic demo.

## 2. New P2-13 code / files
- `backend/demo_local.py`: new Python 3.11+ offline disposable localhost demo. `create_demo_database(path)` requires previously nonexistent destination, reads only packaged `backend/fixtures/sample_bids.csv` and `sample_profile.json`, checks every bid ID starts `DEMO-` and provenance `DEMO_ONLY`, company ID starts `SYNTHETIC-` **before** making DB; stores 2 synthetic bids, profile and eligibility snapshots under source ID `BIDOWL_SYNTHETIC_DEMO`. `serve_demo(port=0, open_browser=True)` uses `tempfile.TemporaryDirectory`, existing `viewer.make_server` binding exclusively 127.0.0.1, ephemeral port, optional default browser; `--no-browser` and `--port` developer flags. Normal Ctrl+C closes HTTP server, temp DB cleaned; abnormal termination may leave OS temporary files. No default customer DB or external API/AI, no ReportLab/font needed just to view. Never overwrites existing file.
- `backend/START_DEMO.cmd` and root `START_BID_OWL_DEMO.cmd`: Windows double-click from repo top level; `py -3` if available else `python`; keeps error visible if startup fails.
- `backend/ui/index.html`, `backend/ui/ui.js`, `backend/ui/ui.css`: synthetic warning banner (hidden by default for real user DB; revealed if `BIDOWL_SYNTHETIC_DEMO` source appears in loaded list); seven-theme CSS token-compatible; no new writable HTTP endpoints and no user HTML injection.
- `backend/tests/test_demo_local.py`: 8 fresh isolated methods, real SQLite contents, input/provenance refusal before writes, root launcher, read-only localhost HTTP, fake server + TemporaryDirectory cleanup, invalid ports. 12 test files now define **152** Python test methods total. This is source/test-count, not execution PASS.
- `backend/DEMO.md`: full user safety, execution and source/QA limits.
- root `README.md`: new product vs old 2025 BID INSIGHT static demo disambiguation; `backend/README.md`: quickstart. `START_HERE.md`: current stage not stale P1. `STATUS.md`, `NEXT_TASK.md`, `HANDOFF.md` refresh.

## 3. Verification / evidence boundary / failure history
Authenticated GitHub source fetched. V8 `new Function(exact ui.js)` verified **JS syntax PASS** after adding banner, not browser rendering/behavior. Source inspected for synthetic marker, existing-file guard, tempfile context, local read-only make_server route, 8 test method declarations. Full Python 152-case suite **NOT executed** in assistant environment, and Windows double-click not run. Do not claim 152 PASS, native Excel/PDF, demo server integration pass or 10k timings. Earlier user's actual P2-10 Windows CPython3.11/ReportLab4.5.1 run: 137 tests, 119 without error, **18 WinError32 file-handle cleanup ERROR, 0 assertion FAIL**; JS syntax PASS; dependent smoke/benchmark SKIP. P2-11 fixed observed source-level leaked SQLite connections; P2-12 added source-level AST guard and QA independent stages, but no new authentic Windows test after those fixes. Current private repository cannot be mounted in model Python container due previous auth/DNS; do not run a partial stand-in and call it full suite. The demo uses only local generated synthetic fixtures and does not access customer DB; browser is still read-only.

## 4. GitHub branch, commits and protected originals
Repo private `hibi89/Bid_Owl` ID 1399359397; branch `feature/bid-owl-v1-basic-mvp` started at `6a7d1369c255936c01eaf6f1e51eed4720635c2a`. Source commits include `7a8f982765360b5ef73e6b699f5874066c8708a0` demo_local.py; `a34fd12b44d6026d8b8673be2a9b114a9c56530d` backend launcher; `52b78b964c6a573a6db5eb9218d4cbb532a33a60` HTML; `fb2ccb6894896e49b04dca935dd4c02d0b39eb6c` JS; `63670c0fd7754d03bf473bbc9cfe0d7f8c275154` CSS; `01826bc81eb5e6e831b4abb4ae469efadf553efe` 8 tests; `0defe140556525ece28aef09c59486ab1c69d733` root launcher; `466ef719efaaf37e3df1d9bf185aec5a7e15d486` test root path; `5cc6554c4cb3bbcccca6a5ef3f1402e3b7b177ba` DEMO.md. Docs commits follow; final feature HEAD after HANDOFF must be fetched, main must remain `c888c795bef72734f3f7016e54013b82453f11d8` with school static/Vercel untouched, author/committer hibi89.
No customer SQLite/CSV/report/PDF/XLSX/.env/keys/fonts uploaded, no fee/API/deployment or permission changes.

## 5. Launch and production state
New Python product **not publicly deployed**. From full authorized developer checkout on Windows user can double-click `START_BID_OWL_DEMO.cmd` in top-level branch folder, or run `python demo_local.py` from backend; URL auto localhost `http://127.0.0.1:<random_port>/`. Ctrl+C for normal shutdown; temporary DB is demo-only. Browser banner states fictional bids and no real data. Existing separate real SQLite viewer `python viewer.py --db <explicit-file> --port 8765` is read-only and CLI import/report/profile remains explicit. Former school Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched and not used by this Python product. No browser/native Windows visual test completed.

## 6. Completion and next work
Previous subjective estimate entire BASIC+PRO+PREMIUM+packaging ~35%; no formally measured recalculation. BASIC one-click temporary demo improves exposure, but **real** customer CSV import, profile editing and PDF remain CLI-assisted and installer/security/final Windows QA pending; not sellable yet.
P2-14: autonomous source implementation of safe real BASIC first-run (offline explicit customer CSV/profile path selection and import/preflight, never write without backup/CAS, never mix demo DB). Avoid exposing write endpoints in local HTTP without threat modeling, CSRF/Origin/Host and approval. Add isolated tests; keep fail-closed UNKNOWN and immutable evidence. P3 PRO user-key official API, P4 PREMIUM opt-in AI, packaging/name KIPRIS/sales only later. Do not request routine user QA/download on ㄱ.
 
## 7. Last instructions
This turn: GitHub changes plus V8 JavaScript syntax check; **152 declared / no 152 execution**. After HANDOFF write check main/feature and committer identity, changed paths. Next chat `[Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]` or `ㄱ` continues P2-14. Earlier detailed P2-12/11 handoff appended below for history.

---

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
