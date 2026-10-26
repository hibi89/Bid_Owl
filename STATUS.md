# BID OWL STATUS — 2026-10-27 KST

## Scope / branch
- Private repository: hibi89/Bid_Owl, ID 1399359397.
- Feature: feature/bid-owl-v1-basic-mvp. P2-01 SOURCE baseline: 2ff7a22082b2e37362d0935dee32fa292566eecb. Subsequent documentation commits change feature HEAD: always re-read GitHub HEAD. Main baseline verified at beginning of session: c888c795bef72734f3f7016e54013b82453f11d8. Legacy education rollback: 2807a93a3e0deba98840712401fdd6025e6f5610. Main and existing Vercel were not modified here.
- Production deployment is NOT APPLICABLE for new Python local viewer; existing legacy Vercel URL, deployed SHA, live rendering unverified.

## Completed source milestones
P1-01 validated UTF-8 CSV import, P1-02 3-state rules/evidence, P1-03 versioned SQLite/import audit/backups, P1-04 CLI + report XLSX/PDF. All use local customer-owned source, not static 2025 legacy metrics.

P2-01 NEW source on the feature branch:
- backend/viewer.py: 127.0.0.1 only, existing schema-v1 SQLite opened mode=ro and PRAGMA query_only; no database creation, mutation or arbitrary filesystem reading. GET JSON read API for bid list/query, detail/rule evidence and profile IDs. Host/Origin checks, no-store, CSP, no CORS header, no request data log, bound static assets.
- backend/ui/index.html, ui.css, ui.js: title/agency/no search, category/status/deadline/profile filters, paged table, open/expired checks, evidence detail panel, 7 distinct light/dark themes, responsive shell, theme/favorite localStorage. User text displayed with textContent. Data basis/assessment timestamp included. Latest bid/profile version mismatch causes UNKNOWN/review required instead of showing old PASS.
- backend/tests/test_viewer.py: five synthetic, no customer data, API/SQL/readonly/Host/Origin/evidence/theme regressions.
- backend/README.md, NEXT_TASK.md, this STATUS and HANDOFF documentation refreshed.

## Actual verification
Previous P1: 96 PASS/0 FAIL/0 SKIP with Linux CPython 3.13.5 on 2026-10-26, including two synthetic PDF and XLSX reports. Those 96 were NOT rerun during this P2 session.
P2 isolated local tests: 5 PASS / 0 FAIL, with a local stand-in import for store.default_database_path because private original repo is not cloned in this runtime. Tested using synthetic schema-compatible SQLite. Python syntax check PASS, Node --check original local ui.js PASS, localhost HTTP response/headers PASS.
Browser visual tests: NOT VERIFIED. Real Chromium navigation attempted twice, both localhost and routed alternate test host failed with ERR_BLOCKED_BY_ADMINISTRATOR. This is environment access policy, not proven BID OWL bug. The remote files were committed through connected GitHub tools; exact remote P2 checkout/full 101-test combined suite is NOT VERIFIED. Windows 11/native Excel, external actual procurement CSV/API, installation and legal determination remain NOT VERIFIED.

## Known limitations / next work
- P2-01 favorites only filters the CURRENT returned page. Saved browser-local favorites are not complete global database search. Must correct before declaring BASIC UI complete.
- Current UI is read-only: customer profile updates and assessment rerun are still CLI-driven; no report export action inside viewer. Existing report generation can persist DB before filesystem report succeeds; not cross-resource atomic.
- Search enumerates bid snapshots; large data performance and concurrent import/watch behavior require benchmarking.
- UI 7-theme desktop/mobile browser accessibility/visual regression not verified.
- NEXT P2-02: global favorites + safe profile workflow + full repository 101-test verification + browser/Windows smoke. Later P3 API, P4 optional AI, P5 Windows/security, P6 selling/trademark.
- Public use brand BID OWL not legally cleared; do not advertise an official bidding qualification or guarantee.

## Product / permissions
BASIC 59,000 KRW, PRO 149,000 KRW, PREMIUM 299,000 KRW one-time price targets as planned, not validated sales. No user files, secrets, SQLite database, fonts or PDFs are committed. No external transmission, payment, permissions, domains, main or Vercel mutation performed. GitHub writer connected as hibi89, commit author/committer needs final SHA verification after docs.