# BID OWL STATUS — P2-04, 2026-10-27 KST

## Source of truth, branches and originals
Private hibi89/Bid_Owl (repo id 1399359397); only feature/bid-owl-v1-basic-mvp changed. Starting feature SHA 2ffc013c7b743961bc48897e793ddf034e62a437. Main was c888c795bef72734f3f7016e54013b82453f11d8 at start; legacy original rollback SHA 2807a93a3e0deba98840712401fdd6025e6f5610. Final feature/main HEAD and hibi89 author must be checked after HANDOFF. Existing legacy Vercel project project08-bid-insight / prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched. New Python viewer production deployment N/A.

## Implementation progress
P1-01 CSV strict importer, P1-02 evidence/UNKNOWN conservative screening, P1-03 immutable versioned SQLite and backups, P1-04 PDF/XLSX CLI. P2-01 local read-only SQLite 127.0.0.1 UI and seven themes; P2-02 global favorites before pagination via bounded same-origin read-only POST; P2-03 company profile JSON form/readonly profile API and backup-first explicit CLI edit/reassess.

P2-04 fixes committed:
- backend/bidowl/store.py: save_profile accepts optional expected_version checked under BEGIN IMMEDIATE for atomic compare-and-set, preventing concurrent stale revision overwrite.
- backend/profile_workflow.py: ReadOnlyProfileStore SQLite mode=ro + query_only for previews, preflight schema refusal on bad/blank DB, apply preflight + guarded save, retained backup conflict errors. No web write API added; earlier assessment history remains immutable.
- backend/viewer.py: detail lookup constrains exact bid pair inside SQLite rather than loading all bids and scanning in Python.
- backend/ui/ui.js: dialog heading ID matches aria-labelledby, Tab focus trap including initial dialog focus, async detail/profile response invalidation on close or replacement, honest status label.
- backend/tests/test_profile_workflow.py +3 edge regression tests; backend/tests/test_viewer.py +1 direct bid detail lookup test.
- backend/README.md, NEXT_TASK.md, STATUS.md, HANDOFF.md updated.

## Verification truth
Recent previous P1 full suite 96 PASS on Linux 2026-10-26, never rerun with P2 source. GitHub test inventory on latest branch: **116 declared test methods** = importer21 + eligibility27 + store28 + report20 + viewer9 + profile workflow11. Newly added 4 tests committed; combined 116 **NOT EXECUTED**. Exact current remote ui.js V8 Function syntax parse PASS. Backend Python was inspected statically through connector; no current integrated real SQLite run. Do not claim bug fixed through execution; implementation and test cases committed, await confirmation. Previous P2 mock tests isolated from full source, not proof of entire branch.
Private raw fetch from this environment previously DNS failed, do not repeat identical. Browser locally blocked by ERR_BLOCKED_BY_ADMINISTRATOR in previous attempts; no Windows/7-theme visual/Excel production evidence. Python local work directory includes earlier partial stand-in, NOT an exact full checkout; do not run it and claim branch tests.
Report/Bid DB/Backup across filesystem not an atomic unit; profile writes+reassess may partially commit and require manual restoration from backup.
Security: no customer docs/data/SQLite/keys/font uploads, no external services, no browser POST mutating real DB, no main/production/Vercel changes.

## Next priorities
P2-05 actual full 116-test checkout and synthetic end-to-end flow, repair failures; real Windows 11 Chrome/Edge/Excel/PDF/Blob download/keyboard, 7-theme visuals; 10k records benchmark and missing-profile onboarding/report UI. P3 official API P4 opt-in AI P5 Windows release P6 trademark and public sale remain not yet shipped. Pricing planned BASIC 59k/PRO 149k/PREMIUM 299k KRW not sale-validated; BID OWL trademark clearance pending KIPRIS. See NEXT_TASK.md and HANDOFF.
