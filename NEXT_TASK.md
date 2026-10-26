# BID OWL NEXT_TASK — P2-09 · 2026-10-27 KST

Private repository hibi89/Bid_Owl; changes ONLY on feature/bid-owl-v1-basic-mvp. User ㄱ means read latest HANDOFF/STATUS/AGENTS/REQUIREMENTS/NEXT_TASK + current source/main HEAD, then continue. No main/Vercel/production/external API/payment changes, no customer uploads without approval.

## Scope/source already implemented
P1 strict CSV, evidence-backed PASS/FAIL/UNKNOWN, revisioned SQLite/backups and CLI XLSX/PDF. P2-01 readonly localhost UI + 7 themes; P2-02 global favorites; P2-03 backed-up CLI profile edit/reassessment plus browser JSON export; P2-04 SQLite CAS and safe detail lookup; P2-05 immutable report replay and disposable synthetic smoke; P2-06 non-overwriting interrupted-output cleanup and new-profile JSON onboarding; P2-07 single-click read-only historical Excel download; P2-08 300-char Korean ID query support, profile-version pinning during batch reassessment, truthful backup/partial-write errors.

## P2-09 actual new code/docs
- NEW backend/benchmark_local.py creates **disposable synthetic SQLite only** under TemporaryDirectory, never touches user/customer DB or external services. Default `--records 10000 --assessed 200` imports Bid objects, saves synthetic profile + first 200 assessments, measures wall-clock ms using perf_counter for import, subset evaluation, first-page list, category/text filter, exact detail, one favorite across all sources. Verifies selected counts and mode=ro/query_only rejects writes; prints JSON including DB size, timings, disclaimer. The "import" metric starts after creation of in-memory Bid objects, and this is NOT a full 10k CSV parser/Excel/PDF/browser benchmark.
- NEW backend/tests/test_benchmark_local.py (3 small tests): 31-row workload, 1-row zero-assessment edge, invalid count/bool input boundaries. Keeps full 10k test optional for runtime predictability.
- backend/verify_local.ps1 adds optional `-Benchmark` switch to run Python unittest + synthetic smoke + optional Node JS check + 10k benchmark. Without flag, normal full suite remains fast.
- NEW backend/BENCHMARK.md documents exact commands, measurements and omissions. No actual timings were collected in this tool session; the code is committed but Python runtime QA is still pending.
- Current GitHub 9 test files declare **134 distinct `test_*` methods**: benchmark3, eligibility27, importer21, profile_workflow12, report21, report_existing10, smoke_local1, store29, viewer10. Verified by reading actual source, **134 NOT EXECUTED / NOT 134 PASS**. Previously exact remote ui.js V8 JavaScript syntax parse PASS; no browser validation.

## NEXT P2-10 priority
1. Obtain permitted authentic checkout of this private repo and run from backend:
   `python -m pip install -r requirements.txt` (if dependency not already present)
   `python -m unittest discover -s tests -v`
   `python smoke_local.py`
   `node --check ui/ui.js`
   `python benchmark_local.py --records 10000 --assessed 200`
   On local Windows with prerequisites installed: `powershell -ExecutionPolicy Bypass -File .\verify_local.ps1 -Benchmark`.
   Record TRUE passing/failing/skipped case counts and *measured* timings. Fix genuine failures before advertising BASIC stability/10k performance. No CI runs exist on feature branch. Avoid initiating paid GitHub Actions or writing to protected main.
2. Verify real Windows browser and Excel/PDF native rendering, long Korean identifiers and one-click historical XLSX, profile JSON Blob download, 7 themes, keyboard/mobile, interrupted profile revision/backup recovery. Check 10k query timing; if slow, profile with SQLite EXPLAIN and optimize only after actual benchmark evidence.
3. Finish BASIC usability: CSV import and profile apply and PDF replay still require separate CLI. Any HTTP write path requires threat model, CSRF/Host/Origin/auth and backups plus explicit user permission. Later P3 PRO government API customer key; P4 opt-in AI; P5 Windows packaging/security; P6 KIPRIS legal name clearance/sales approval.

## Known blocker and legal/privacy boundaries
GitHub connector source reads/writes work. Current container had no authenticated private checkout; earlier private git/raw/API DNS/auth and Chromium localhost ERR_BLOCKED_BY_ADMINISTRATOR prevented actual Python/browser tests. Do not re-run obsolete /mnt/data/bidowl_p2 and misrepresent results. No customer SQLite/docs/CSV/Excel/PDF, credentials/API keys/.env/font binaries committed. Local and disposable synthetic tests only. Planned prices 59k BASIC, 149k PRO, 299k PREMIUM are unverified. Historic school demo 340/340 is not new BID OWL QA.
