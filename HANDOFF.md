# BID OWL HANDOFF — P2-08 · 2026-10-27 KST

## 1. Goal / technology / confirmed product requirements
Private BID OWL / 비드아울: Windows 11 local-first public-bid screening for SMEs, not legal qualification/automatic tender/award guarantee. BASIC planned KRW 59,000 once: validated CSV, profile, source-evidenced rule PASS/FAIL/UNKNOWN, search/favorites, seven UI themes, XLSX/PDF. PRO planned 149k KRW official procurement API (user key, only while local PC runs); PREMIUM planned 299k optional user-supplied AI API + profitability analysis. Prices and trademark not verified. Technical system: Python 3.11+, SQLite schema v1 with immutable revisions, stdlib XLSX, ReportLab+local permitted Korean TTF PDF, localhost read-only HTTP HTML/CSS/JS browser. No mandatory cloud/paid tool/data egress for BASIC.

## 2. Implementation to date / this turn's changes and rationale
P1-01 strict importer, P1-02 conservative rule evidence, P1-03 SQLite revision/backup, P1-04 report CLI. P2-01 local readonly viewer/7 themes, P2-02 global favorites readonly POST, P2-03 profile JSON editor + backup-required CLI apply/reassess, P2-04 CAS and query/detail/modal fixes, P2-05 immutable report replay/synthetic smoke, P2-06 XLSX error cleanup and new-company onboarding, P2-07 one-click readonly historical XLSX download.
P2-08 code committed:
- backend/viewer.py: _arg accepts individual max_length: 300 for source_id, bid_no, profile; ordinary parameters retain 160 default. Older 160 shared limit hid valid 220/300-character IDs from detail. GET path bound raised from 1024 to 12288 encoded characters to support Unicode/Korean IDs (300 Korean chars per ID may be thousands of percent-encoded ASCII bytes). URL still capped (414 above limit), parse_qs max 12 fields, parameter-binding and Host/Origin/loopback restrictions preserved.
- backend/bidowl/store.py: optional `expected_profile_version` for assess_and_record; positive-int validation and check under BEGIN IMMEDIATE lock BEFORE evaluation/saving. Stops another process changing company profile mid-batch and giving the current command silently mixed versions.
- backend/profile_workflow.py: forwards planned revision to each assessment; tracks whether profile update itself committed, so post-commit race is correctly reported as PARTIAL_WRITE with backup even with 0 assessments, not deceptively CONFLICT_NO_WRITE.
- tests/test_viewer.py +1 method with 220-character **Korean** triple source/bid/profile ID; actual GET with percent encoding plus oversized request 414, direct query and profile list; explicitly commit/close fixture SQLite writer for Windows temp cleanup.
- tests/test_store.py +1 expected revision conflict/history preservation test.
- tests/test_profile_workflow.py +1 injected racing post-write conflict with backup retained, history and partial write semantics.
- STATUS, NEXT_TASK, HANDOFF updated. These are actual committed changes; Python runtime success not asserted.

## 3. Actual test commands, passed vs unexecuted
On an authenticated exact full private checkout under backend:
  python -m unittest discover -s tests -v
  python smoke_local.py
  node --check ui/ui.js
Windows helper:
  powershell -ExecutionPolicy Bypass -File .\verify_local.ps1
GitHub directly inspected eight test source files and identified **131 unique test method definitions** (eligibility27, importer21, profile_workflow12, report21, report_existing10, smoke_local1, store29, viewer10), no duplicate method names in each file. **131 NOT RUN; do not report PASS**. Historical P1 96 PASS Linux 2026-10-26 only on older source; historic mock smoke not full current integration. Exact current remote ui.js V8 Function syntax parse PASS. Static readback checked CAS guard before INSERT, planned version wired, error-classification flag, max_len and bounded URL. No CPython full checkout suite, Windows/Edge browser, native PDF/Excel or actual DB integration executed in this turn. GitHub Actions read-only check found zero existing workflow runs for feature branch; no CI job initiated.

## 4. Current stage and stop
P1 source complete; P2-01..08 source implemented, but full QA and real Windows browser interactions pending. P2-08 stops after code tests + handoff + branch/author verification. NEXT P2-09 must prioritize genuine full 131-run test before more unrelated feature work; fix actual failures and rerun. Then Windows 11, Excel/PDF, input path usability, 7 themes and 10k record benchmark. Future P3 official API, P4 opt-in AI, P5 Windows packaging/security, P6 KIPRIS/trademark/sales remain unshipped.

## 5. Errors, attempts, blockers and non-retry
Private clone previously failed due sandbox DNS/auth; signed raw.githubusercontent.com and api.github.com download similarly inaccessible from Python/container; authenticated GitHub connector can read/write source but not transparently mount entire private checkout in local container. Do not repeat same failing download or run old /mnt/data/bidowl_p2 stand-in and claim current source tests pass. Prior Chromium localhost attempts were blocked ERR_BLOCKED_BY_ADMINISTRATOR, not proof of app failure; real Windows Edge/Chrome or authorized full checkout is appropriate. No GitHub Actions jobs on feature branch; avoid creating paid GitHub Actions job without permission. Two external-reader questions remain: (1) user Windows testing/browser Blob/XLSX, (2) full Python suite. Keep status unverified until measured.
SQLite profile and assessments are individually committed; multi-bid reassessment can partially commit if interrupted. Backup before profile mutation retained, no automatic unsafe rollback. XLSX/PDF paired reports are best-effort partial-file cleanup, not crash-atomic.

## 6. GitHub repository, commits, paths and protected baseline
Private https://github.com/hibi89/Bid_Owl repo id 1399359397, branch feature/bid-owl-v1-basic-mvp. Starting P2-08 SHA 37e4af25c45906b6614313b016446f86340eaf3a. Source/fixture commits of this task:
  1e79c67beb7e0eb7b7e549cf4ab4a5a59fbb6559 viewer _arg limits;
  e546535568d0faedf33d28ab9ef42b89e8ca5146 viewer Korean ID test;
  fb3768a12c8152842b460d72701a4e3f03408b87 store pinned revision;
  c371d0b953b2a459f4d93bc2d4f277cd2d09b2bf profile reassessment pin and truthful conflict;
  6794464ed3696ce4ff0b5340e4068f76f3c41872 store test;
  6aaf32d46433ef55d9484b5cb2e79d18cdf6340e profile race test;
  c5966177335ea0ffa5f5dfc04660592d280fdbbf Windows writer fixture close;
  739291f138d70bea07d2169c93ec44f0dbad1669 raised bounded URL size;
  e29d154af5b794dfb3adb0c1702823d638016151 Korean GET regression.
Docs commits follow. Main baseline c888c795bef72734f3f7016e54013b82453f11d8; original legacy rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Must verify final main and feature SHA/author after HANDOFF commit.

## 7. Production, local URL, commands/environment
New BID OWL localhost Python NOT deployed: N/A public production URL. From backend, `python viewer.py --db ./demo.sqlite3 --port 8765`, browse http://127.0.0.1:8765 on same PC. Historical XLSX local download uses GET /api/report?assessment_id=N; PDF replay still CLI `python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./new-reports --format pdf` with installed licensed local TTF and ReportLab. Existing separate 2025 school static demo Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ untouched, legacy Production URL/SHA/live HTTP not verified. No Windows native Excel/browser run in this sandbox.

## 8. Security, user data, backup and permission rules
Main school-demo 340/340 static QA and old date are unrelated to new product. Never change main/Vercel/permissions/domain/product launch or force push without explicit permission. Never upload private customer database, CSV, contracts, API keys, credentials, PDF/XLSX, font files or .env to GitHub. Local DB versioned immutable historical evidence; backup_to refuses overwrite; apply requires explicit --apply and unique backup; new reassess pins version. Viewer is read-only on 127.0.0.1 with Host/Origin/CSP/Fetch Metadata checks. No external/paid service or procurement API invoked. BID OWL legal trademark/KIPRIS unresolved, price unvalidated.

## 9. NEXT P2-09 priority and required acceptance
1. Actual current-branch complete private checkout: run all **131 declared tests**, collect pass/fail/errors/skips; run `python smoke_local.py`; run `node --check ui/ui.js`. Fix failures, only then claim integrated QA. No automated future running without an actual automation.
2. Synthetic concurrency exercise: another process modifies company v3 after v2 save, verify no assessment silently saves on v3 under planned v2; accurate PARTIAL_WRITE and backup. Verify direct/viewer HTTP long Korean IDs and 414 bound; no DB write.
3. Windows 11 Edge/Chrome real visit: 7 themes/mobile, keyboard, new/edit JSON Blob downloads, direct XLSX in Excel, PDF with Korean TTF, same-origin/host errors and temporary file cleanup. 10k-list/detail benchmark with grounded measured latency. No claims until run.
4. BASIC still requires CLI for CSV import, profile apply and PDF; customer-ready packaging/UX unfinished. If considering HTTP mutation, design authentication/CSRF, backup/restore and obtain approval first.
5. Only after BASIC gate: P3 official customer-key API, P4 customer-opt-in AI, P5 packaging/security, P6 trademark/sales.

## 10. Last checked date and continuation
2026-10-27 KST. Remote code and branch source checked via GitHub connector; 131 tests are source inventory, not executions. JS V8 syntax and static guard checks PASS. User ㄱ resumes P2-09. This HANDOFF commit is latest expected HEAD; verify actual SHA and hibi89 author/committer at end.
