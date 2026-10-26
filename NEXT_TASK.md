# BID OWL NEXT_TASK — P2-06 · 2026-10-27 KST

Private repository hibi89/Bid_Owl. All work ONLY feature/bid-owl-v1-basic-mvp; never change main/legacy Vercel/deployments/paid services/customer files without approval. On user ㄱ, read fresh HANDOFF, STATUS, AGENTS, REQUIREMENTS, NEXT_TASK and actual GitHub source; verify main & feature branch HEAD first.

## Prior source milestones
- P1: strictly validated CSV; source-grounded 3-state rule assessment, immutable bid/profile/assessment revisions + backups, native XLSX and ReportLab PDF via CLI (earlier 96 tests PASS Linux 2026-10-26).
- P2-01: localhost read-only SQLite HTTP/viewer and 7 themes; P2-02 global read-only favorites with bounds and same-origin POST; P2-03 explicit backed-up company editing and re-assessment CLI + browser JSON export; P2-04 readonly preview, SQLite version CAS, per-bid exact SQL detail, modal accessibility; P2-05 immutable saved report replay and synthetic full-stack smoke.

## P2-06 changes, source implemented / not yet integrated verified
1. backend/bidowl/report.py: XLSX exclusive-creation writer removes its own incomplete file on any ZIP/XML failure; existing paths are never deleted.
2. backend/report_existing.py: on failure of PDF after successful XLSX with --format both, remove only the completed sibling generated in this invocation. This is best-effort failure cleanup, not power-loss-level atomic multi-file transaction. Source SQLite remains query_only.
3. backend/tests/test_report.py: +1 synthetic interrupted XLSX sheet regression. backend/tests/test_report_existing.py: +2 regressions for sibling PDF failure cleanup and pre-existing PDF preservation.
4. backend/ui/index.html + ui.js: new company profile onboarding button. Create JSON from empty conservative unknown fields, enter new profile ID, download locally and apply via existing explicit --create / --apply / --backup CLI. Existing-profile editor remains; no new HTTP write path. backend/tests/test_viewer.py adds assertions to existing UI/theme test.
5. backend/verify_local.ps1: self-contained Windows local verification from *actual private checkout*: Python all tests, synthetic smoke, Node syntax if installed. Stops at first nonzero exit and notes untested Windows/native Excel/browser/official records.
6. backend/REPORT_REPLAY.md updated.
7. GitHub connected source contains **126 declared Python test methods**: 27 eligibility +21 importer +11 profile workflow +21 report +8 report_existing +1 smoke +28 store +9 viewer. Count confirmed by reading test definitions, **126 NOT RUN / NOT 126 PASS**. Exact current GitHub ui.js parsed with V8 Function constructor = PASS. Runtime profile onboarding/browser and output-failure recovery not verified.

## NEXT P2-07: highest priority, acceptance criteria
- Work from authorized GitHub private checkout with Python 3.11+ and ReportLab/local Korean TTF installed. Run:
  `cd backend`
  `python -m unittest discover -s tests -v`
  `python smoke_local.py`
  `node --check ui/ui.js`
  Windows convenience: `powershell -ExecutionPolicy Bypass -File .\verify_local.ps1`
  Report actual PASS/FAIL/skip counts and fix any real test failures immediately. The smoke uses only provided synthetic fixtures and a temp directory. Do not repeat prior container private git/raw DNS attempts or call stand-ins the actual repo.
- Validate real local output failure cleanup and both-format PDF font/license, native Excel, browser Blob download for new and edited profile, 7 themes, keyboard focus and mobile widths, no profile before onboarding, version conflict after backup; measure 10k list/detail.
- BASIC customer-ready UX still incomplete: CLI necessary to save/edit profile and export reports. New read-only HTTP binary report route might avoid CLI, but must first review sensitive output/download/path safety and avoid DB mutation or leaked files; full write UI requires explicit authenticated security/CSRF/backup approval.
- P3 official procurement user-key API, P4 optional AI, P5 Windows installation/security, P6 KIPRIS and product sale later.

## Blocking, privacy and production
Connector GitHub read/write works; local sandbox can't obtain private full checkout via previous DNS/auth and signed raw method, so all P2 tests remain unverified on actual checkout. Browser automation previously blocked with ERR_BLOCKED_BY_ADMINISTRATOR. Main unchanged from baseline c888c795bef72734f3f7016e54013b82453f11d8 at start; recheck at final. Existing Vercel project project08-bid-insight not touched; local Python product not deployed. No customer CSV/docs/SQLite/API credentials/PDF/XLSX or fonts committed; no external service calls or costs. Old 340/340 school static QA is not BID OWL product QA.
