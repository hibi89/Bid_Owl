# P2-23 — 공고 마감 상태 변경에 따른 판정 무효화

저장된 규칙 평가가 공고·회사·엔진 버전과 같더라도, 평가 당시 마감 여부와 현재 마감 여부가 달라졌으면 **PASS/FAIL을 현재 판정으로 재사용하지 않음**. 목록·상태별 필터·공고 상세 모두 UNKNOWN과 재판정 안내를 표시합니다. 과거 스냅샷/근거는 보존합니다. 테스트용 SQLite도 실제 v1 스키마의 `is_expired` 필드를 맞췄습니다. [VIEWER_QUERY.md](VIEWER_QUERY.md)에 자세한 계약을 기록했습니다. 실제 전체 Python 248개 테스트 및 Windows 실사용 재검증은 미완료입니다.

---

# P2-22 — 상태별 조회 백엔드 최적화

BID OWL 공고 목록의 PASS·FAIL·UNKNOWN 필터를 기존 메타데이터 우선 경로에 통합했습니다. 한 번에 공고 200건씩 판정의 **공고·프로필·규칙 엔진 현재성**만 검사하고, 해당 상태로 필터링한 뒤 요청 페이지의 최대 100건만 상세 조회합니다. SQL은 안전한 파라미터 바인딩을 사용하고 구형 DB의 근거 부족 판정은 UNKNOWN으로 유지합니다. 전체 기준과 보수적 판정은 [VIEWER_QUERY.md](VIEWER_QUERY.md). 실제 Windows 전수 테스트와 최종 1만 건 통합 성능 검증은 아직 안 됐습니다. 프론트엔드 미관 작업은 사용자 지시대로 계속 보류합니다.

---

# P2-21 — 공고 목록 조회 백엔드 최적화

일반 목록·키워드·카테고리·마감일·관심 공고 검색에서 전체 공고의 평가 이력을 조회하던 경로를 개선했다. 가벼운 공고 메타데이터로 필터/정렬/페이지를 먼저 선택한 후 해당 페이지(최대 100건)의 자격 판정/근거를 일괄 조회한다. 기존 Unicode 검색·정렬·UNKNOWN 우선 정책은 유지하고 **상태별 필터는 검증 전까지 기존 경로 유지**. [VIEWER_QUERY.md](VIEWER_QUERY.md) 참조. `benchmark_local.py --compare-full-scan`은 기존 방식과 새 방식을 동일한 합성 DB로 비교하는 선택형 성능 측정기다. 현재 실제 Windows 10k 통합 성능 측정은 미완료. 프론트엔드 디자인은 계속 보류.

---

# P2-20 — 복구 데이터 전체 내용 검증

백업 복원은 이제 건수 외에 모든 공고·회사·버전·판정·규칙 근거의 `evidence_sha256` 지문을 비교합니다. 소스 파일을 읽는 중 WAL/SHM 사이드카가 생긴 경우도 차단합니다. [RECOVERY.md](RECOVERY.md) 참조. 백업+복원 성능 측정은 `python benchmark_local.py --records 10000 --assessed 200 --with-recovery`로 선택적으로 실행하도록 구현했습니다. 전체 애플리케이션의 실제 1만 건 성능 측정은 아직 완료되지 않았습니다. 프론트엔드 디자인은 사용자 지시대로 보류합니다.

---

# P2-19 — 로컬 SQLite 백업 검사 및 안전한 복구

`backup_recovery.py`는 기존 DB와 백업을 덮어쓰지 않는 **새 파일로의 복원**을 제공한다. 기본은 읽기 전용 미리보기(무결성·외래키·스키마·건수·해시 검사), `--apply`를 붙여도 복구된 DB의 자동 활성화/원본 교체는 없다. 실행 및 위험 한계는 [RECOVERY.md](RECOVERY.md) 참조. 전체 Python 226개 테스트는 정의 상태일 뿐 실제 전수 통과하지 않았다.

**사용자 지시: 프론트엔드 디자인은 보류. 이후 작업은 백엔드 우선.**

---

# P2-18 — 기존 DB의 삭제·교체 감지 및 안전한 열기

CSV 등록·회사 편집·구형 CLI는 기존 로컬 SQLite 파일을 열 때 `mode=rw`(없으면 생성 금지)로 연결하고, 미리보기에서 확인한 파일 식별값이 실제 쓰기 시점과 같은지 검사하도록 보강했습니다. 신규 DB는 `xb`로 예약한 파일만 초기화합니다. 구체 동작과 **파일 잠금이 아닌 best-effort 한계**는 [DB_FILE_SAFETY.md](DB_FILE_SAFETY.md). 전체 테스트·Windows 원본 DB 교체 검증은 미완료입니다.

---

# P2-17 — 기존 CLI의 안전한 백업·규칙 엔진 지문 처리

기존 `python cli.py --csv ... --profile ... --source-id ... --output ...` 경로도 이전 DB를 **변경하기 전에** 읽기 전용 검증과 자동 백업을 수행하도록 수정했습니다. 이전과 달리 같은 ID의 회사 프로필 내용이 다른 경우 자동 덮어쓰지 않고 `profile_workflow.py` 사용을 안내합니다. 기존 v1 DB의 규칙 지문 메타테이블도 백업 성공 후에만 추가하며 새 평가에 SHA-256 엔진 지문을 저장합니다. 반복 실행 시 XLSX/PDF 보고서는 새 평가 스냅샷과 별도 파일로 남습니다.

기존 CLI는 개발/합성 CSV·보고서 호환성을 위해 샘플 `DEMO-` 데이터도 명시적으로 사용할 수 있지만, **실제 회사 파일 입력**은 `START_BID_OWL_IMPORT.cmd` GUI 또는 `import_local.py`를 우선 권장합니다. CLI에 대한 테스트는 실제 Python/Windows 실행 전이므로 상용 안전성 확정은 아닙니다. 백업 경로는 성공 응답 JSON `backup` 필드로 보고되며, 부분 실패는 `CLI_PARTIAL_OR_UNCERTAIN`을 반환하므로 백업 및 DB/생성된 보고서를 확인한 뒤 재실행해야 합니다.

---

# P2-16 규칙 엔진 변경 감지와 구형 DB 보수적 판정

새 판정에는 로컬 엔진 소스 SHA-256 지문을 저장합니다. 구형 또는 다른 엔진으로 평가된 PASS는 현재 조회에서 UNKNOWN으로 보이며, 새 등록/재평가 시 기존 DB 백업 후 자동 갱신됩니다. 자세한 처리·제한은 [ENGINE_POLICY.md](ENGINE_POLICY.md). **전체 Python 190개 정의 테스트 및 Windows 실사용 통과는 아직 미검증입니다.**

---

# BID OWL BASIC — 실제 CSV와 회사 정보 간편 등록 (P2-14)

Windows 개발 브랜치 폴더 최상위 **`START_BID_OWL_IMPORT.cmd`**를 더블클릭하면 로컬 Tkinter 회사 정보/CSV 등록 화면이 열리도록 구현했습니다. CSV와 회사 정보의 미리보기·입력 검증 뒤 명시적 승인을 받아 DB에 저장합니다. 기존 DB는 수정 전에 별도의 덮어쓰지 않는 백업을 생성하며, 프로필 내용이 바뀐 경우 묵시적으로 덮어쓰지 않습니다. 자세한 실행·실패 대응은 [IMPORT.md](IMPORT.md). **Windows GUI와 전체 Python 회귀 테스트 실제 실행은 아직 미확인입니다.**

---

# BID OWL BASIC — 오프라인 합성 데모 (P2-13)

Windows에서 개발판 압축을 풀었다면 저장소 최상위 `START_BID_OWL_DEMO.cmd`를 더블클릭하여 **가상 공고 2건만** 보는 임시 로컬 체험을 시작할 수 있습니다. Python 3.11+ 외에 ReportLab이나 API 키는 필요 없습니다. 브라우저가 자동으로 열리며 콘솔 Ctrl+C로 종료합니다. 데모는 실제 고객 DB를 사용하지 않으며 원본 입찰공고가 아닙니다.

명령줄로도 `python demo_local.py`를 실행할 수 있습니다. 세부 제한·정리·검증 상태는 [DEMO.md](DEMO.md) 참조. 아래 CLI 설명은 실제 프로젝트 데이터 작업을 위한 기존 수동 개발 경로이며, 데모와 혼용하지 마세요.

---

# BID OWL BASIC — Local CLI MVP (P1-04)

Offline CSV → company profile → PASS/FAIL/UNKNOWN rule evaluation → SQLite → PDF/XLSX reports.
This is a development MVP using SYNTHETIC data, not a commercially installed Windows program or legally authoritative bidder-qualification service.

## Install and run
Requires Python 3.11 or newer. ReportLab BSD is required for PDF, and an available Korean TTF font for PDF rendering. On Windows the system Malgun Gothic path is used; on Linux locally installed NanumGothic TTF is used. Override with BIDOWL_PDF_FONT pointing to an installed local .ttf file. Font binaries are never committed or redistributed.

    cd backend
    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python cli.py --csv fixtures/sample_bids.csv --profile fixtures/sample_profile.json --source-id SYNTHETIC-CSV --db ./demo.sqlite3 --output ./reports --format both

Replace all fixture and local path arguments for non-demo use. Never upload customer data, SQLite DB, PDF or XLSX to GitHub. Supported report formats: both, pdf, xlsx. Omit --db for OS-local default database path.

## Input contract
CSV required columns: bid_no,title,agency,category,bid_deadline,budget,requirements. Optional: source_ref,data_as_of.
UTF-8/-SIG, positive KRW integer budget, timezone-aware ISO timestamps including seconds. Requirements are a JSON array of id/kind/value/source (source.text and source.locator). Supported kinds region_any, category_any, license_all, staff_min, experience_total_min_krw. Unknown conditions or missing evidence/profile values -> UNKNOWN, not PASS. Empty conditions -> UNKNOWN. FAIL dominates multiple mixed rules but unresolved conditions continue to require review. Deadline expiry is independent of rule status. Final human decision is always required.

Profile JSON: required profile_id, optional region, categories, licenses, staff_count, experience_total_krw; null means not known, empty category/license lists mean known empty.

## Data safety and report contents
SQLite stores bid versions, profile versions, assessment snapshots, rule evidence, import audit; repeated equivalent data do not create new bid versions. Fail whole CSV on validation issue; SQL transaction rollback on DB write errors. Reports use saved assessment versions (not today's recalculation), with source, checked_at, deadline, individual decisions, and legal non-guarantee warning.

XLSX has sheets 검토요약 and 조건별근거; source strings are escaped against Excel formula injection; zip/xml OOXML generated with Python standard library. PDF uses ReportLab with Korean embedded font and visible evidence. Existing files are not overwritten. An output file generation failure after DB commit may leave the DB persisted; retry creates a new assessment ID and report path. No cross-resource atomic commit is claimed.

## Licensing
ReportLab open-source toolkit: BSD, commercial use permitted (https://docs.reportlab.com/developerfaqs/).
Naver NanumGothic font: SIL OFL 1.1 (https://help.naver.com/service/30016/contents/18088).
Installed Windows system fonts are referenced, not included in source or redistributed. Check the exact Windows environment and embedding permissions before shipping installers.

## Validation (2026-10-26 KST)
Local CPython 3.13.5 Linux: 96 PASS/0 FAIL/0 SKIP via python -m unittest discover -s tests -v; 21 CSV, 27 eligibility, 28 SQLite, 20 report/CLI. All new and previous source/test files Git blob SHA matched their tested local bytes before GitHub commit. Synthetic 2-bid CLI run generated two PDFs and two XLSX; PDF rendered and Korean TTF embedded, XLSX parsed and re-imported with artifact_tool. Native Windows 11 and Microsoft Excel, official procurement source data, Production web UI, real law and installer not verified. Old static legacy QA 340/340 is unrelated to these tests.

Next stage P2: local UI/SQLite read bridge, practical search/filter/evidence and seven themes. Preserve main and current Vercel production.


## P2-01 local SQLite viewer (2026-10-27)

After importing your own approved CSV with cli.py, start a **read-only** local browser from the backend directory:

    python viewer.py --db ./demo.sqlite3 --port 8765

Open http://127.0.0.1:8765 on the same PC. --db defaults to the OS-local database; the file must already exist with schema v1. Stop with Ctrl+C. No internet service, key or Vercel deployment is involved. The viewer will not create or modify a database.

The viewer exposes GET /api/bids (search q, exact category/status, open/expired, profile, pagination), GET /api/detail (source_id,bid_no,profile) and GET /api/profiles. The browser renders real SQLite source snapshots, version-sensitive conservative statuses, timestamps and condition evidence; old 2025 static demo metrics are NOT presented. Current assessment expired flag is recomputed relative to now; stale previous PASS/FAIL becomes UNKNOWN until assessed again. Content is displayed as text (not raw HTML). Seven light/dark themes can be selected.

Favorites and selected theme are stored in **this browser's localStorage**, not in SQLite. In the historical P2-01 build, “favorites only” filtered only the currently loaded page. P2-02 changes this behavior; see below. Browser visual regression, profile editing and Windows integration remain follow-ups. No write API is available. API refuses remote host headers and cross-origin requests; only 127.0.0.1 is bound. All app files must remain together under backend/ui.

Verification: isolated P2 Python unittest suite 5 pass/0 fail; Node UI JS syntax check passed locally. Combined 101-test suite not rerun from the exact GitHub source after commit. Chromium test could not navigate any local/test URL in this execution environment (ERR_BLOCKED_BY_ADMINISTRATOR), so browser rendering is NOT VERIFIED, not a confirmed application failure. Windows/native application and production remain UNVERIFIED / NOT APPLICABLE.

## P2-02 global favorites query (2026-10-27)

The "관심 공고만" checkbox now searches **all records** matching favorite identifiers (including bids beyond the currently displayed page) before applying status/category/deadline/text filters and pagination. Accurate global totals and pages are returned by the local read-only backend. Favorites remain isolated to the same browser's localStorage; switching browsers or clearing storage does NOT preserve them. Up to 1,000 saved favorite identifiers can be queried. Old malformed localStorage identifiers or exceeding the limit produce a visible error rather than silently omitting data.

A POST /api/bids/favorites endpoint was added **for JSON read-only querying only**, not for database mutation. Request schema is `{"favorites":[["source_id","bid_no"],...],"filters":{"q":"...","page":"1","page_size":"30"}}`; size limited to 1 MiB, favorites at most 1,000, allowed filter keys restricted. Strict exact loopback Host, Origin and application/json are required. Uses SQLite URI mode=ro + query_only; no database schema migration, write endpoint, customer file upload, or external service. The original GET /api/bids, /api/detail and /api/profiles remain compatible.

Implementation choice:
- In-browser full 10,000-bid pagination and filtering: zero server changes but many repeated requests and inconsistent totals; rejected.
- Persistent SQLite favorites table: good multi-browser durability but needs schema migration, backup, and authenticated mutation API; deferred to a reviewed phase.
- Browser-local identifiers + bounded read-only POST: chosen for lowest initial cost/risk and accurate global pagination.

New tests in backend/tests/test_viewer.py cover global filtering across pages, UNKNOWN+filters, empty sets, malicious/invalid input, POST origin/type/size bounds and SQLite immutability. **They are committed but were not executed as part of the full remote checkout this session.** Verified separately: actual committed JS source parses with the JavaScript function compiler (no execution), and the new Python helper snippet passes local ast.parse. A connector-source byte inspection confirmed expected GitHub files. Raw private source download from this execution environment failed DNS resolution, so the combined expected 103 tests (96 prior + 7 P2) are **NOT VERIFIED**. Browser/Windows actual usage remains unverified. Do not claim P2-02 fully integrated until a real repo checkout runs the tests.

## P2-03 local company-profile revision — preview, backup, apply

The browser can show the selected saved company profile using the same-PC read-only `GET /api/profile?profile_id=...` endpoint. "프로필 편집 파일 만들기" opens a local form for region/categories/licenses/staff/experience. UNKNOWN (`null`) and verified empty lists (`[]`) are distinct. **Downloading JSON does not update SQLite**. No browser write API was added.

From `backend`, use an existing database and downloaded JSON file (first preview):

    python profile_workflow.py --db ./demo.sqlite3 --profile-file ./company-edited.json --expected-version 1 --reassess

After reviewing the preview and selecting a **new backup filename that does not yet exist**, apply:

    python profile_workflow.py --db ./demo.sqlite3 --profile-file ./company-edited.json --expected-version 1 --reassess --apply --backup ./before-profile-change.sqlite3

For a new company, add `--create` and omit the expected version (default 0). The DB file must already exist. This program does not create databases, contact network services or install anything. The backup must be different from the source and cannot overwrite an existing file. Profile edits create an immutable new version (if changed). Re-assessment, when explicitly requested, evaluates all locally stored bids against the newly saved profile and adds immutable assessment snapshots. This may be expensive: at most 10,000 bids per run, with optional `--max-reassess` to refuse larger batches. An unassessed profile revision causes old assessment status to become UNKNOWN on the read-only viewer, until rechecked.

The `--apply` route saves a consistent backup **before** mutation. The existing SQLite engine commits profile and each assessment sequentially, not atomically as a batch: an interrupted multi-bid assessment may be PARTIAL. A partial-write error reports the backup filename and count of previously committed assessments; inspect before an operator chooses to restore. No automatic rollback falsely claims otherwise.

Comparison considered:
- **Browser POST mutations**: one-click UX but new CSRF/authentication surface, backup lifecycle, and migration decisions. Deferred pending security approval and real Windows/browser verification.
- **Local CLI with explicit --apply/backup**: modest usability cost, no remotely reachable write endpoint, can reuse existing revisioning and provenance. Selected for this stage.

The new `tests/test_profile_workflow.py` includes 8 synthetic regression methods for preview-no-write, backup/no-overwrite, version conflict, validated JSON, creation and partial-write failure. `tests/test_viewer.py` adds 1 read-only profile query method. Expected total when run in a full checkout: **112 tests** (96 prior P1 + 8 viewer + 8 profile workflow). **Do not report 112 PASS yet:** this session verified connected GitHub code presence and actual JavaScript syntax, but not full Python execution, end-to-end browser, native Windows, or data restoration on real customer DB. The earlier 96 P1 and 5 P2 PASS are historical measurements, not combined proof for this commit.

## P2-04 safety/hot-path corrections (2026-10-27)

The edit preview now opens one **SQLite URI mode=ro + PRAGMA query_only** connection and validates the schema. An already-existing unrelated or unversioned/blank SQLite file cannot be silently initialized by a preview or apply. Apply independently preflights the schema in read-only mode before opening the writer. When profile data is committed, `BidOwlStore.save_profile(..., expected_version=N)` enforces N inside SQLite's `BEGIN IMMEDIATE` write transaction: edits from other processes after the preview cannot be silently overwritten. Version conflicts are reported and previously made backups are retained. This still is not an atomic transaction spanning the backup file and all re-assessments.

The viewer's single-bid detail query now adds parameter-bound `source_id + bid_no` filtering in SQLite **before loading rows**, rather than scanning all bid payloads. This improves the detailed-evidence lookup scaling but is NOT a measured 10,000-record performance result. Keyboard dialog behavior has also been corrected: descriptive dialog heading, Tab/Shift+Tab focus loop, and asynchronous result generation identifiers so closed panels do not repopulate from late API responses.

Added tests: three synthetic profile workflow cases for no writer during preview, invalid-DB no initialization, and version race rejection; one targeted-detail result test. Total source tests now expected: **116 = 96 P1 + 9 viewer + 11 profile**, NOT EXECUTED as the exact full private checkout in this environment. GitHub writes and exact JS parse were verified. End-to-end Windows, actual SQLite integration for this commit, native Excel/browser/Blob download and public sales readiness are NOT VERIFIED.
