# BID OWL — NEXT TASK (2026-10-26 KST)

Repository: hibi89/Bid_Owl; active branch: feature/bid-owl-v1-basic-mvp. Do not modify main, Vercel, published domains or existing static educational app without explicit approval.

## Completed
- [x] P1-00: inspect latest HEAD/branches and legacy demo, preserve main SHA c888c795bef72734f3f7016e54013b82453f11d8.
- [x] P1-01: backend/bidowl/{schema.py,importer.py,__init__.py}, backend/tests/test_importer.py, backend/fixtures/sample_bids.csv and backend/README.md.
- [x] CSV strict structure, UTF-8-SIG, timestamp zones, positive KRW integer, 10MiB/10k rows/100 rules, duplicate ID checks, location evidence data, all-or-nothing validation. Code commit 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b.
- [x] 21/21 unittest PASS locally on Linux Python 3.13.5; GitHub source file SHA checks matched.
- [ ] Real Windows 11 run and real official bid inputs untested.

## P1-02 NEXT — company profile and PASS/FAIL/UNKNOWN
Create backend/bidowl/profile.py, eligibility.py, tests/test_eligibility.py.
Profile fields: region, categories, licenses, staff_count, experience_total_krw. Missing profile values = UNKNOWN, never assume FAIL. Eligibility rule kinds: region_any, category_any, license_all, staff_min, experience_total_min_krw.
A condition is UNKNOWN if source text/locator is missing, kind unsupported, policy requires legal interpretation, or profile data missing. Missing/empty conditions => overall UNKNOWN; any FAIL => overall FAIL; otherwise any UNKNOWN => UNKNOWN; all PASS => PASS. Capture each rule ID, source text/locator, evaluation time and reason, human review flag. No implicit geographical synonym expansion.
Tests for PASS/FAIL/UNKNOWN, missing evidence, combined states, profile changes, unknown kind, due dates. Re-run tests, commit feature, verify SHA/author, update STATUS/HANDOFF.

## P1-03 after that — SQLite
Add store.py and tests for original record, revision history, normalized profile, provenance, atomic import, duplicate input, restart, rollback, re-open, local backup. Parameterized SQL; never commit actual data.

## P1-04 after that — report/CLI
CSV + company profile -> SQLite -> decision with sources -> actual Excel/PDF and Korean warning labels. Verify generated binaries/fonts and run on Windows before marking commercial-ready.

## Later
BASIC UI/7 themes, PRO official API, PREMIUM opt-in AI, Windows install/security, brand release QA. API keys, paid third-party use, external file transmission, production deployments require approval. User says ㄱ = move to next incomplete unit.
