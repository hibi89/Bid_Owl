# BID OWL HANDOFF — 2026-10-27 KST

## 1. Product, confirmed requirements, technology
BID OWL (비드아울) is a Windows 11 local procurement screening product for smaller businesses. BASIC 59,000 KRW CSV/profile, conservative PASS/FAIL/UNKNOWN & sources, Excel/PDF and usable local UI; PRO 149,000 KRW official procurement API with local-PC-only renewal; PREMIUM 299,000 KRW optional consented user-key AI docs/financial assumptions. Prices and 0 KRW mandatory recurring fee are planning targets. No guarantee of legal eligibility or award. Use Python stdlib, local SQLite v1, ReportLab for PDF, static HTML/JS/CSS UI, seven themes. Historic 2025 education app and its 340/340 are separate from new product.

## 2. Changes, completed functions, decision basis
Preserve main legacy and build in feature/bid-owl-v1-basic-mvp. Completed P1-01 CSV strict import, P1-02 rules with provenance, P1-03 SQLite import/profile/assessment revisions/backup, P1-04 CLI+real XLSX/PDF. P2-01 committed backend/viewer.py, backend/ui/{index.html,ui.css,ui.js}, backend/tests/test_viewer.py plus updated docs. Read-only 127.0.0.1 browser + schema-v1 SQLite, bid list/search/status/field/deadline/company filter, evidence drawer, timestamps, 7 themes, browser-local favorites. Snapshot stale by changed bid/profile revision downgrades old status to UNKNOWN pending review. Reuse existing backend instead of external service or rewriting legacy frontend; security/cost and low-maintenance favor this read-only local solution.

## 3. Test commands and verification results
Run in real full repo:
    cd backend
    python -m unittest discover -s tests -v
    node --check ui/ui.js
    python viewer.py --db ./demo.sqlite3 --port 8765

P1 Linux CPython 3.13.5 full suite on 2026-10-26: 96 PASS, 0 FAIL, 0 SKIP, synthetic PDFs 2 and XLSX 2 actually generated. P2 isolated tests in this session: 5 PASS, 0 FAIL; Python compile and Node syntax for local UI pass; static HTTP/JSON/query/Host/Origin and read-only verified with synthetic DB. Original P1 96 not rerun this session; combined 101 expected, not measured. Exact remote P2 checkout untested. Browser navigation and screenshots NOT VERIFIED: Chromium attempts to local/test URL twice ERR_BLOCKED_BY_ADMINISTRATOR, attributable to execution environment policy, not demonstrated application defect. Native Windows/Excel, real bid API/data, legal qualification, installation NOT VERIFIED.

## 4. Stage states and interruption point
Complete: P1 backend CLI modules. Partial: P2 BASIC browser integration (read-only UI/source committed; five isolated local tests passed; browser/Windows not validated). Pending: P2-02 cross-page favorites, in-app profile modification/assessment flow, true UI report action and a full integration/regression. Planned: P3 official API, P4 opt-in AI, P5 Windows release + security, P6 sales/legal checks. Public trademark/sales blocked until verified. Current session stops after P2-01 branch-only source plus docs and SHA check.

## 5. Failure evidence, root cause, prior attempts, avoid-repeat, alternatives
Browser attempt #1 Chromium to 127.0.0.1 -> ERR_BLOCKED_BY_ADMINISTRATOR. Materially changed attempt #2 using Playwright route on alternate host -> same ERR_BLOCKED_BY_ADMINISTRATOR. Stop repeating browser approaches in this environment; use Windows manual or external permitted browser as the next meaningful check. Initial original full private-repo clone previously unavailable by environment/DNS/auth: don't repeat unchanged approach; GitHub connector allows verified source reads/writes. Report generation and database writes are sequential, not atomic across files/DB: PDF failure may leave a valid DB snapshot; implement resumption later, don't falsely claim rollback.

## 6. Repo, branches, SHA and paths
Private repository https://github.com/hibi89/Bid_Owl, repo ID 1399359397. Source work branch feature/bid-owl-v1-basic-mvp. P2 source HEAD 2ff7a22082b2e37362d0935dee32fa292566eecb BEFORE doc changes. Current HEAD must be queried after this handoff update, not inferred from text. Main verified at session start c888c795bef72734f3f7016e54013b82453f11d8; legacy rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Paths backend/cli.py, backend/viewer.py, backend/bidowl/{schema,importer,profile,eligibility,store,report}.py, backend/ui/*, backend/tests/test_*.py. The new product is NOT on main.

## 7. Production URL/project/commands/environment
Legacy Vercel project name project08-bid-insight, id prj_YcrN7OdOjKl6M457HelGIItLeeXZ. Production URL, deployed SHA, actual HTTP/UI/API unverified and untouched; P2 local Python viewer not production deployable (N/A). Windows 11 intended target, Linux CPython 3.13.5 synthetic tests. Run python viewer.py --db <local-existing-v1-db> --port 8765 from backend and open http://127.0.0.1:8765 on the same PC; shut down with Ctrl+C. Existing CLI import sample in backend/README.md. Python 3.11+ target; no required hosted services for BASIC.

## 8. Original, backup, auth and no-change boundaries
Legacy education code preserved on main, branch isolated; rollback commit above. SQLite backup via store.backup_to disallows overwrite. All customer DB, bids, PDF/XLSX, keys, personal data, .env, system fonts must remain off GitHub. ReportLab BSD and system/NanumGothic fonts have licensing notes in backend/README. GitHub connected account hibi89; final author/committer and head check required. Do not modify main, Vercel link, domain, permissions, billing, production or public release without user approval. No secrets inside handoff.

## 9. Next steps with priority, acceptance, approvals
1) Reconfirm feature/main SHA and inspect newly committed exact remote viewer/ui files. Reconstruct full private checkout in authorized test environment and run full 101 expected Python suite, node syntax and synthetic CLI run; report measured actual.
2) P2-02 fix current-page-only favorites so all search results can be selected globally; compare a safe local SQLite favorites storage migration vs client-only read filter for reliability/cost before implement. Keep source DB safe and old assessments immutable.
3) Add safe UI profile editing/evaluation/import/export or practical CLI deep links; review threat model and backups before any write API. Make screen accurate about timestamps/status/data provenance.
4) Windows localhost browser UI E2E (desktop/mobile, seven themes, keyboard/contrast/console/network), real CSV and native Excel/PDF. Never confuse simulated with official data.
5) Update STATUS/HANDOFF after every completed major stage. P3 API key, paid AI, external uploads, Vercel production and public sale require explicit user approval. Completion requires actual working app beyond tests/commits.

## 10. Updated and checked KST, verification scope, source commit
Updated 2026-10-27 KST. Last observed P2 source commit 2ff7a22082b2e37362d0935dee32fa292566eecb; documentation commits follow it. This handoff's final HEAD SHA must be obtained from GitHub after the commit. Verified: GitHub connector source writes and locally isolated synthetic backend tests (5), previous recorded P1 96. Not verified: byte-for-byte full remote checkout test, live browser, Windows, production, official API/data, legal/trademark. Resume on ㄱ; follow NEXT_TASK.md first.