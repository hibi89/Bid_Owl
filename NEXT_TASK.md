# BID OWL — NEXT_TASK (2026-10-26 KST)

Repo: hibi89/Bid_Owl private, active branch feature/bid-owl-v1-basic-mvp. main/static legacy and Vercel production must stay untouched without explicit approval.

## Completed
- [x] P1-00 repository/branch recovery and original main protection (main c888c795bef72734f3f7016e54013b82453f11d8).
- [x] P1-01 strict offline CSV contract and parser, code commit 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b, previous 21 tests PASS.
- [x] P1-02 profile and source-gated 3-state evaluator, code commit fa2ed6aea6c634490d1f467bc1a3c3788df6adb1, previous 27 tests PASS.
- [x] P1-03 SQLite persistence at module scope, code commit e1f3befafe1590570a99879812f678a5a60b99a1, 28 local tests PASS in this turn, new files' Git blobs match local bytes. See STATUS/HANDOFF for exact test boundary.
- [ ] **Full exact GitHub P1-01+P1-02+P1-03 combined 76-test run is pending.** Prior local environment recreated upstream contracts and did not contain previous two test suites.

## NEXT P1-04 — reports + CLI
1. Confirm HEAD and obtain actual GitHub source checkout if possible; execute all existing test suites together (report exact pass/fail) without assumptions. If not possible, clearly report unverified.
2. Build backend/cli.py: validate CSV and safe profile JSON input, choose explicitly local SQLite path, import -> assess -> output selected bids with evidence and checked_at. Fail closed, no secrets, flag synthetic fixtures.
3. Report module: export true, independently inspectable Excel (.xlsx) and Korean PDF; choose permissive dependency/library/fonts after licensing and rendering checks. Explicit customer-data privacy and no external API.
4. Report fields: profile ID, source/actual data timestamp, current deadline, original source snippets and locations, rules PASS/FAIL/UNKNOWN, expired status, human-review warning. No actual legal qualification guarantee.
5. Unit/integration tests: bad file no writes, PDF file opens and Korean glyphs render, xlsx strings/cells readable, no prompt injection from CSV content, escape potentially dangerous Excel formula prefixes. For unavailable fonts/licensing, label report portion incomplete rather than faking PASS.
6. Commit only to feature, source SHA verify, update STATUS.md/HANDOFF.md. Keep main untouched.

## Later
P2 BASIC search+UI+7 themes, P3 PRO official procurement APIs/amendment identifiers/quotas and alerts, P4 PREMIUM opt-in customer AI, P5 Windows install/security, P6 brand check + Kmong. No production/cost/external transmission without approval.
