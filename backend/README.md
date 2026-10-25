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
