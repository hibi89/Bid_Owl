# BID OWL NEXT_TASK — P2-07 (2026-10-27 KST)

Private hibi89/Bid_Owl. Work ONLY on feature/bid-owl-v1-basic-mvp; main and legacy Vercel must remain unchanged. On ㄱ fetch HEAD, read HANDOFF/STATUS/AGENTS/REQUIREMENTS/NEXT_TASK and continue safely.

## Source implemented
P1 CSV/SQLite immutable version+rules+Excel/PDF; P2-01 readonly local browser, 7 themes; P2-02 global localStorage favorites + readonly JSON API; P2-03 profile JSON editor and CLI backup/apply/reassess; P2-04 atomic SQLite profile version compare-and-set and keyboard/detail fixes; P2-05 historical XLSX/PDF replay CLI; P2-06 incomplete XLSX/dual-output failure cleanup, new profile form and local Windows validation script.

P2-07:
- backend/viewer.py adds `GET /api/report?assessment_id=N` binary XLSX response, accepting only one positive bounded stored assessment ID and exact path; the existing Host/Origin and same-origin Fetch-Metadata checks apply. SQLite mode=ro + PRAGMA query_only remains mandatory. Immutable historical assessment, original bid version and rule evidence are rendered by existing report engine. One self-cleaning TemporaryDirectory used for generated XLSX; no permanent user report file created by HTTP and no database mutation. 16 MiB download cap, Cache-Control no-store/nosniff, fixed attachment filename. JSON 400 for invalid ID, 404 missing assessment and 403 forbidden Host/cross-site.
- backend/ui/ui.js + ui.css: a real one-click **Excel (.xlsx) 직접 다운로드** link in selected evidence drawer when a saved assessment is available. Stale historical status warned. PDF still supported only via local CLI because font dependency and browser delivery not verified. User profile changes still require backup-first CLI.
- backend/tests/test_report_existing.py adds two methods exercising real synthesized ZIP bytes and HTTP attachment/safe requests against synthetic real SQLite. backend/smoke_local.py now exercises binary read-only report GET alongside existing synthetic full flow.
- backend/REPORT_REPLAY.md documents exact endpoint and limitations.
- GitHub remote test inventory: **128 declared methods** (eligibility27, importer21, profile workflow11, report21, saved-report10, synthetic smoke1, store28, viewer9). These definitions were counted but **128 NEVER RUN as a full actual checkout**; do NOT say 128 PASS. Exact remote ui.js V8 syntax parse PASS, not browser UI validation.

## NEXT P2-08 must do first
1) Run full actual Python source suite in authorized private repo checkout: `cd backend && python -m unittest discover -s tests -v`; also `python smoke_local.py`, `node --check ui/ui.js`. Windows shortcut `powershell -ExecutionPolicy Bypass -File .\verify_local.ps1`. Record actual pass/fail counts and fix all failures. GitHub files are connector-visible but no private full checkout available to this container (previous git/raw/API DNS failure); old /mnt/data/Bid_Owl_work is empty and bidowl_p2 is a partial stand-in. Do not claim full execution there.
2) Real Windows browser: test clicking XLSX attachment from detail, verify data/headers and saved original rule evidence, profile first-use Blob download, keyboard focus, seven themes and mobile widths. Test Excel opening real XLSX, ReportLab PDF with local permitted Korean TTF, and 10,000-record perf. Verify request ID/Host/origin/cross-site errors and temporary files cleanup.
3) BASIC still not fully one-click: CSV import and profile apply CLI and PDF re-export CLI. Any writable HTTP API needs proper CSRF/auth backup design and user approval; do not silently add. Can continue with read-only browser improvements. P3 user-key official API, P4 AI opt-in, P5 Windows packager/security, P6 KIPRIS trademark/sales gate later.

## Security and production
Historical report contents include potentially sensitive customer evidence; stream only on loopback, no-store, no arbitrary path. No external upload/network paid tools, customer DB/API keys/docs/fonts into GitHub. Never deploy to public Vercel or modify main without consent. Existing static school demo metrics 340/340 irrelevant. Revenue/product prices 59k/149k/299k KRW tentative and trademark not cleared.
