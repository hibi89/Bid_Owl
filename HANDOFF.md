# BID OWL HANDOFF — P2-09 · 2026-10-27 KST

## 1. Purpose, technical system, stable requirements
BID OWL is a Windows-local SME public procurement screening tool, not legal certification, bidding guarantee or automatic tender submission. BASIC planned one-time KRW 59,000: validated CSV bids, company profile, conservative PASS/FAIL/UNKNOWN and cited original rule evidence, SQLite version history, search/favorites/seven themes, Excel/PDF historical reports. PRO planned KRW 149,000 official Korean procurement API with user-issued key, on-PC-only sync; PREMIUM KRW 299,000 optional user-supplied AI key and profitability. Prices, final legal brand and market demand not verified. Tech: Python 3.11+, SQLite schema v1, stdlib XLSX, ReportLab + locally permitted Korean TTF for PDF; frontend localhost 127.0.0.1 HTML/CSS/JS. No mandatory cloud service or customer data transmission.

## 2. This iteration's implementation, code/files, choices
Earlier stages: P1 strict CSV/evidence rules/versioned storage/PDF+XLSX CLI; P2-01 local read-only UI; P2-02 global favorites; P2-03 profile edit JSON download and explicit backed-up CLI apply; P2-04 CAS/read-only preview/detail SQL/accessibility; P2-05 historical saved-assessment replay plus synthetic end-to-end smoke; P2-06 incomplete output cleanup/new profile onboarding and Windows QA helper; P2-07 one-click read-only XLSX attachment; P2-08 300-char Korean ID support and profile-reassessment race protection.
P2-09 NEW:
- backend/benchmark_local.py: isolated tempfile synthetic Bid dataset 1–10000, DEFAULT 10000; constructs Bid objects (not parsing CSV), imports in a single SQLite transaction with BidOwlStore, saves a fake company and assesses first 200 records by default. Opens viewer.open_database (SQLite URI mode=ro, PRAGMA query_only=ON), benchmarks in perf_counter milliseconds all bids first page, category+q filter, detail by exact key and global favorite; checks counts, rejected DELETE, SQLite size and generates JSON. Deleted temp dir after normal return; DOES NOT touch customer DB, upload data, use API keys or internet.
- backend/tests/test_benchmark_local.py: 3 SMALL unittest methods: 31-record real SQLite flow, 1-record unassessed flow, invalid counts including bool. Full 10k intentionally NOT part of default unittest discovery.
- backend/verify_local.ps1: optional `-Benchmark` flag, after full tests/synthetic smoke/optional Node syntax, runs `python benchmark_local.py --records 10000 --assessed 200`; default no flag remains normal verification. Any nonzero exits mark failure.
- backend/BENCHMARK.md: execution methods, interpretation of each timing and warning that no timings exist until actual run.
- NEXT_TASK.md, STATUS.md, HANDOFF.md updated.
Choice: measure the existing 10k query path before speculative SQL/pagination optimizations. Python objects created before timing; no CSV parse, browser DOM or PDF/Excel timing. The benchmark is a helper, not performance certification.

## 3. Measured verification, unverified, exact commands
Authenticated GitHub source fetched and test method regex counted 9 files with **134 unique declarations** = benchmark3 + eligibility27 + importer21 + profile workflow12 + report21 + saved report10 + synthetic smoke1 + store29 + viewer10. These are source definitions, **134 NOT EXECUTED/134 NOT PASS**. GitHub latest benchmark and Windows helper source read-back confirmed use of TemporaryDirectory, mode=ro/query_only connection, bounds and `-Benchmark` flag. Exact remote ui.js V8 syntax parse PASS in prior iteration (unchanged this turn). HISTORIC P1 96 PASS Linux CPython on Oct 26 earlier P1 source ONLY. No real current suite or 10k benchmark, no measured milliseconds, no live Windows/Chrome/Excel/PDF tests executed.
From permitted full private checkout backend dir:
    python -m pip install -r requirements.txt
    python -m unittest discover -s tests -v
    python smoke_local.py
    node --check ui/ui.js
    python benchmark_local.py --records 10000 --assessed 200
Windows optional combined helper:
    powershell -ExecutionPolicy Bypass -File .\verify_local.ps1 -Benchmark

## 4. Stage/percent, stop point and next
P1 source complete; P2-01 through P2-09 code present with only static/source testing of new features; full Python QA and Windows customer readiness remain blockers. Earlier high-level estimate roughly 35% of BASIC+PRO+PREMIUM+installer/sales complete, not recalculated or objectively measured this iteration. BASIC is NOT shippable yet: user still runs CLI for import/company DB changes/PDF; browser Excel download and local viewer have not been native-Windows tested. Stop after P2-09 files/docs committed and final main/feature SHA+hibi89 identity checked. P2-10 must execute genuine entire 134-test suite, smoke, 10k benchmark and fix failures FIRST. Then Windows manual proof, full user experience, API/AI/installer/brand gate later.

## 5. Failures, blockers, prior attempts, avoid-repeat
Private repo clone from model's Python container failed DNS/auth. Signed raw.githubusercontent.com and api.github.com downloads also DNS unavailable from that container; GitHub connector reads/writes remote source but does not directly mount authenticated checkout into sandbox. Old /mnt/data/bidowl_p2 incomplete mocked stand-in and /mnt/data/Bid_Owl_work/backend empty: never run stand-in and label the result actual GitHub full suite. Chromium localhost previously ERR_BLOCKED_BY_ADMINISTRATOR from platform restriction (not proven app bug). Read-only GitHub Actions query found zero workflow runs on branch in P2-08; avoid creating potentially paid GitHub CI runner without user approval. New benchmarking is only source, not a measured performance result. Python tests and Windows script committed but have not run on target PC. Profile reassessment can commit partially if interrupted, backup retained; output multi-format file cleanup is best effort rather than fully crash-atomic.

## 6. Repository, protected branches, SHA/commits/files
Private https://github.com/hibi89/Bid_Owl repo ID 1399359397. Feature branch `feature/bid-owl-v1-basic-mvp`. P2-09 starting feature SHA `4981740128b582ca71ed2820ce6653b23ada4900`. New source commits:
- `e40ad3f742ceea97b9009e652cdef74798ef74a5`: backend/benchmark_local.py,
- `70d4a5dba2a9a92a0d19de4358ab9fc39eda5235`: correct timing label at any record count,
- `156d518940ec972f26a073897c5e50e42b44cb93`: backend/tests/test_benchmark_local.py (+3 methods),
- `ba19fc20ef0e5b1f0abeea843001e6814a02c5c8`: backend/verify_local.ps1 optional -Benchmark,
- `6550da84874f47f6a41cfb29019f93b1c8e7b82f`: backend/BENCHMARK.md.
Docs commits follow, pre-HANDOFF STATUS `ee52bc94be71fe8f05dffa665db92394cd2b0c90`. Final feature HEAD must be fetched after HANDOFF write. Main baseline `c888c795bef72734f3f7016e54013b82453f11d8` (untouched). Original school demo rollback `2807a93a3e0deba98840712401fdd6025e6f5610`. Only changed paths this stage: backend/benchmark_local.py, backend/tests/test_benchmark_local.py, backend/verify_local.ps1, backend/BENCHMARK.md, NEXT_TASK.md, STATUS.md, HANDOFF.md. No main/public code.

## 7. Production, local command, URLs/environment
New Python localhost product not deployed (public production URL N/A). After user explicitly runs `python viewer.py --db ./demo.sqlite3 --port 8765` from backend, browser local URL http://127.0.0.1:8765; HTTP GET /api/report?assessment_id=N returns historical XLSX from readonly SQLite, PDF still explicit CLI with ReportLab/font. Existing legacy 2025 school demo Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched; deployed URL/SHA/live HTTP unverified. Benchmark only runs with command on an authenticated working checkout and deletes its generated temp DB. Windows 11/Excel/Edge/Chrome not tested in this turn.

## 8. Originals, backups, secrets and access permissions
Main school static demo historical 340/340 QA and old countdown unrelated to BID OWL product quality. All work GitHub feature branch, no forced push, original main untouched, no Vercel changes or deployment. No customer CSV/DB/PDF/XLSX, fonts, .env, API credentials/keys or business secrets uploaded to GitHub. Company local apply requires explicit --apply + new backup and expected version CAS; assessments preserve source evidence, report exports cannot silently overwrite existing files. Connected writing author/committer hibi89; verify actual final identity. Brand KIPRIS legal availability and customer sales approval pending. No paid tool/external network call to real procurement service.

## 9. NEXT P2-10 ordered acceptance and approvals
1) On authorized **exact current private checkout**, execute all 134 Python tests and synthetic smoke via `python -m unittest discover -s tests -v` and `python smoke_local.py` and `node --check ui/ui.js`. Get real counts/errors and fix actual failing cases before claiming release readiness.
2) Run `python benchmark_local.py --records 10000 --assessed 200` on Windows, record *actual* import/filter/list/detail/favorite elapsed ms, DB size, Python version and CPU/RAM/SSD environment. Repeat, profile slow queries then optimize. Never invent benchmark performance.
3) Windows Chrome/Edge: open synthetic local viewer, verify XLSX attachment in real Excel, profile JSON Blob downloads + explicit backup apply, PDF rendering with Korean local TTF, 7 themes, mobile/keyboard, Unicode ID and cross-site boundaries, incomplete backup recovery. No user/customer data as test fixtures.
4) After BASIC acceptance, P3 official procurement customer API key, P4 optional AI/sensitivity, P5 Windows installation/security, P6 KIPRIS/trademark/pricing/sales. Explicit approval for paid tools, external user-data transfer, prod deployment/main modification/public marketing.

## 10. Last update/date/next-turn instruction
2026-10-27 KST. GitHub connector created source/docs and verified 134 test definitions and fixture-only temp DB. No genuine CPython 134-case run, benchmark 10k execution or Windows browser/Excel/PDF results; these remain open. User sends ㄱ to resume P2-10. After this HANDOFF commit, verify feature and main HEAD, committer identity, changed files and numbers.
