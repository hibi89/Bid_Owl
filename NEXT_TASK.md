# BID OWL NEXT_TASK — 2026-10-27 KST

## Current branch / resume
Repo: hibi89/Bid_Owl (private). Work branch: feature/bid-owl-v1-basic-mvp. Keep main and old Vercel untouched. Resume command [Bid_Owl 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. Before any further changes read HANDOFF -> STATUS -> AGENTS -> REQUIREMENTS -> this file -> actual source and latest HEAD.

## Completed / observed
- P1-01 CSV strict importer (21), P1-02 conservative 3-state eligibility (27), P1-03 SQLite revisions/audit (28), P1-04 CLI + XLSX/PDF (20). Combined P1 96 passed on Linux at 2026-10-26; not a commercial Windows verification.
- P2-01 added backend/viewer.py (127.0.0.1 only; SQLite mode=ro, query_only; GET-only APIs), backend/ui/index.html/ui.css/ui.js, backend/tests/test_viewer.py. Search/title/agency/number, category/status/deadline/profile filters, paging, detail evidence, stale assessment downgrade to UNKNOWN, 7 CSS themes, browser-local favorites, mobile CSS. UI uses textContent, not unsafe bid HTML injection.
- P2 tests: 5/5 locally with synthetic schema-compatible SQLite fixture; Node syntax of locally tested JS passed. HTTP API, Host/Origin checks and static file response tested. **Exact GitHub checkout combined tests/real browser NOT VERIFIED.** Chromium blocked localhost and alternate test host twice with ERR_BLOCKED_BY_ADMINISTRATOR in this environment. Never claim an application failure from this alone.
- P2-01 code baseline on this branch before docs: 2ff7a22082b2e37362d0935dee32fa292566eecb. GitHub current HEAD must be read again after subsequent doc commits.

## NEXT P2-02: polish and close BASIC UI gaps
1. Confirm latest branch SHA and read actual remote files, compare against tested local source. Run full python -m unittest discover -s tests -v on full checkout, and Node --check ui/ui.js.
2. Replace current-page-only favorites checkbox with correctly **global, paginated favorites** (prefer persistent local SQLite store with an explicit safe write-path design/backup, or a client-side aggregated read-only approach; compare before implementation). Do not pretend it already works across all pages.
3. Add local profile editing/import UX (currently CLI JSON), sensible open/expired flags, missing-data UX and re-assessment workflow preserving saved historical reports. Do not enable arbitrary write API without reviewing threat model.
4. Real browser desktop/mobile visual regression, keyboard accessibility, 7-theme focus contrast and responsive detail panel; Windows 11 real machine smoke when available.
5. Run 101 expected legacy+P2 regression tests (expected count, not measured). Inspect Vercel/project status only as needed; P2 local Python is NOT DEPLOYED.
6. Complete STATUS/HANDOFF with actual SHA, verification and next task. Keep customer private data, DB files, PDFs, keys, fonts out of GitHub.

## Later stages
P3 official government procurement API and revisions with approved key; P4 optional AI with explicit consent and cost; P5 Windows packaging/security/real user files; P6 trademark KIPRIS/marketing/Kmong launch gate. No public sale, paid service, external upload, main change, Vercel production change without approval.

## Current blockers / honest limitations
Customer Windows/browser and native Excel not tested. Official API and licensing/legal procurement rules not checked; brand BID OWL legal availability unresolved. Favorites currently per browser/per visible results page, not global. Browser navigation blocked by this environment, not proof of UI malfunction. Legacy 340/340 and demo 2025 bid results remain unrelated to real new product.