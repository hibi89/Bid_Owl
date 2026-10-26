# BID OWL STATUS — P2-09 · 2026-10-27 KST

## Code/product branch, identity and untouched production
Private GitHub hibi89/Bid_Owl (repo ID 1399359397). Work only feature/bid-owl-v1-basic-mvp; previous feature HEAD 4981740128b582ca71ed2820ce6653b23ada4900. Protected main baseline c888c795bef72734f3f7016e54013b82453f11d8, school-demo legacy restore 2807a93a3e0deba98840712401fdd6025e6f5610. This task does NOT write to main, old Vercel project project08-bid-insight/prj_YcrN7OdOjKl6M457HelGIItLeeXZ, GitHub permissions or production deployment. Final SHAs/author to confirm after HANDOFF commit.

## Source status
P1 conservative CSV/rule eligibility/SQLite version history/CLI XLSX+PDF. P2-01 readonly local UI and 7 themes, P2-02 global favorites, P2-03 explicit backed-up profile mutation/reassessment through local CLI, P2-04 version CAS+readonly preview/SQL detail/keyboard drawer, P2-05 historical saved report replay/synthetic smoke, P2-06 output-failure cleanup and new-profile JSON form, P2-07 one-click localhost XLSX attachment, P2-08 Unicode 300-char ID bounded query and reassessment profile version pinning.

P2-09:
1) New backend/benchmark_local.py creates up to 10,000 synthetic local Bid objects, inserts all in one SQLite transaction in TemporaryDirectory, assesses 200 synthetic bids by default, reads using actual viewer mode=ro, measures perf_counter ms for import, subset assessment, list page, category/search, detail and global favorite. Checks results and readonly attempted DELETE, then discards disposable DB. Reports JSON and DB file size, no customer data, external API, browser or PDF. Does not measure actual CSV parsing, DOM rendering or Windows/native Excel.
2) New backend/tests/test_benchmark_local.py 3 small unittest methods (31 rows + 1-row edge + illegal parameters). The default 10k benchmark is excluded from ordinary full test discovery.
3) backend/verify_local.ps1 optional -Benchmark switch; default still executes full unit suite and synthetic end-to-end, then optional Node syntax. -Benchmark appends 10k run and fails on nonzero process exit.
4) New backend/BENCHMARK.md measurement methodology, environment metadata, commands and explicit limitations; NEXT_TASK.md/STATUS.md/HANDOFF.md updated.
5) No new business feature/real API added; this is a measured-performance gate preparation task.

## Verification strictly separated
Authenticated GitHub source readback found 9 Python test files with **134 distinct test method declarations** (benchmark3, eligibility27, importer21, profile workflow12, report21, report existing10, smoke1, store29, viewer10); this count is NOT run and NOT 134 PASS. Source structure inspection confirmed benchmark opens only disposable DB and actual read-only viewer connection, bounded data counts, optional PowerShell flag. V8 JS parse on unchanged exact remote ui.js was PASS in previous P2-08. **Current Python entire 134 test suite, synthetic benchmark 10k and smoke_local.py NOT EXECUTED IN THIS ENVIRONMENT.** Actual 10k timings and Windows user experience unknown. Historical P1 on Linux 96 PASS (2026-10-26, different source baseline), no evidence it validates P2.
Main container lacks a private authenticated full repo checkout (previous DNS/auth clone/raw/API failures). Older /mnt/data/bidowl_p2 was a partial stand-in. Earlier Chromium loopback ERR_BLOCKED_BY_ADMINISTRATOR. GitHub Actions feature branch had zero runs when checked P2-08. No user Windows Excel/PDF/native Chrome/Edge, UI 7 themes, report font/license, 10k latency, profile recovery or KIPRIS reviewed.
No customers' SQLite/PDF/XLSX/CSV, credentials, .env, API keys, font files, official procurement data uploaded to GitHub. No external API, paid service or public marketing.

## Next P2-10
On an actual authenticated private checkout from backend:
`python -m unittest discover -s tests -v`
`python smoke_local.py`
`python benchmark_local.py --records 10000 --assessed 200`
`node --check ui/ui.js`
or Windows `powershell -ExecutionPolicy Bypass -File .\verify_local.ps1 -Benchmark` with Python/ReportLab/font set up. Record actual pass/fail/skip and timings; fix failures and profile hotspots first. Test actual Excel/browser, mobile/7 themes, first-use profile download and 10k performance, real printable PDF with installed Korean TTF. BASIC still needs CLI for import, profile mutation and PDF, and is NOT ready for paid launch. PRO official user-key API, PREMIUM optional AI, Windows packager/security, brand/trademark clearance and public sale follow later. Product planned price points BASIC 59,000, PRO 149,000, PREMIUM 299,000 KRW are estimates, not tested sales.
