# BID OWL — STATUS (2026-10-26 KST)

## Repository/branches
- Private GitHub: hibi89/Bid_Owl, repository ID 1399359397 (old name project08-bid-insight).
- Existing main HEAD c888c795bef72734f3f7016e54013b82453f11d8 **unchanged**; legacy snapshot rollback 2807a93a3e0deba98840712401fdd6025e6f5610.
- Active branch feature/bid-owl-v1-basic-mvp. P1-03 source commit **e1f3befafe1590570a99879812f678a5a60b99a1**. Subsequent docs commit becomes branch HEAD (look it up).

## P1 BASIC progress
- P1-01 CSV importer (schema validation, UTF-8/SIG, ISO date, budget/JSON, whole-batch rejection, synthetic sample): code exists; previous reported 21 tests PASS.
- P1-02 immutable company profile and per-condition PASS/FAIL/UNKNOWN with source evidence and manual review: code exists; previous reported 27 tests PASS.
- **P1-03 SQLite implementation COMPLETE at module scope**: bidowl/store.py, tests/test_store.py, __init__.py exports, backend/.gitignore, backend/README.md. SQLite v1 schema, profile versions, bid snapshots keyed source_id+bid_no, content-digest idempotency, append revisions, import audit log, immutable assessments/rule provenance, default local storage path, atomic rollback, consistent non-overwriting SQLite backup. Unknown schema is refused; auto-migration and official amendment number parsing not implemented.

## Actual tests in this work turn
- Linux CPython 3.13.5, from backend: python -m unittest discover -s tests -v (only new test_store.py installed in local recreated project).
- P1-03 **28 tests PASS / 0 FAIL / 0 SKIP** including SQL injection-shaped identifiers, insert failure rollback, profile/bid old revisions, import errors, restart, backup integrity and assessment source.
- Local test environment contained manually reconstructed prior module surfaces for P1-01/P1-02; it is not a byte-for-byte checkout of every earlier file. New store.py, test_store.py, __init__.py match GitHub blob SHA exactly. **Full combined 76 test execution against exact GitHub checkout is NOT VERIFIED**; next step requires that.
- Official bid sources, Windows 11 recovery/installation, unexpected power loss and public qualification law remain unverified.

## Pending
P1-04 minimal CLI/report (PDF & Excel actual file validation, Korean rendering, timestamps, evidence), BASIC UI/7 themes; PRO government API (official correction number), PREMIUM optional AI, Windows packaging, external integration/real production QA, brand/KIPRIS and sales gate.
No actual personal/company data or API keys uploaded.

## Production
Legacy Vercel project project08-bid-insight (prj_YcrN7OdOjKl6M457HelGIItLeeXZ) had historical READY metadata only. Production URL/SHA, Git-rename connection and actual UI/browser are NOT VERIFIED. Current Python feature is not applied to Vercel. No change to production/configuration/domain/permissions.

## Immediate resume
Read HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → NEXT_TASK.md and latest source; user ㄱ advances P1-04. Re-test full checkout before describing entire BASIC MVP as functional.
