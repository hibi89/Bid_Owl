# BID OWL NEXT_TASK — 2026-10-27 KST (P2-04)

Repo: private hibi89/Bid_Owl, feature/bid-owl-v1-basic-mvp. Main/legacy Vercel untouched. On user ㄱ, read HANDOFF, STATUS, AGENTS, REQUIREMENTS, NEXT_TASK and latest source/branch SHA. Resume implementation automatically; don't assume past unverified test results are current.

## Implemented source / verification
P1: CSV validation, evidence-based PASS/FAIL/UNKNOWN, immutable bid/profile/assessment revision SQLite with consistent backups, CLI real PDF/XLSX. 96 tests last executed successfully 2026-10-26 on Linux, not rerun after P2.
P2-01: readonly 127.0.0.1 viewer, search/filters/detail/provenance and seven themes.
P2-02: browser-local favorites can filter globally before pagination through bounded read-only same-origin POST.
P2-03: company profile edit JSON builder in browser + local preview/--apply/mandatory non-overwriting backup and optional re-evaluation CLI. No browser mutation API.
P2-04:
1) bidowl/store.py: optional expected_version enforced inside BEGIN IMMEDIATE transaction of save_profile(), preventing time-of-check version overwrite; backward compatible default None.
2) profile_workflow.py: ReadOnlyProfileStore uses SQLite mode=ro/query_only for preview; refuses blank/unversioned/incorrect schema without initialization; apply preflights read-only before writer, uses atomic version guard; distinguishes prewrite profile conflict with retained backup.
3) viewer.py: exact source_id+bid_no SQL predicate for single detail, no O(all bids) Python scan.
4) ui/ui.js: labelled dialog, focus containment, stale async response invalidation when drawer closed/another detail is opened, and clearer assessment status messaging.
5) tests/test_profile_workflow.py +3 regression methods (preview readonly, invalid DB no initialization, race); tests/test_viewer.py +1 (single-key detail) and backend/README.md updated.

GitHub source inventory verified: 116 declared test methods: test_eligibility 27, test_importer 21, test_profile_workflow 11, test_report 20, test_store 28, test_viewer 9. This is a count of *declared tests*, **NOT PASS verification**. Actual current ui.js content parses under V8 Function constructor PASS. P2-04 Python source + 4 tests committed through GitHub, **full Python 116 have not been executed**. Previous private repo clone and signed raw URL cannot resolve via DNS/auth in this execution environment, do not retry identical method. Browser Chromium localhost attempts in prior session blocked by ERR_BLOCKED_BY_ADMINISTRATOR (not necessarily application defect).

## NEXT P2-05
- Prefer an authorized full repository checkout in an environment that can execute private code. Run `cd backend && python -m unittest discover -s tests -v`; report actual 116 pass/fail/skips and fix any failing assertion. Specifically check atomic profile race mock, mode=ro preflight, SQLite detail predicate and same-origin POST.
- Run `node --check ui/ui.js`, validate real HTTP GET bids/detail/profile and favorites-only POST; run synthetic CSV -> versioned SQLite -> report PDF/XLSX -> profile preview -> mandatory backup -> explicit apply --reassess; confirm existing assessment remains accessible and updated profile revision reflected as required.
- Validate actual browser (Edge/Chrome Windows 11) Blob JSON export with CSP, dialog keyboard focus, seven themes and responsive layout. Benchmark 10k-bid list+detail; optimize only on measured profile.
- Improve customer-friendly report actions and missing profile onboarding; current profile updates require CLI, not yet ready as smooth paid-product UI. Future UI mutation route requires CSRF/authentication, backup and user approval.
- Continue P3 official procurement API (user key) / P4 optional AI / P5 Windows packaging and security / P6 KIPRIS and public sales clearance after BASIC integration.

Safety: no customer records or keys/files/fonts in GitHub; no external API calls/paid products; no main/Vercel/deployment/domain changes. Historic school demo metrics 340/340 unrelated.
