# BID OWL HANDOFF — P2-06 · 2026-10-27 KST

## 1. Product/goal/requirements and technical architecture
BID OWL/비드아울, private local-first Windows 11 SME public procurement screening. BASIC planned one-time KRW 59,000: CSV input, company profile, conservative PASS/FAIL/UNKNOWN plus sourced rule evidence, local SQLite, filters/favorites, PDF+XLSX and seven themes. PRO planned KRW 149,000 official procurement API with customer-issued key, on-PC-only updates; PREMIUM planned KRW 299,000 optional customer-model AI and profitability. No official eligibility/award guarantee. All prices/product brand unvalidated. Backend Python 3.11+/SQLite v1/ReportLab+local Korean TTF PDF/stdlib XLSX. UI localhost HTML/CSS/JS; NO remote user data uploads or paid services for BASIC.

## 2. Work done, changed files, alternatives and choice
Earlier P1 CSV/rule/evidence/revisioned SQLite/report CLI; P2-01 read-only localhost UI, P2-02 global favorites read-only POST, P2-03 company editing with backup-required CLI and browser JSON form, P2-04 transaction CAS/read-only preview/accessibility, P2-05 report re-export by historical assessment ID and synthetic end-to-end smoke.
P2-06 new source:
- backend/bidowl/report.py `write_xlsx`: after exclusive file creation, catch errors from sheet/XML/ZIP writing and unlink only the just-created broken XLSX. Existing filenames are untouched.
- backend/report_existing.py `export_existing`: if --format both successfully created XLSX and subsequent PDF fails, unlink the just-created XLSX sibling; PDF renderer handles own partial output. This is best-effort cleanup and does NOT guarantee atomicity across shutdown/power loss.
- backend/tests/test_report.py +1 test injecting late worksheet error; backend/tests/test_report_existing.py +2 tests PDF-after-XLSX failure rollback and pre-existing PDF untouched. All committed; runtime still unverified.
- backend/ui/index.html, backend/ui/ui.js: added "새 회사 프로필 만들기" onboarding form. Browser creates/downloads JSON with chosen profile ID, conservative null fields, list and numeric validation; operator must run CLI preview then explicitly `--create --apply --backup` to write. Existing edit flow unchanged. backend/tests/test_viewer.py extended existing UI test asserting both controls/instructions.
- backend/verify_local.ps1: simple on-user-Windows offline private checkout QA: run full unittests, synthetic smoke, then Node syntax if available; stops on nonzero exit; no user data or web services. backend/REPORT_REPLAY.md, NEXT_TASK.md, STATUS.md, HANDOFF.md refreshed.
Why: safer to retain a local explicit writer + mandatory backup than introduce an unrestricted HTTP mutation API. Cleanup on ordinary output exceptions chosen over full transactional file-system redesign; no claim of power-loss safety.

## 3. Tests with commands, measured PASS vs unverified, current source
From an authorized exact checkout, backend directory:
  `python -m unittest discover -s tests -v`
  `python smoke_local.py`
  `node --check ui/ui.js`
  Windows: `powershell -ExecutionPolicy Bypass -File .\verify_local.ps1`
  Saved synthetic assessment replay example: `python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./replayed_reports --format both` (need local ReportLab/font for PDF).
GitHub sources checked: **126 declared test methods** (eligibility27/importer21/profile workflow11/report21/report existing8/smoke local1/store28/viewer9). **126 NOT ACTUALLY EXECUTED; do not claim 126 PASS**. Previous P1 96 PASS/0 FAIL Linux on 2026-10-26 is old baseline, earlier isolated P2 tests and mock stores cannot be counted toward this branch's full suite. Exact GitHub ui.js V8 Function syntax parse PASS. Newly committed Python fault-injection tests, full end-to-end smoke, Windows script, browser and real XLSX/PDF generation NOT EXECUTED in this environment.

## 4. Current stage, progress/completed/in-progress/pending and stop point
P1 code complete. P2-01 through P2-06 features/source added and partial static validation; customer-ready integration and full Python QA pending. Product NOT ready for commercial shipping; profile creation/edit and report replay still require explicit local CLI, no one-click mutating web app. Next P2-07 is full 126-test integration, fix failures, offline smoke, Windows/Excel/PDF/browser visual checks, 10k-bid search and crash recovery. Then P3 official API, P4 optional AI, P5 Windows installer/security, P6 trademark and public sale. Stop at after HANDOFF and final branch HEAD identity checks.

## 5. Failures, symptoms/causes, prior attempts and alternatives
Private GitHub full checkout failed from Python container because git clone/private auth/DNS; signed raw.githubusercontent.com and api.github.com DNS unavailable. GitHub connector successfully reads/writes sources but cannot directly materialize all files into container. Do not repeat unchanged method; do not test old /mnt/data stand-in and present result as current branch 126 PASS. Previous Chromium 127.0.0.1 attempts failed ERR_BLOCKED_BY_ADMINISTRATOR due environment restriction; not evidence of app flaw. Authenticated private Windows checkout or approved execution runner is correct alternative. Python tests committed via connector remain unexecuted. Multi-file report outputs and sequential SQLite reassessment remain non-atomic for crash/power loss, backups + manual recovery required. Avoid silent auto-restore.

## 6. Repo, branch SHA, changed files and git identity
Private repo https://github.com/hibi89/Bid_Owl id 1399359397. Feature branch feature/bid-owl-v1-basic-mvp; P2-06 start SHA 4c7cdcb169cf1fb68f4ea9f4f63dd91bfad15341. This turn code commits: 1faf1c28eb60062c66e13784dc430e81acbdd354 (XLSX cleanup), af65899e8e461a469035d49618dd2ee396a6bc2e (both-format cleanup), 38fec7a6d3f704a5d65f385bd573bcf5ca9ca914 (+2 tests), b54daf628cebe449b83b625cae629f26fa1bc0ae (+1 test), c61a187c5f010a7220c91455003154d4bdfdc731 (HTML), f7319569a822847d5c54e1c5a0d2f6c625ab2caf (JS create profile), 72972e9c19916bf783b07323ef108482f059ab2f (static UI test), 080c2e511d3389939316bdcb6c37e58165aa9ba0 (Windows QA helper); docs follow. Pre-HANDOFF STATUS commit f1e50c5a98a7b576bf334b13ddaaa7ecff95f813. Query current HEAD after this HANDOFF commit. Main baseline c888c795bef72734f3f7016e54013b82453f11d8 (no main writes). Old original legacy rollback SHA 2807a93a3e0deba98840712401fdd6025e6f5610.
Paths: backend/bidowl/report.py, backend/report_existing.py, backend/tests/test_report.py, backend/tests/test_report_existing.py, backend/tests/test_viewer.py, backend/ui/index.html, backend/ui/ui.js, backend/verify_local.ps1, backend/REPORT_REPLAY.md, NEXT_TASK.md, STATUS.md, HANDOFF.md.

## 7. Production URL/Vercel state, run commands and environment
New Python localhost tool not deployed (N/A); `python viewer.py --db ./demo.sqlite3 --port 8765` binds 127.0.0.1, navigate http://127.0.0.1:8765 on same PC. Production original legacy Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched; deployed URL/live SHA/HTTP unverified. Windows 11 actual browser/native Excel and PDF, licensing/font embedding NOT rechecked. `verify_local.ps1` committed but not run. All smoke data synthetic and temp-only.

## 8. Originals, rollback/backups, secrets, permissions and scope
Main's 2025 education static demo with its historical 340/340 QA and old countdown unrelated to BID OWL actual QA. No main/force push/history alteration, no Vercel changes or deployment, no paid service, no domain/permissions modifications. All customer SQLite/CSV/docs, PDF/XLSX, secrets, .env, official API keys and font files stay local, never uploaded to GitHub. SQLite backup_to refuses overwrites, profile CLI requires apply+new backup; reports avoid overwrite and catch ordinary export failure. Connected GitHub writing identity hibi89; re-check final HEAD commit author/committer. BID OWL KIPRIS mark clearance unknown. No external upload or release without user approval.

## 9. NEXT P2-07 acceptance, dependencies and approvals
1) Get authorized exact private repo checkout from an environment with GitHub access, then run real **126 tests**, `python smoke_local.py` and JS syntax command (use Windows helper). Record actual counts and fix failures. Include injected XLSX/PDF cleanup, create-profile UI JS logic, read-only local APIs and profile version CAS. Never infer PASS from test source definitions.
2) Real offline Windows 11 Chrome/Edge visit, 7 themes, new company profile JSON Blob download/CSP, keyboard/focus/accessibility, synthetic PDF with locally licensed Korean TTF, XLSX Excel inspect, 10k-bid benchmark. Verify backups and interrupted runs on synthetic copies before customer databases.
3) Improve BASIC UI report export (no write API without auth/CSRF/security review) and company onboarding usability, decide install approach and real CLI user ergonomics.
4) Later P3 PRO official key/API and external network, P4 PREMIUM opt-in AI, P5 Windows packaging, P6 KIPRIS/trademark and public sale gate need their own approvals; no production/main modifications until explicit user approval.

## 10. Final date, verification evidence and continuation
Updated 2026-10-27 KST. GitHub source inspection confirmed 126 test definitions and V8 parsing of exact remote JS; Python full suite/browser/Windows/official data NOT VERIFIED. Final feature HEAD commit is produced by this HANDOFF update and must be fetched before reporting. User ㄱ continues P2-07.
