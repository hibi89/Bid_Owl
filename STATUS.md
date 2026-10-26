# BID OWL STATUS — P2-07 · 2026-10-27 KST

## Repository, protected source and scope
Private hibi89/Bid_Owl repo ID 1399359397, active branch feature/bid-owl-v1-basic-mvp, start HEAD 53d7485c67d2212baf3ca213b6d8d21b0996607a. Main start c888c795bef72734f3f7016e54013b82453f11d8; legacy original rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Main/Vercel not touched; new Python app production deployment N/A. Existing Vercel static-demo project project08-bid-insight/prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched and live URL unverified. Recheck final feature/main SHAs after HANDOFF.

## Implemented code and decisions
Prior P1-01..04 importer+rule-backed PASS/FAIL/UNKNOWN+versioned local SQLite+CLI PDF/XLSX. P2-01 read-only localhost viewer and 7 themes, P2-02 global favorites read-only JSON POST, P2-03 backed-up company profile edits and JSON form, P2-04 SQLite version CAS/read-only preview/detail SQL/modal fix, P2-05 saved assessment report replay CLI and synthetic smoke, P2-06 incomplete XLSX/dual-output error cleanup and new-company onboarding.

P2-07:
- backend/viewer.py new `render_saved_xlsx(conn,id)` loads exact immutable historical assessment via saved evidence SnapshotReader, generates XLSX within self-cleaning TemporaryDirectory, caps response at 16 MiB. `GET /api/report?assessment_id=N` returns binary with fixed Content-Disposition filename and XLSX MIME type, no-store/nosniff, strict positive integer, only one param, localhost Host/Origin checks and cross-site Fetch-Metadata rejection; DB `mode=ro` and `PRAGMA query_only=ON`; NO SQLite writes or permanent report files.
- backend/ui/ui.js and backend/ui/ui.css show keyboard-accessible one-click Excel download in evidence drawer for stored assessment IDs and retain conservative stale-assessment warning. No direct PDF download until local font/report rendering browser validation; PDF remains via CLI.
- backend/tests/test_report_existing.py two new real synthetic-DB / HTTP response methods (XLSX valid ZIP bytes, immutable DB, headers, rejection paths); backend/smoke_local.py extended to download and verify ZIP bytes; backend/REPORT_REPLAY.md documents functionality.
- NEXT_TASK, STATUS and HANDOFF updated.

## Measured checks vs unverified
Fetched actual GitHub branch test files and counted 128 declared Python test methods: eligibility27, importer21, profile workflow11, report21, report existing10, smoke1, store28, viewer9. These are **only declared methods; 128 integrated Python test runs NOT EXECUTED** in a full authenticated checkout. Current GitHub ui.js V8 Function constructor syntax parse PASS. No actual HTTP ZIP/Browser/Windows/full SQLite test run this turn. Historic P1 Linux 96 PASS in prior Oct 26 P1 baseline, not applicable to P2-07 changes. Previous partial stand-in /mnt/data/bidowl_p2 not a checkout; /mnt/data/Bid_Owl_work/backend is empty. Private clone/download DNS/auth failed previously; avoid claiming tests of outdated stand-in. Real Chrome/Edge localhost previously blocked ERR_BLOCKED_BY_ADMINISTRATOR in this environment, not proven app defect.
No real native Excel/PDF visual, 10k-bid performance, KIPRIS brand, official tenders, installer, Windows 11 user acceptance or revenue verification. Client DB/docs/credentials never uploaded.

## Next stage
P2-08 run actual 128 Python unittests plus smoke_local.py in genuine checkout, repair failures, test web XLSX download and profile JSON editing on Windows native browser, verify PDF/Excel, mobile/7 themes, run 10k-bid benchmark and backup recovery on synthetic databases. CLI remains for import/profile mutation/PDF; one-click paid UX not yet finished. P3 PRO official user-key API, P4 opt-in AI, P5 Windows packaging/security, P6 trademark and public sale gate follow separately; planned BASIC 59k/PRO149k/PREMIUM299k prices not validated.
No main/Vercel/deployments/paid external services/permissions changed. Connected GitHub account hibi89. Final commit/author verification pending after HANDOFF.
