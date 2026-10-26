# BID OWL NEXT_TASK — 2026-10-27 KST

Repo: hibi89/Bid_Owl (private). Work ONLY on feature/bid-owl-v1-basic-mvp. User ㄱ resumes first unfinished step. Read latest HANDOFF -> STATUS -> AGENTS -> REQUIREMENTS -> NEXT_TASK -> source. Never modify main/Vercel without approval.

## Implemented source
- P1: strict CSV importer, PASS/FAIL/UNKNOWN evidence engine, revisioned SQLite, CLI PDF/XLSX. Previous real combined Linux 96 PASS / 0 FAIL from 2026-10-26, not re-run here.
- P2-01: localhost SQLite read-only API, responsive listing/filter/detail, seven themes. Previous five isolated mock-data tests PASS.
- P2-02: server-side global favorites before pagination; bounded same-origin read-only JSON POST; two more viewer regression methods committed, previously unexecuted.
- P2-03: new `backend/profile_workflow.py` dry-run first, explicit --apply and backup, optimistic existing-version check, create opt-in, optional --reassess all bids (<=10000), history untouched and PARTIAL_WRITE handling. New `GET /api/profile` returns current saved profile read-only. UI field editor exports local JSON for a human-run CLI apply, NOT silent database mutation. Updated backend/ui/index.html, ui.js and ui.css, backend/tests/test_profile_workflow.py (8 source tests) and backend/tests/test_viewer.py (+1 method).
- GitHub exact blob SHA for profile_workflow.py a8ac6a204edcbf8afde904391d4f51c53f12876f was independently recomputed on local source bytes. AST compile PASS; 7 separate isolated smoke tests with a **fake SQLite store**, 0 fail. Actual GitHub JS source V8 syntax parse PASS. This smoke is NOT the real BidOwlStore integration and is not part of the repository unittest suite.
- Expected full tests 96 P1 + 8 viewer + 8 profile workflow = **112** tests, but full 112 suite NOT RUN / not PASS-verified.

## NEXT P2-04: full integration and customer-local usability
1. Verify latest remote branch HEAD, author/committer, exact files. In a permitted authenticated full private checkout, run:
   - cd backend && python -m unittest discover -s tests -v
   - node --check ui/ui.js
   - python cli.py --csv fixtures/sample_bids.csv --profile fixtures/sample_profile.json --source-id SYNTHETIC-CSV --db ./demo.sqlite3 --output ./reports --format both
   - python viewer.py --db ./demo.sqlite3 --port 8765
   - Browser GET /api/bids, POST /api/bids/favorites with same-origin request, GET /api/profile and detail; then profile_workflow.py preview -> backup -> --apply --reassess; confirm original PASS remains in history, latest status reflects new version.
2. Fix concrete failures, including URI/Host/Origin assumptions, HTTP 400/403 paths, desktop and mobile UI forms, profile null vs empty array, file download restrictions under CSP. Do not repeat prior private raw-download DNS method or Chromium blocked navigation in same execution environment.
3. Benchmark up to 10,000 bids search and optional re-assessment with real full engine, validate crash recovery and actual backup restore with separate test copy.
4. Decide UX polish after security review: optional one-click local profile editing route only if authentication, CSRF protection, backup/recovery, authorization and user approval are settled. Current product requires explicit local CLI command and is incomplete as a one-click commercial UI.
5. Windows 11 real Edge/Chrome, PDF+native Excel, seven-theme visual/accessibility, server only on 127.0.0.1, file preservation, no external egress. Brand/KIPRIS, official API, legal rules and public release unverified.

## Explicit unresolved / prohibited
Private full checkout unavailable from this runtime (prior clone DNS/auth and raw signed URL DNS fail); 112 source tests remain unexecuted, browser in this sandbox previously ERR_BLOCKED_BY_ADMINISTRATOR. User real DB, credentials, customer documents, reports, fonts never upload. Main and existing Vercel untouched; Python local module Production deployment N/A. Do not claim real official procurement data, Windows installer, sales readiness, or formal legal qualification. P3 API, P4 paid AI, P5 installer, P6 trademark/sales follow later.
