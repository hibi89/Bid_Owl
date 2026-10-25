# BID OWL — STATUS (2026-10-26 KST)

## Repository/version
GitHub private: hibi89/Bid_Owl, id 1399359397 (renamed from project08-bid-insight).
main = c888c795bef72734f3f7016e54013b82453f11d8 (unchanged 2025 educational static app).
Development branch = feature/bid-owl-v1-basic-mvp.
P1-01 source commit = 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b; docs-only followup commit is the newer HEAD. Legacy rollback SHA 2807a93a3e0deba98840712401fdd6025e6f5610.

## Done — P1-01
New source: backend/bidowl/schema.py, importer.py, __init__.py; synthetic fixtures/sample_bids.csv; tests/test_importer.py; backend/README.md.
CSV import validates header, UTF8/SIG, ISO date timezones, KRW budget, requirement JSON provenance, duplicate bid/rule IDs and limits; all-or-nothing rejection. Expired deadline calculated dynamically, not precomputed 2025 days_left.
Test executed locally (Linux CPython 3.13.5): python -m unittest discover -s tests -v from backend, 21 PASS / 0 FAIL / 0 SKIP. Sample fixture two synthetic records, one expired. Remote and local Git blob SHAs match for four Python files. The GitHub CSV is UTF-8 without BOM, local fixture UTF-8-SIG; remote fixture not independently executed. Commit Author and Committer mapped to hibi89.

## Incomplete
P1-02 company profile/rule decision, P1-03 SQLite, P1-04 Excel/PDF/CLI, UI/7 themes, PRO official procurement API, PREMIUM optional AI, Windows installer/security, real data QA and sales: NOT IMPLEMENTED.
No real source documents or credentials. No actual user data imported.

## Production and dependencies
Current branch is local Python development, not a Vercel deployment target. Existing Vercel project project08-bid-insight / prj_YcrN7OdOjKl6M457HelGIItLeeXZ had READY metadata in prior check; rename Git-link/Production SHA/browser functionality NOT VERIFIED. No Production/configuration changes.
BID OWL brand chosen but KIPRIS and similar BiddingOwl rights NOT VERIFIED; public launch held. Windows 11 and official procurement API NOT VERIFIED.
Next command ㄱ => implement P1-02 on same feature branch. Follow HANDOFF.md -> STATUS.md -> AGENTS.md -> REQUIREMENTS.md -> NEXT_TASK.md.
