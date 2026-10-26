# BID OWL STATUS — P2-06 · 2026-10-27 KST

## Branch/production source
Private hibi89/Bid_Owl (repo ID 1399359397), only feature/bid-owl-v1-basic-mvp changed. Feature starting HEAD 4c7cdcb169cf1fb68f4ea9f4f63dd91bfad15341; main baseline c888c795bef72734f3f7016e54013b82453f11d8. Recheck after HANDOFF. Legacy restore SHA 2807a93a3e0deba98840712401fdd6025e6f5610. Existing main and Vercel project project08-bid-insight/prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched. No new Python localhost app production deployment (N/A); legacy deployed URL/SHA/live HTTP not verified.

## Implemented source
P1 importer + evidence-backed PASS/FAIL/UNKNOWN rule engine + immutable SQLite revision/backups + CLI PDF/XLSX. P2-01 local readonly SQLite UI/7 themes, P2-02 server-side global readonly favorites query, P2-03 JSON profile edit+backed-up CLI apply/reassess, P2-04 readonly preview/version race protection/SQL detail lookup/accessibility, P2-05 immutable assessment report replay with synthetic full-stack local diagnostic.

P2-06:
- backend/bidowl/report.py: incomplete exclusive-created XLSX archive is deleted when ZIP/XML generation raises, without deleting any pre-existing path.
- backend/report_existing.py: if --format both creates XLSX then PDF export fails, cleans up generated XLSX sibling. Not a true atomic two-file filesystem transaction on power loss.
- backend/tests/test_report.py +1 and backend/tests/test_report_existing.py +2 fault-injection regressions, demonstrating intended behavior when executed (not yet run).
- backend/ui/index.html and backend/ui/ui.js: create-company onboarding form exports JSON locally with explicit --create --apply --backup CLI instructions. Does NOT open browser DB write API; null/unknown fields default conservatively. backend/tests/test_viewer.py adds static onboarding assertions to existing test.
- backend/verify_local.ps1: future actual Windows checkout test runner, stops on failed unittest/synthetic smoke; Node check if installed. backend/REPORT_REPLAY.md updated.
- NEXT_TASK, STATUS, HANDOFF updated.

## Verified measured facts vs gaps
GitHub test sources fetched and counts inspected: **126 defined methods** = eligibility27 + importer21 + profile workflow11 + report21 + report_existing8 + smoke_local1 + store28 + viewer9. These are merely TEST DEFINITIONS, **126 NOT EXECUTED** on current private repo. Source `backend/ui/ui.js` V8 Function syntax parse PASS; output from latest GitHub ref inspected. New Python regression tests and workflow not actually run, so no claimed pass results. Historic P1 96 PASS on 2026-10-26 Linux and historical isolated P2 checks not equivalent to current branch.
Private full checkout not present in Python container (prior private clone, signed raw, DNS/auth failures). Do not repeat same failed network method or treat old stand-in files as exact GitHub branch. No Windows real Edge/Chrome/7 theme preview, native Excel/ReportLab PDF outputs or actual 10k-bid benchmark this turn. Browser prior sandbox ERR_BLOCKED_BY_ADMINISTRATOR. KIPRIS trademark, official procurement data and real legal eligibility unverified.

## Current next steps
P2-07 priority: authentic private full checkout `python -m unittest discover -s tests -v`, `python smoke_local.py`, `node --check ui/ui.js`; Windows users can run `backend/verify_local.ps1`. Fix actual failures. Then real PDF and Excel, full 7 themes/mobile/focus/Blob profile create, 10k search and version-conflict/backup restore. BASIC product not ready for customer sale: profile mutation and report generation still require explicit CLI. Following P3 official API, P4 opt-in AI, P5 Windows installer/security, P6 brand/KIPRIS sales gate. Planned 59k/149k/299k KRW pricing not validated.
No customer DBs, docs, API credentials, reports, fonts or private info shared, no service fees, no Vercel/main changes or user machine mutation. Author connected hibi89; recheck feature commit author after HANDOFF.
