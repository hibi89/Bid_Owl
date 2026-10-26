# BID OWL HANDOFF — 2026-10-27 KST (P2-02)

## 1. Goal, final requirements, architecture
BID OWL local-first procurement screening tool for Windows 11 small businesses. BASIC planned KRW 59,000 one-time CSV/profile/evidence-backed PASS/FAIL/UNKNOWN/Excel/PDF/local web UI; PRO KRW 149,000 optional user-key official procurement incremental API and PC-on alerts; PREMIUM KRW 299,000 opt-in user-model AI and cost scenarios. No paid required monthly subscription target, pricing not proven. Not a legal qualification/award guarantee. Python 3.11+ stdlib and ReportLab, SQLite revisioned snapshots, existing static HTML/JS/CSS parts, seven themes. Old 2025 educational demo values/340/340 not product QA.

## 2. Completed functions, changed files and design reasons
P1-01 CSV strict input, P1-02 conservative rules/evidence, P1-03 versioned SQLite/backup, P1-04 local CLI PDF/XLSX completed earlier. P2-01 local viewer: readonly SQLite / GET APIs / responsive UI seven themes, search filters/evidence, browser favorites. P2-02 this session:
- backend/viewer.py: query_bids accepts optional favorite_keys, global filtering happens BEFORE paging; new query_favorites validates 1,000 favorite pairs and only whitelist filter keys; POST /api/bids/favorites is **strictly read-only** with exact Host/Origin, JSON-only, 1 MiB cap, SQLite mode=ro. No DB migration/write/mutation.
- backend/ui/ui.js: when only-favorites mode, sends JSON pairs and filters; server returns globally accurate total/page and query; auto-correct page if final favorite deleted; max 1,000 saved IDs; existing localStorage only. HTML and seven themes unchanged.
- backend/tests/test_viewer.py: 2 new tests for global multi-page results, combined status filter, malformed input, body/origin/host content-type limits, no DB writes.
- backend/README.md, NEXT_TASK.md, STATUS.md, HANDOFF.md refreshed.
Alternative 1 client fetch every page: high number of requests; rejected. Alternative 2 SQLite mutable favorites table: durable but schema migration, backup and new mutation CSRF risks; postponed. Chosen browser-local + read-only bulk lookup reduces cost and intrusion.

## 3. Test commands, pass/fail and verification gaps
Full repo commands:
  cd backend
  python -m unittest discover -s tests -v
  node --check ui/ui.js
  python cli.py --csv fixtures/sample_bids.csv --profile fixtures/sample_profile.json --source-id SYNTHETIC-CSV --db ./demo.sqlite3 --output ./reports --format both
  python viewer.py --db ./demo.sqlite3 --port 8765
Previously P1: 96 PASS / 0 FAIL / 0 SKIP with Linux CPython 3.13.5; 2 synthetic PDFs + 2 XLSX generated. Previous P2-01: isolated 5 PASS / 0 FAIL. This P2-02 session: added two test methods, not executed. Expected total 96+7=103 but **103 PASS is NOT claimed**. Actual GitHub JS content parsed successfully with Function compiler; new Python helper snippet locally ast.parse PASS (not exact full module). GitHub blob fetch confirms changed files. Full actual branch checkout test, Python runtime, POST HTTP new regression, browser rendering, Windows 11, native Excel, official data and legal interpretation remain UNVERIFIED.

## 4. Status, in progress, pending, blocked and stop location
Source P1 completed; P2-01 partially verified; P2-02 code+tests committed but integrated execution pending. P2-03 next: verify full 103 expected tests, synthetic CLI-to-UI smoke and safe company-profile editor/assessment workflow; responsive/a11y/7-theme real browser and Windows smoke. P3 official procurement API, P4 AI, P5 installer/security, P6 brand/sales later. Public launch blocked pending KIPRIS/trademark and real-product tests. Stop after documentation update/feature HEAD check.

## 5. Failures/evidence/cause/attempts/do-not-repeat/alternatives
Old repo checkout attempt failed GitHub access/DNS/auth in this restricted sandbox. Current improved single-file private signed raw download attempted via curl with GitHub-generated link; failed `curl: (6) Could not resolve host: raw.githubusercontent.com`. No benefit repeating same environment. GitHub connected API succeeds read/write; use a permitted authenticated checkout on another environment to execute full test suite. Prior real Chromium local URL and alternate host both blocked by ERR_BLOCKED_BY_ADMINISTRATOR; cannot infer app runtime failure. Avoid more identical attempts; Windows local browser or approved browser environment is practical path. SQLite assessment commit vs PDF filesystem export is not atomic; failures can leave stored assessment with missing report. No unverified success assertion.

## 6. Repository, branches, commit SHA and paths
Private https://github.com/hibi89/Bid_Owl, repo ID 1399359397; feature/bid-owl-v1-basic-mvp. Starting HEAD 1cfb8f54304a47f3604010ed4e4c86b2eeb505f1. P2-02 code SHAs 016ab8c251f92628e17ccd6e102b374284d20608 (viewer), 823edf48d31ed0077cdd0c700f20594f59b44b68 (JS), cd05d6d56daf6613c7f7ebe11c558a60f3cfe7d9 (tests). Documentation followed; last pre-handoff STATUS commit 648f83dda7192da2ef8b967e4a2a76631e685353. Final feature HEAD will be this handoff update; re-read GitHub for actual SHA. Main baseline c888c795bef72734f3f7016e54013b82453f11d8, legacy rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Paths backend/viewer.py, backend/ui/ui.js, backend/tests/test_viewer.py, backend/bidowl/*.py, backend/cli.py and docs.

## 7. Production URL, Vercel status, run commands and environment
New Python local viewer not deployed; deployment N/A. Existing legacy Vercel project project08-bid-insight, ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ, unchanged. Existing Production URL/SHA/status/HTTP browser not re-verified. Local-only run from backend: `python viewer.py --db ./demo.sqlite3 --port 8765`, browse http://127.0.0.1:8765; Ctrl+C stops. Python 3.11+ target; validated P1 on Linux 3.13.5 previously, Windows not validated. No external API server or customer-key requirement for BASIC.

## 8. Source locations, backup, secrets, do-not-modify scope
Original legacy static education code still on main; preserve unchanged and rollback references. SQLite in user local application data, backup_to creates a consistent new backup and refuses overwrite. Customer bids/DB, documents, .env, API keys, reports, system fonts must never be uploaded to GitHub. Github linked writer hibi89; check commit identity and final SHAs. No force push/history alteration; no new paid services, permissions, production deployments, domain, user file edits or external data transmission without approval.

## 9. Next priority, procedure, success criteria, approvals
1) Reconfirm latest HEAD and docs, then full private checkout in permitted runner and run expected 103 tests (actual count/results must be reported); inspect failed new POST tests, UI JS, synthetic CLI->HTTP->favorites. Recheck both branch SHA and commit identity.
2) Plan/implement approved local company profile editing with safe input validation, explicit user actions, backup/revisioning, CSRF and no external transmission; preserve P1 historical assessment snapshots and add tests. Compare CLI extension vs new UI mutation surface before code changes.
3) Real Windows 11 Edge/Chrome, responsive PC/mobile keyboard/7 themes, reports open with Excel/PDF, error/no-profile, stale/expired, large-record performance, local-only network exposure. Verify actual, do not infer from code.
4) Update STATUS/HANDOFF after next major work; no main/Vercel/public release changes without approval. P3 keys/external operations/paid AI require approval.

## 10. Updated time, evidence range, and documentation source commit
Updated 2026-10-27 KST. GitHub actual source P2-02 commits listed in section 6; final HANDOFF commit and author to be re-queried immediately after saving. Prior 96+5 test evidence belongs to earlier sessions, only actual JS syntax and new helper isolated ast.parse were measured this time. No full current integration/browser/Windows/official API verification. Resume with ㄱ and NEXT_TASK.md.
