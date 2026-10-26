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
