# BID OWL HANDOFF — 2026-10-27 KST, P2-03

## 1. Goal, purpose, confirmed requirements and technologies
Private local-first Windows 11 procurement assessment product, BID OWL / 비드아울. BASIC (planned one-time KRW 59,000) validated CSV, editable company profile, 3-state evidence-carrying rule screening, local SQLite, Excel/PDF, seven-theme web app. PRO planned KRW 149,000 official Korean procurement API user-key updates only while PC on; PREMIUM planned KRW 299,000 opt-in user-model AI and profitability inputs. Pricing not validated. Never claim qualification/award guarantee. Python 3.11+, SQLite v1, ReportLab, stdlib XLSX, HTML/CSS/JS, no mandatory server/subscription.

## 2. Completed implementation, changes and decision reasons
Earlier P1-01 strict importer, P1-02 PASS/FAIL/UNKNOWN rules/provenance, P1-03 immutable SQLite profile/bid/assessment versions with non-overwriting backup, P1-04 CLI/PDF/XLSX. P2-01 local readonly SQLite GET server, responsive seven-theme browser list/details and date/condition filters. P2-02 globally paginated browser-local favorites through bounded same-origin JSON POST that **does not write**. New P2-03:
- backend/profile_workflow.py: dry run by default; validate profile JSON before writable DB; explicit --apply + existing version match + mandatory newly created backup before modification; --create optional; --reassess optional, up to 10k saved bids. Old profiles and assessment versions persist. Multi-bid progress is sequential; partial writes are reported with retained backup, no false full rollback.
- backend/viewer.py: GET /api/profile read from SQLite current profile_versions.
- backend/ui/index.html, ui.js, ui.css: human can edit current profile fields in a form and download JSON; browser itself CANNOT apply to DB. Local CLI preview/apply is explicit. Null vs [] remains distinct; no HTML insertion of user data; no external uploads.
- backend/tests/test_profile_workflow.py eight unit test methods, backend/tests/test_viewer.py one additional method; README, STATUS, NEXT_TASK and HANDOFF updated.
Design comparison: browser writable endpoint would improve convenience but add CSRF/access control/backup transaction risk; CLI editing has some user friction but preserves existing readonly HTTP security, chosen for current phase. Full commercial one-click interface remains unfinished.

## 3. Test command, pass/fail, verified/unverified
Run after authenticated full repo checkout:
    cd backend
    python -m unittest discover -s tests -v
    node --check ui/ui.js
    python cli.py --csv fixtures/sample_bids.csv --profile fixtures/sample_profile.json --source-id SYNTHETIC-CSV --db ./demo.sqlite3 --output ./reports --format both
    python viewer.py --db ./demo.sqlite3 --port 8765
    python profile_workflow.py --db ./demo.sqlite3 --profile-file ./edited-profile.json --expected-version 1 --reassess
    python profile_workflow.py --db ./demo.sqlite3 --profile-file ./edited-profile.json --expected-version 1 --reassess --apply --backup ./new-backup.sqlite3

Previously P1 actual Linux: 96 PASS/0 FAIL; P2-01 isolated 5 PASS/0 FAIL. Current combined expected test count 112 (96 + 8 viewer + 8 workflow), **FULL 112 NOT EXECUTED**, so no pass claim. This turn independently verified Github exact profile_workflow.py bytes match git blob SHA a8ac6a204edcbf8afde904391d4f51c53f12876f, Python ast parse PASS, **seven isolated mock SQLite-store smoke tests PASS/0 FAIL** against the same code. This is not real BidOwlStore test. Exact remote ui.js syntax parse PASS through V8 Function constructor. New committed unittest cases NOT EXECUTED; actual browser DOM, Windows and real official data NOT VERIFIED.

## 4. Stage completion, progress, pending, blocker/stop
P1 backend source complete, P2 source implementation progressing, P2-03 source committed and mock verified only. Need P2-04 full integrated tests, real SQLite backups/assessment preservation, browser desktop/mobile 7 themes, CLI UX and Windows. Later P3 API, P4 AI, P5 installer/security, P6 brand/sales. Current stop after this GitHub HANDOFF and final SHA checks. User ㄱ means continue P2-04 automatically.

## 5. Errors, causes, attempts, forbidden retries, alternatives
Private repo clone and later signed raw.githubusercontent.com download failed DNS/auth resolution in previous sessions. GitHub connected API READ/WRITE works; don't repeat same private download command with identical environment. Full Python integration currently blocked; use permitted authenticated checkout and execute full suite. Previously Chromium local + routed host blocked with ERR_BLOCKED_BY_ADMINISTRATOR; don't infer product defect, test on user Windows/local authorized browser. UI Blob download CSP and local CLI process not browser tested. SQLite commits assessment one-by-one after a consistent backup; if failure, manual review/restore required; automatic rollback unsafe. Avoid claiming atomicity, browser proof or real customer qualification.

## 6. Repository, branch, SHA, paths
Private https://github.com/hibi89/Bid_Owl, repo id 1399359397. Feature branch feature/bid-owl-v1-basic-mvp. P2-03 main source commits: 6d631fcb9db441a94a6c14dacc10737758e516df (profile_workflow.py); f1c186ea94c43a73f615f0042ac9a043cb1ac595 (tests); 0c24e5b28a8990d42e3cba127a908c5898f63944 (readonly endpoint); b259367de2e81a5555a12e6cd7ecbb4107d1f2e2 (HTML); f787968ee9fa4904fb0709b8e5ba793bac191cd1 (JS); 5beaaddcbdd016fce953f1c7d82b246399ffea22 (CSS); 07be1bff2e60776bfd76390c77f2f2c0e752c993 (viewer test). Latest pre-handoff STATUS commit 54844ec5f591722f464f4e16f3094cca3db73f0c; confirm final HEAD after writing. Main previously at c888c795bef72734f3f7016e54013b82453f11d8, untouched this session; rollback legacy original 2807a93a3e0deba98840712401fdd6025e6f5610. Paths backend/profile_workflow.py, backend/viewer.py, backend/ui/{index.html,ui.js,ui.css}, backend/tests/{test_profile_workflow.py,test_viewer.py}, backend/bidowl/store.py, backend/cli.py.

## 7. Production URL, Vercel, run commands and environment
Legacy Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ. Existing production URL/SHA/live HTTP/React browser NOT checked; no changes to legacy Vercel. New feature Python localhost application NOT deployed (N/A). Run Python viewer from backend on Windows: python viewer.py --db ./demo.sqlite3 --port 8765 then http://127.0.0.1:8765. Run profile_workflow CLI locally with explicit --backup for apply; actual Windows 11 and native Excel not tested. Local 127.0.0.1 only; API user data never transmitted.

## 8. Originals, backup, authentication and prohibited modifications
Original static school demo remains on main; old QA 340/340 and 2025 metrics are NOT new product proof. Local user DB and generated report inputs are private; no DB, PDF, Excel, font files, credentials, secrets, .env, tokens pushed. Backup CLI creates a new independent SQLite snapshot via existing backup_to and refuses overwrite. User must inspect partial failure before manual restore; historical snapshots preserved by existing store. GitHub writer connected hibi89; final commit author/committer must be checked. Do not change main, Vercel, permissions, production, domains, billing, customer file, or launch without approval. Brand KIPRIS/BiddingOwl similarity not legally cleared.

## 9. Next actions, order, success criteria, approval needs
Next P2-04:
1) Fetch verified fresh feature/main SHA and source, run full **112 expected** repository Python tests, Node check, synthetic CSV -> SQLite -> real PDF/XLSX, HTTP/JSON/favorites/profile endpoint and profile backup/apply/reassessment through actual store. Determine actual PASS/FAIL count and address bugs first.
2) Test user profile JSON form download + commands; verify no unintended HTTP mutation/egress, stale results UNKNOWN, historical evidence and backup restoration, SQL injection, same-origin, 1MiB limits.
3) Run Windows 11 Edge/Chrome, mobile responsive/keyboard/7 theme visibility and PDF/Excel, 10k-bid performance, crash/resume.
4) Decide after review whether to implement optional authenticated one-click local edit UI; this extends write surface and needs security/backup/CSRF approval. No production deploy, API key use, paid external service, brand/public sale without approval. Record STATUS/HANDOFF after milestone.

## 10. KST updated/checked, validation scope and source baseline
Updated 2026-10-27 KST, prior session source baseline feature SHA 148d51eec12002c491e19862b27e364be2c7fd51. Final HANDOFF commit is the next GitHub write, query actual HEAD and author after. Only byte-matched CLI Python syntax/7 mock tests and JS syntax verified this session; full 112 in private repo, browser, official external data, Windows/Production and legal clearance remain UNVERIFIED.
