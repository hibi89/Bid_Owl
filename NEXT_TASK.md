# BID OWL — NEXT_TASK (2026-10-26 KST)

GitHub: hibi89/Bid_Owl (private); code branch: feature/bid-owl-v1-basic-mvp. Never modify main/static demo, Vercel/project connections, credentials, or public sales without approval.

## Verified progress
- [x] P1-00 source/branch preservation: main c888c795bef72734f3f7016e54013b82453f11d8.
- [x] P1-01 CSV schema/importer, UTF-8-SIG, strict timezone/amounts/requirement JSON, synthetic fixtures, fail-whole-batch, test_importer.py. Code SHA 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b. Prior run: 21 pass, 0 fail.
- [x] P1-02 company profile and eligibility: backend/bidowl/{profile.py,eligibility.py,__init__.py}, backend/tests/test_eligibility.py. Code SHA fa2ed6aea6c634490d1f467bc1a3c3788df6adb1. Added 27 unit tests: 27 pass, 0 fail on Linux CPython 3.13.5 against the GitHub schema contract reproduced locally. New profile/eligibility/test blob SHAs match the tested local files. Entire P1-01+P1-02 suite not rerun together; treat integrated regression as unverified.
- [ ] Windows 11 and real official source CSV tests: pending.

## NEXT: P1-03 SQLite persistence
Implement backend/bidowl/store.py and backend/tests/test_store.py, then run all tests together against an exact complete source checkout:
1. SQLite in local app data directory (never commit .db/.sqlite); schema versioning, foreign keys, transactions and parameterized SQL.
2. Persist profile, imported bids/requirement provenance, per-bid version/revision, decisions with per-rule evidence, per-import audit log.
3. Stable idempotency key: source identity + bid number + revision identifier/content digest; do not replace older bid state destructively. Malformed source -> entire transaction rollback.
4. Recover SQLite file on restart/reopen. Handle repeated imports, profile changes, source revision, integrity errors, interrupted transaction, manual backup.
5. Test atomic rollback, duplicate no-op, corrected changed bid revision, multi-profile isolation, provenance, audit, schema upgrade and reopen. Clearly distinguish real version fields vs synthetic test data.
6. Local tests and GitHub file hash; commit only to feature, update STATUS.md/HANDOFF.md.

## After that: P1-04 reports/CLI
CSV + profile -> SQLite -> 3-state decision/evidence -> Excel/PDF. Real generated output validation (Korean text/fonts/licenses), command-line sample and error messages. Then BASIC UI/7 themes, PRO official public procurement API, PREMIUM opt-in AI, Windows packaging and release QA.

## Contract notes
Profile None = not provided; explicit empty tuple = confirmed none. Source text AND locator required to mark an individual requirement PASS/FAIL. Unknown kinds/values -> UNKNOWN; FAIL priority across multiple rules but unknown rule still flagged for review. Empty rule list -> UNKNOWN. Expired = separate flag (even if eligibility PASS). All decisions advisory; final human approval always required. Real jurisdiction/equivalence/legal rules not inferred.

User "ㄱ" = continue P1-03 without repeating prior choices. No production/deployment claim from local Python commits.
