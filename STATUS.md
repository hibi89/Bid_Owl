# BID OWL — STATUS (2026-10-26 KST)

## Source and checkpoints
Repo: **hibi89/Bid_Owl**, private, ID 1399359397 (renamed from project08-bid-insight).
Protected existing main: **c888c795bef72734f3f7016e54013b82453f11d8** (unchanged).
Working branch: **feature/bid-owl-v1-basic-mvp**; P1-02 code commit **fa2ed6aea6c634490d1f467bc1a3c3788df6adb1**; docs-only commit afterward, query live branch SHA.
Legacy rollback source SHA: 2807a93a3e0deba98840712401fdd6025e6f5610.

## Implemented
- P1-01: CSV input schema/validation and error-reporting, synthetic fixtures, 21 unit tests previously run (21 PASS/0 FAIL).
- P1-02: immutable CompanyProfile with strict input checks and explicit missing values; evaluate_bid handles region_any/category_any/license_all/staff_min/experience_total_min_krw; per-rule PASS/FAIL/UNKNOWN; provenance, reason codes, checked_at, is_expired, data_as_of; missing evidence, unknown kinds, missing profile values => UNKNOWN. Any FAIL outranks UNKNOWN in aggregate while unresolved rules still signal human review. Final manual approval required on every result.
- Files added: backend/bidowl/profile.py, eligibility.py, backend/tests/test_eligibility.py; existing __init__.py extended without removing importer exports.

## Verification
New 27 P1-02 unittest cases run locally in Linux CPython 3.13.5: **27 PASS, 0 FAIL, 0 SKIP**. Test cases include boundary counts, profile validation, exact region matching, multiple decision priorities, expired separately from eligibility, missing source, unknown rule, profile edits.
Local test used an equivalent limited schema contract stub (Bid/Requirement and is_expired) to avoid assuming private GitHub checkout access; P1-02 production code and test file **GitHub blob SHAs match local tested source exactly**. Full previous importer/P1-01 test suite was NOT rerun in the same current environment; integration regression is UNVERIFIED. P1-01 previous result: 21 PASS/0 FAIL from prior turn, not additional tests run now.
Real source CSV, Windows, legal qualification, full end-to-end local run, PDF/Excel, Vercel/browser and public API are NOT VERIFIED.

## Next / pending
P1-03 transactional SQLite with idempotence, revisioned bids and audit; P1-04 CLI/PDF/Excel; BASIC UI/7 themes; PRO official API; PREMIUM optional AI; Windows install/QA/sales. No customer data or external keys copied.

## Deployment/approval gate
Legacy Vercel project project08-bid-insight (prj_YcrN7OdOjKl6M457HelGIItLeeXZ) only previously READY metadata, actual Production SHA/HTTP/UI behavior NOT VERIFIED. Feature branch Python only: **Vercel production deployment NOT APPLICABLE**, no settings modified.
BID OWL brand license/KIPRIS/BiddingOwl conflict unresolved; public sales held.
