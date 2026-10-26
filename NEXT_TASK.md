# BID OWL NEXT_TASK — P2-05 (2026-10-27 KST)

Private repo hibi89/Bid_Owl. Only feature/bid-owl-v1-basic-mvp. New chat: read HANDOFF -> STATUS -> AGENTS -> REQUIREMENTS -> NEXT_TASK -> current code, and check main/feature HEAD. "ㄱ" resumes automatically.

## Prior implementation
P1: importer, evidence-based PASS/FAIL/UNKNOWN, versioned SQLite, PDF/XLSX. P1 was measured at 96 PASS/0 FAIL on Linux 2026-10-26.
P2-01 read-only SQLite 127.0.0.1 viewer, search/evidence/seven themes. P2-02 global browser-local favorites via same-origin bounded read-only JSON POST. P2-03 JSON profile editor + dry-run/backup-required explicit local edit/reassess CLI. P2-04 store expected_version inside transaction, preview read-only SQLite, keyed detail SQL, async drawer and accessibility hardening.

## P2-05 source committed (NOT integration-verified)
- backend/report_existing.py: open existing SQLite with viewer.open_database(mode=ro/query_only), load a persisted immutable assessment with historical bid version/rule evidence, write local non-overwriting XLSX/PDF with existing renderer, **without reimporting or re-evaluating**. Validates assessment ID and output collisions. No network/DB write endpoint.
- backend/ui/ui.js: evidence drawer shows selected saved assessment ID and the correct report_existing.py local command, with explicit warning if this is a stale PASS/FAIL.
- backend/tests/test_report_existing.py: six synthetic report replay, history preservation, overwrite refusal, missing ID, readonly, CLI tests.
- backend/smoke_local.py: disposable synthetic fixture end-to-end runner: CSV -> SQLite -> XLSX -> loopback API GET and read-only favorites POST -> stored report replay -> profile preview + backup + apply + re-assess -> historical snapshot and backup verification. It does not use user DB, official API, external services, or PDF.
- backend/tests/test_smoke_local.py: one synthetic integration test.
- backend/REPORT_REPLAY.md documents exact local commands and limitations.
- GitHub currently has **123 declared test methods**: import21, eligibility27, store28, report20, viewer9, profile_workflow11, report_existing6, smoke_local1. Count observed using fetched source; NOT actual pass result. Current exact remote ui.js parses in V8 Function (PASS).

## NEXT P2-06 priorities
1. Run a fully authenticated/authorized actual checkout on a runner able to access this private repo. Execute `cd backend && python -m unittest discover -s tests -v` and `python smoke_local.py`; report real test count/errors (123 is only an inventory). Fix failures immediately and rerun.
2. Test `python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./new-reports --format both` on a **synthetic** DB; inspect real XLSX and PDF (ReportLab + local Korean TTF). Verify original DB not mutated and new files never overwrite.
3. Windows 11 local Chrome/Edge: inspect UI detail/history and profile JSON download, CSP, keyboard focus, seven themes responsive, Excel/PDF. Benchmark 10k bids and assess status/batch crash recovery.
4. Customer-friendly report export and profile editing remain CLI-assisted by design, not full one-click paid UX. No writable HTTP endpoint without explicit CSRF/authentication/backup review and user approval.
5. Future: P3 official procurement API with customer key, P4 opt-in AI, P5 Windows install/security, P6 trademark/sale gate. No main/Vercel/production/paid-service changes and no customer DB/docs/keys/fonts in GitHub.

## Blocker / earlier attempts
Container DNS couldn't resolve GitHub private repo clone, signed raw URL or api.github.com, and no private checkout exists at /mnt/data. Do not run partial old stand-in and call it full current QA. Chromium blocked local navigation in previous session with ERR_BLOCKED_BY_ADMINISTRATOR. No proof of browser bug or successful rendering. Work remains source-implemented/integration-pending until genuine execution on full checkout.
