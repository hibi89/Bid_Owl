# BID OWL STATUS — 2026-10-27 KST

## Repository and verified branch heads
Private: hibi89/Bid_Owl, repo ID 1399359397. Feature branch: feature/bid-owl-v1-basic-mvp. Observed starting feature SHA 1cfb8f54304a47f3604010ed4e4c86b2eeb505f1; P2-02 code commits 016ab8c251f92628e17ccd6e102b374284d20608, 823edf48d31ed0077cdd0c700f20594f59b44b68, cd05d6d56daf6613c7f7ebe11c558a60f3cfe7d9. Docs follow code: after updating HANDOFF, query live current branch SHA. Main remained c888c795bef72734f3f7016e54013b82453f11d8 at session start; recheck on closure. Legacy rollback commit 2807a93a3e0deba98840712401fdd6025e6f5610.

## Product implementation
P1-01 importer, P1-02 conservative evidence-backed PASS/FAIL/UNKNOWN, P1-03 versioned SQLite/backups, P1-04 complete local CLI CSV/profile -> stored revision/assessment -> Excel/PDF. UI P2-01 in backend/viewer.py and backend/ui/: loopback, SQLite mode=ro, static local seven-theme responsive table, category/status/deadline/text/profile search, detail rule provenance. Historical 2025 school demo data and 340/340 are not current procurement data.

P2-02 code feature: browser-local favorites selected from any page are now processed by bounded **read-only POST /api/bids/favorites** against the complete SQLite listing before search/status/category/expiry and pagination, fixing prior current-page-only favorite totals. Browser sends JSON pairs source_id+bid_no, max 1000; request max 1MiB, strict JSON, exact same Host and Origin. The endpoint only executes query_bids with a query_only connection; no DB write, storage schema migration or external API. Stored IDs and chosen theme still localStorage in same browser. Unavailable/malformed favorites fail visibly instead of hiding records.

## Verification: facts vs gaps
Previously measured P1 96 PASS Linux CPython 3.13.5, 0 FAIL (2026-10-26); synthetic two PDF+XLSX. P2-01 isolated 5 PASS from prior session, 0 FAIL. This session added 2 test cases to backend/tests/test_viewer.py (expected combined 103 tests) but DID NOT execute them. Confirmed new files and blob SHA from GitHub; exact remote JS syntax parsed successfully in V8 Function compiler (PASS). New Python helper snippet passed local AST parse, not full Python syntax test and not real HTTP runtime test.
GitHub private raw URL signed-download via curl failed DNS resolution in this container, after previous private repo clone DNS/auth restriction; stop repeating unchanged method. Chromium in prior session blocked local/alternate host navigation by ERR_BLOCKED_BY_ADMINISTRATOR, so browser UI/screenshot verification is NOT VERIFIED, not a proven product fault.
Combined 103-test suite, end-to-end integration on full checkout, native Windows, browser, Excel, user official bids, security audit and legal procurement interpretation remain NOT VERIFIED.

## Remaining priorities/risks
NEXT P2-03: execute actual full GitHub repository checkout tests, correct integration issues, design and implement safe company-profile edit/assessment workflow, remaining search/UI gaps, keyboard/7-theme browser regression and Windows smoke. P3 PRO official API, P4 PREMIUM optional AI, P5 packaging/security/reinstallation, P6 public brand/sales license. Public BID OWL trademark not cleared via KIPRIS; do not release/claim an official qualification verdict.
Current P2-02 is SOURCE IMPLEMENTED / INTEGRATION UNVERIFIED; not customer-ready. SQLite assessment status must remain UNKNOWN when bid/profile revision changes. Existing partial DB commit before PDF/Excel export remains unresolved for retries.

## Production/data safety
Original legacy main and existing Vercel project project08-bid-insight (prj_YcrN7OdOjKl6M457HelGIItLeeXZ) not modified; no new Python feature production deployment (N/A). Current legacy production URL and live SHA/HTTP not verified. No paid services, external data transfer, changes to domains or env, customer bid data, credentials or SQLite uploaded. Local backup backup_to forbids overwriting existing files. GitHub writer hibi89; final author/committer and HEAD check required after docs.
