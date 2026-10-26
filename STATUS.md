# BID OWL STATUS — P2-05 · 2026-10-27 KST

## Branch, source and main safety
Private repository hibi89/Bid_Owl. Feature branch feature/bid-owl-v1-basic-mvp; starting HEAD 6f2cd7652d0f9284402f7528c8a0c2c2ec1fd531. Main at start c888c795bef72734f3f7016e54013b82453f11d8, unchanged by planned work. Original legacy rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Main/Vercel not modified. Existing Vercel project project08-bid-insight/prj_YcrN7OdOjKl6M457HelGIItLeeXZ is legacy; new localhost Python is not deployed, production URL/live SHA not checked.

## Source implemented
P1-01 import, P1-02 evidence-based conservative PASS/FAIL/UNKNOWN, P1-03 immutable SQLite revisions and non-overwrite backup, P1-04 local report generation. P2-01 readonly SQLite viewer/7 themes, P2-02 global read-only favorites, P2-03 browser JSON profile editor and separate backup-required CLI mutation/reassessment, P2-04 SQLite compare-and-set profile version and read-only previews, precise detail SQL and async keyboard dialog fixes.

P2-05 new:
- backend/report_existing.py reconstructs existing saved evaluation ID into Excel or PDF using mode=ro/query_only, historical exact bid version and immutable rule evidence; **no DB mutation or new assessment**. Checks ID/output collisions; if PDF requested checks dependency and Korean TTF. Existing files not overwritten.
- backend/ui/ui.js evidence drawer shows the local re-export command for selected stored assessment ID and warns on stale historical evaluations. No new HTTP write endpoint.
- backend/tests/test_report_existing.py (6 synthetic methods) and backend/smoke_local.py + tests/test_smoke_local.py (1 method) add a disposable real-code-path integration diagnostic from synthetic CSV through SQLite/XLSX/localhost HTTP+favorites/profile edit+backup/reassess, with no external/API/customer data and no PDF requirement.
- backend/REPORT_REPLAY.md, NEXT_TASK.md, STATUS.md, HANDOFF.md updated. Command from backend: `python smoke_local.py`; replay: `python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./replayed_reports --format both`.

## Verification and uncertainty
GitHub source fetched after changes, 123 *declared* test methods confirmed by inspecting eight test files: importer21, eligibility27, store28, report20, viewer9, profile-workflow11, report-existing6, smoke-local1. **123 TESTS NOT EXECUTED/NOT PASS-VERIFIED.** Previously P1 Linux 96 PASS/0 FAIL on 2026-10-26; earlier P2 isolated tests/smoke not equivalent to current full checkout. GitHub current ui.js V8 Function syntax parse PASS. Code added through connector and source SHA checked; no real Python DB/report tests run this session. Private repo cannot be checked out in this container: previous private clone and signed raw download DNS/auth failed, api.github.com DNS also inaccessible. Browser localhost previously blocked by execution policy ERR_BLOCKED_BY_ADMINISTRATOR.
No native Windows 11, actual PDF Korean font, Chrome/Edge, browser export, 7-theme visual, 10k bids speed, real government data or KIPRIS legal confirmation. No fake completion claims.
Report output is local filesystem and SQLite read-only; XLSX/PDF two-output creation is not atomic if a filesystem failure occurs, though existing output targets are rejected.

## Immediate next priority
P2-06 authorized full checkout + actual 123 unittests + python smoke_local.py; repair failures. Then real report_existing XLSX/PDF, Windows Edge/Chrome, 7-theme keyboard, PDF/Excel smoke, 10k-bid performance and backup restore tests. After BASIC human-friendly UI closure, P3 official user-key API, P4 opt-in model AI, P5 Windows installer/security, P6 trademark/sales release. User consent required for paid services, external uploads, public launch, main/Vercel changes. Brand/price not validated: 59,000 / 149,000 / 299,000 KRW planned.

## Privacy/no-operations
No customer bid data, SQLite, PDF/Excel, secret/API key, .env or font uploaded to GitHub. No fees or external service actions. No destructive user system operation. SQLite historical status is reference only; no legal qualification/award warranty. All GitHub source work committed as hibi89; final HEAD and author to re-verify after HANDOFF.
