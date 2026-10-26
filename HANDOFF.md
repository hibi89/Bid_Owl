# BID OWL HANDOFF — P2-05 · 2026-10-27 KST

## 1. Purpose, requirements, technology and verified scope
BID OWL / 비드아울 is a Windows 11 localhost procurement screening tool for SMEs. BASIC planned 59,000 KRW one-time: CSV, local profile, sourced conservative PASS/FAIL/UNKNOWN, evidence detail, favorites/search, 7 themes, historical XLSX/PDF. PRO planned 149,000 KRW official government procurement API with customer key and on-PC monitoring; PREMIUM planned 299,000 KRW optional customer-key AI and financial sensitivity. Not officially qualified, no bid success guarantee. Prices, use of BID OWL brand, legal data interpretation and public sale not approved/verified. Python 3.11+/SQLite schema v1, ReportLab Korean PDF, stdlib XLSX and offline CSS/JS.

## 2. Changes, completed features, options/decision
P1 source: importer, rule engine, versioned SQLite, CLI PDF/XLSX. P2-01 localhost read-only viewer, P2-02 global favorites, P2-03 local JSON profile editor+explicit backed-up apply CLI, P2-04 read-only preview/CAS profile race protection/SQL detail key and keyboard dialog.
P2-05:
- backend/report_existing.py: export already persisted assessment ID through readonly SQLite URI mode=ro/query_only into XLSX/PDF without CSV re-import, re-evaluation or DB mutation; refuse overwritten output paths; report uses original bid/profile revisions and saved evidence, warns historical status not current legal decision.
- backend/ui/ui.js: display actual saved assessment ID, format-both CLI command and stale evidence warning in detail drawer. No browser DB-write capability, no new remote endpoints.
- backend/tests/test_report_existing.py: 6 synthetic test methods for XLSX structure/no DB mutation, immutable earlier vs later status, no overwrite, missing ID, readonly connection and CLI exit. backend/smoke_local.py: one-command disposable synthetic end-to-end import->SQLite->XLSX->HTTP API/favorites/profile->old assessment replay->versioned profile dry-run+backup/apply/reassess->historical preservation; backend/tests/test_smoke_local.py one test.
- backend/REPORT_REPLAY.md, NEXT_TASK.md, STATUS.md, HANDOFF.md documentation.
Choice: rather than triggering another CLI import/re-evaluation to get a report or adding unsafe writable HTTP endpoint, replay saved historical assessment via read-only local operation. Cost 0 additional mandatory API and preserves audit history. UX remains CLI-assisted, not yet one-click commercial UI.

## 3. Commands and measured vs unverified tests
Run on an authenticated actual full repository checkout from backend:
    python -m unittest discover -s tests -v
    python smoke_local.py
    node --check ui/ui.js
    python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./new-reports --format both

New smoke uses fixture-only synthetic data and a temporary directory, and checks HTTP endpoints, profile history and backup. It deliberately exercises XLSX not PDF (doesn't require ReportLab/font) and no external API. The GitHub current source includes **123 declared test methods** across 8 files (21 importer +27 eligibility +28 store +20 report +9 viewer +11 profile workflow +6 report existing +1 smoke). **123 NOT EXECUTED OR PASS-VERIFIED** in this turn. Historical P1 96 PASS Linux CPython 3.13.5 on 2026-10-26 and P2 isolated prior smoke cannot count as present branch QA. GitHub fetched exact current ui.js parsed by V8 Function (PASS); source/test files and GitHub commits checked. Python runtime and real HTTP/XML report flows in the new modules still unmeasured. Windows/Chrome/Edge, actual PDF/Excel application, security scan, KIPRIS and real tender data not tested.

## 4. Stage status/stop point and next gate
P1 code complete with older independent tests. P2-01..05 source implemented; global integrated E2E blocked by sandbox/private GitHub checkout. Current stop after P2-05 GitHub commits/docs. P2-06 next: execute real 123 Python tests and the synthetic smoke in authorized checkout, fix failing tests and verified bugs, real Windows browser/Excel/PDF and 7 themes, 10k list/detail benchmark and local report export UX; then P3 API, P4 AI, P5 installer, P6 public branding/sale clearance.

## 5. Failures, explanations, attempts/avoid-repeat/alternatives
Private full git clone earlier failed auth/DNS. Signed raw.githubusercontent.com download also DNS unresolved, and api.github.com DNS in local Python check cannot resolve; no full private repo physically mounted. GitHub connector successfully reads/writes actual repo source, but cannot copy its private files into the Python container directly in this environment. Don't run old /mnt/data/bidowl_p2 stand-in and claim current GitHub test success. Browser previous Chromium attempts at 127.0.0.1 / alternate host blocked ERR_BLOCKED_BY_ADMINISTRATOR, platform policy not proof of broken UI; try Windows local Edge/Chrome or authorized runner. Historical multi-assessment writes and dual-format file exports are not one atomic transaction; partial failures require manual inspection and backups, never promise automatic all-or-nothing rollback.

## 6. Repository, HEADs, commits and files
Private https://github.com/hibi89/Bid_Owl ID 1399359397. Feature branch feature/bid-owl-v1-basic-mvp starting SHA 6f2cd7652d0f9284402f7528c8a0c2c2ec1fd531. This session source commits: f7c7efd6dc4a1f46b7f896b15e2f8252abc8d277 report_existing.py; 6519db7999b5193106de8c889fe7b8a7a93f23fc report tests; 2d8cf59e1fc0a32f7c517200a9568e68711ca8c8 ui.js; 69dac4f07602fe9f2cd3384f5f9669963ae10875 smoke_local.py; 63d3442857c8b8e4e206d9557976687d39758904 smoke test; aaf22d6f4f5ef02af8648334711308bff42903ee REPORT_REPLAY.md. Pre-handoff STATUS e607416657cdb8078e754735a593975273c9a76b. Final HEAD must be queried after HANDOFF write. Main previously c888c795bef72734f3f7016e54013b82453f11d8, no main writes; old legacy restoration SHA 2807a93a3e0deba98840712401fdd6025e6f5610. Core source backend/bidowl/*.py; local backend/viewer.py, cli.py, profile_workflow.py, report_existing.py, smoke_local.py, ui/*; tests/*.

## 7. Production, URLs, execution/environment
Legacy Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ unchanged; Production live URL/deployed commit/HTTP unverified; new product Python local loopback deployment N/A. Run from backend directory: `python viewer.py --db ./demo.sqlite3 --port 8765`, open http://127.0.0.1:8765; `python smoke_local.py` for temp synthetic check. Existing customer DBs only local Windows appdata; no cloud services required for BASIC. User must manually select report output folder and profile JSON backup, cannot claim seamless app yet.

## 8. Legacy/original, backup/auth boundaries, data safety
Original 2025 educational Vercel static demo on main intact, 340/340 static UI QA and 2025 countdown NOT new product evidence. New code only feature branch, cannot force push or overwrite originals. SQLite backups non-overwriting; report files also non-overwriting, earlier assessments immutable. No customer records/SQLite, PDFs, XLSX, credentials, fonts, API keys, .env or secrets uploaded to GitHub. Connected GitHub write account hibi89; recheck latest commit identity and branch. Do not alter main, Vercel, DNS, GitHub access permissions, paid subscriptions, external transfers or public marketing without explicit user approval. BID OWL KIPRIS/legal name unresolved.

## 9. Next steps, acceptance, approvals
1) Obtain permitted authenticated exact repo checkout, run `python -m unittest discover -s tests -v` (expected 123 tests), `python smoke_local.py` and `node --check ui/ui.js`. Record ACTUAL counts/error details, fix and rerun. Verify synthetic source always uses temp folder and original DB is untouched.
2) Real PDF with ReportLab and locally licensed Korean TTF, inspect Excel/PDF; verify report ID history, no overwrite, no DB mutations and no external egress. Verify actual multi-format export error recovery.
3) Actual Windows 11 Edge/Chrome desktop/mobile widths with 7 themes, contrast/focus and Blob JSON download; 10,000-bid search/detail perf metrics; profile optimistic locking and after-conflict recovery.
4) If wanting one-click UI report/edit, evaluate GET report binary streaming or signed same-origin UI write route with auth/CSRF/backup after security design and explicit user approval. Do not silently enable mutation API. Only after tests consider P3 official API. Public sale requires brand KIPRIS and customer expectations alignment.

## 10. Checked date, evidence and current HEAD recording
2026-10-27 KST. GitHub source and UI V8 syntax/declared test count measured; 123 execution status NOT VERIFIED and all new Python E2E flows remain unproven until proper runner. Current feature HEAD is this HANDOFF GitHub update's commit; query and store actual SHA before final user response. User ㄱ resumes P2-06.
