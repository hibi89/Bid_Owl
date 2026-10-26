# BID OWL NEXT_TASK — P2-10 · 2026-10-27 KST

## Resume rule
Private hibi89/Bid_Owl. User ㄱ = automatically continue after fetching current main + feature branch heads and reading HANDOFF, STATUS, NEXT_TASK, AGENTS, REQUIREMENTS plus source. Work only `feature/bid-owl-v1-basic-mvp`. No deployment, main rewrite, external customer-data transfer, paid automation, API key sharing or public sale without user authorization.

## Source through P2-09
P1 strict CSV/rule PASS/FAIL/UNKNOWN versioned SQLite with evidence and PDF/XLSX. P2-01 readonly loopback viewer/7 themes; P2-02 global favorites; P2-03 mandatory-backup profile CLI and JSON download; P2-04 CAS and readonly preview/detail; P2-05 saved assessment report replay + synthetic smoke; P2-06 partial-file export cleanup and new-company form; P2-07 read-only one-click XLSX; P2-08 long Korean ID and pinned profile-version reassessment; P2-09 synthetic up-to-10k bid performance benchmark source.

## P2-10 commits/source
- NEW `backend/qa_runner.py` cross-platform actual Python test suite runner. Calls unittest.TestLoader.discover + TextTestRunner on all `test_*.py` under tests, collects **real** tests_run/failures/errors/skips/expected failures/unexpected successes/failed IDs and elapsed_ms, then executes synthetic `smoke_local.run_smoke` only if unittests succeeded. Validates optional Node.js `node --check ui/ui.js`; 10k synthetic benchmark only when `--benchmark` explicitly requested and unit/smoke succeeded. Report returns FAIL for any failing executed stage, and distinguishes SKIP. Git HEAD if available, Python/OS/machine, timestamp recorded; customer data never read. Writes an exclusive new JSON file `backend/qa_results/bidowl_qa_...json` that is not uploaded.
- NEW `backend/tests/test_qa_runner.py` three deterministic mocked tests of machine-readable PASS result shape, failure preventing smoke/benchmark, and JavaScript failure propagating to overall FAIL. Mock result count is fixture, not genuine executed test count.
- `backend/verify_local.ps1` simplified to call new Python runner `python qa_runner.py` or `python qa_runner.py --benchmark` once, with same opt-in `-Benchmark`, reporting real JSON path. No new external CI services or paid runners.
- `backend/.gitignore` excludes `qa_results/`. `backend/BENCHMARK.md` documents local invocation and measured-vs-unverified distinction. STATUS/HANDOFF/NEXT_TASK updated.
- GitHub remote **10 Python test modules / 137 declared `def test_*` functions**, counted by fetching each current test file: benchmark3, eligibility27, importer21, profile workflow12, QA reporter3, reports21, replay10, smoke1, storage29, viewer10. **137 NOT EXECUTED, NOT 137 PASS** in current authoring environment. Last actual historical Linux P1: 96 PASS (2026-10-26 on earlier source); current branch Python integration remains unknown. Earlier exact remote JavaScript V8 syntax parse PASS, but not browser E2E.

## NEXT P2-11: actual execution, highest release blocker
1. Run on an authentic authorized private repository checkout with Python 3.11+, ReportLab and local Korean licensed TTF:
    cd backend
    python qa_runner.py --benchmark
   or Windows:
    powershell -ExecutionPolicy Bypass -File .\verify_local.ps1 -Benchmark
   This runs and records the **real** all-Python-unit suite, synthetic end-to-end, JavaScript check if Node installed and 10k dataset timing, local JSON under backend/qa_results/. Compare actual Git SHA in JSON to branch HEAD before stating PASS. If the run reports FAIL or SKIP, fix source/test or environment and rerun. Do not invent timings.
2. Validate real Windows 11 Chrome/Edge UI 7 themes, first-use company JSON download and explicit backed-up apply, historical XLSX download opens natively in Excel, Korean PDF with local font, keyboard focus, 300-char Korean IDs and actual 10k search responsiveness. The QA runner *does not* claim these browser/native results.
3. BASIC still CLI-assisted for CSV import, profile DB writes and PDF. Secure one-click UX needs CSRF/auth/backups, not an unreviewed writable HTTP endpoint. Later P3 PRO official government API user key, P4 optional PREMIUM AI, P5 packager/security, P6 trademark/KIPRIS/sales gating.

## Blocking history and privacy
Exact current private repo cannot be checked out in this author's local container (prior private git/raw/API DNS+auth failures); no direct Python 137-run measurement here. Previous sandbox Chromium localhost blocked with ERR_BLOCKED_BY_ADMINISTRATOR. Never run old partial stand-in as if full current checkout. GitHub action runs absent at last check; avoid consuming potentially paid GitHub compute without approval. No customer CSV/SQLite/docs/reports/fonts/credentials/API keys/.env committed or uploaded. Main/Vercel original school demo preserved. Total all-tier project completion estimate previous ~35%, not an objectively measured percentage or changed in P2-10.
