# BID OWL — HANDOFF (2026-10-26 KST)
Resume prompt: [Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]; ㄱ means proceed with next incomplete unit, no repeat questions for confirmed choices.

## 1. Goal / requirements / stack
Brand BID OWL (비드아울). Windows 11 locally installed procurement evaluation tool; not automatic bidding or legal guarantee. BASIC 59,000 KRW: CSV/profile/rules PASS-FAIL-UNKNOWN/provenance/report. PRO 149,000: official public procurement API corrections/incremental updates and PC-running-only notifications. PREMIUM 299,000: optional customer-provided AI API, PDF/DOCX extracted provenance, profit simulation. One-time purchase and zero recurring mandatory fee TARGET, not validated. Python/SQLite with eventual reuse of static HTML/JS/CSS and 7 themes (cloud, obsidian, midnight, graphite, emerald, sand, iris). More in REQUIREMENTS.md, ROADMAP.md, PRODUCT_AND_COST.md.

## 2. Completed features / changes / decisions
2025 educational PWA has static 20-item demo, simulated scores, 340/340 displayed QA and fixed 2025 deadline fields; NEVER present these as actual product tests. main preserved. P1-01 built in feature: Python schema/importer parsing strict CSV, provenance, conditional rules, source metadata, duplicate/empty/date/budget/errors, max limits and whole-file failure. Design choice: malformed imports never yield partial accepted bids. Real bidding/legal interpretation awaits human review. Changed paths: backend/bidowl/schema.py, importer.py, __init__.py, backend/fixtures/sample_bids.csv, backend/tests/test_importer.py, backend/README.md, NEXT_TASK.md, STATUS.md, HANDOFF.md.

## 3. Tests / pass-fail / verification
Run from backend: python -m unittest discover -s tests -v. Linux CPython 3.13.5: 21 PASS, 0 FAIL, 0 SKIP. Sample fixture 2 synthetic bids loaded, 1 past deadline. Git blob sha for four source/test files equals local tested version. GitHub sample CSV UTF-8 versus local generated UTF-8-SIG; remote sample not separately executed. Windows real run, actual government CSV and end-to-end full system are NOT VERIFIED.

## 4. Completed / in-progress / pending / blocked
Completed P1-00, P1-01. Next P1-02 profile/evaluator and tests. Pending P1-03 SQLite, P1-04 reports/CLI, P2-BASIC UI, P3-PRO, P4-PREMIUM, P5 Windows QA, P6 sales. Brand release, actual public API keys/terms, Windows install and optional external AI need verification/approvals.

## 5. Errors / causes / attempts / do-not-repeat / alternatives
Initial test_missing_header had incorrect fixture (removed an optional rather than required field), giving one failing test. Corrected input removed budget; rerun 21/21 PASS. No need to repeat broken test fixture. Do not alter legacy app to hide its static-data problem; implement independent verified engine. Real Windows testing awaits accessible environment; if unavailable use Python unittest and mark NOT VERIFIED.

## 6. Repo / branch / SHAs / paths
Repo https://github.com/hibi89/Bid_Owl (private, id 1399359397). main c888c795bef72734f3f7016e54013b82453f11d8, unchanged. Feature branch feature/bid-owl-v1-basic-mvp. P1-01 code commit 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b. Final doc commit = later HEAD; query GitHub on next resume. Legacy backup/restore snapshot 2807a93a3e0deba98840712401fdd6025e6f5610. Next focus backend/bidowl/{profile,eligibility}.py and backend/tests/test_eligibility.py.

## 7. Production / Vercel / execution / environment
Legacy Vercel project project08-bid-insight, ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ. Prior READY metadata seen, but actual URL, Git rename connection, Production SHA, HTTP/browser/API behavior NOT VERIFIED. New Python changes were NOT deployed: deployment non-applicable to this implementation. Current run: from backend, python -m unittest discover -s tests -v; python -c "from bidowl import load_csv; print(len(load_csv('fixtures/sample_bids.csv')))". Python 3.13.5 Linux validated, Windows 11 untested.

## 8. Original / backup / credentials / modifications forbidden
Main branch holds original educational app and fixed test data. Never push user bid files, real CSV/PDF, API keys, .env or SQLite files. User-approved work isolated on feature, no force push, no changes to Vercel/production domain/authentication/rights. GitHub connected identity hibi89 with author/committer mapped correctly. Original legacy restore SHA above.

## 9. Next priorities / steps / completion / approvals
1) Re-read live GitHub feature HEAD and NEXT_TASK then implement P1-02 profile, eligibility. Values absent -> UNKNOWN; source missing/unknown kind -> UNKNOWN; any FAIL dominates, otherwise UNKNOWN dominates, else PASS. Zero requirement case UNKNOWN.
2) Test profile changes, source traceability, multiple rules; run local Python tests; commit feature and compare remote source SHA; update this handoff/STATUS.
3) P1-03 transactional SQLite and P1-04 actual PDF/Excel/CLI; later only deploy/publish if approved.
External API keys/costs/data transmission/public brand sales/production alterations require explicit user approval. Default choices already ratified; do not ask again.

## 10. Timestamp / verification scope / document baseline
Updated 2026-10-26 KST based on GitHub main c888c795bef72734f3f7016e54013b82453f11d8 and verified code commit 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b. Current handoff is subsequent docs commit; its own SHA cannot be embedded before commit, so verify live branch HEAD. Only local test/GitHub code hashes verified; actual Windows/Production/server/API untouched or unverified. Startup order HANDOFF -> STATUS -> AGENTS -> REQUIREMENTS -> NEXT_TASK -> code.
