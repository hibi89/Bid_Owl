# BID OWL — HANDOFF (2026-10-26 KST)

User resume: [Bid_Owl 깃헙 레포지토리 보고 작업이어가셈] or ㄱ. Read HANDOFF.md → STATUS.md → AGENTS.md → REQUIREMENTS.md → NEXT_TASK.md → source. Do not ask about already agreed name/pricing/architecture; take next unblocked development item.

## ① Goal / confirmed requirements / technology
BID OWL (비드아울), local Windows 11 procurement-opportunity screener. BASIC KRW 59,000 CSV/company profile/evidence-based PASS/FAIL/UNKNOWN, risk/deadline, Excel/PDF. PRO KRW 149,000 official procurement API incremental updates and local alerts while PC runs. PREMIUM KRW 299,000 optional customer AI key for PDF/DOCX text analysis and profit simulation. One-time charge/monthly mandatory 0 KRW TARGET, not validated. Python/SQLite and progressive reuse of existing JS/CSS/HTML, seven color themes. No legal qualification warranty, automatic bidding or guaranteed award; all verdicts require manual approval. REQUIREMENTS.md/ROADMAP.md are product source.

## ② Finished features / changes / decisions
P1-01 CSV validator/parser and synthetic fixtures; P1-02 immutable CompanyProfile and evidence-gated tri-state eligibility; P1-03 new backend/bidowl/store.py and backend/tests/test_store.py, updated __init__.py, backend/README.md and backend/.gitignore. SQLite schema version 1: bid key (source_id,bid_no), normalized content SHA-256, appended bid versions; profiles snapshot versions; assessment snapshots bound to bid/profile revisions, individual reason/source fields; import audits, all-or-none BEGIN IMMEDIATE transactions, consistent backup with no overwrite, reject unsupported DB schemas. Same latest content is unchanged; correction content becomes a new internal version. This does NOT implement official government amendment identifiers or automatic migration. Existing static 2025 educational demo (20 records; displayed 340/340) untouched.

## ③ Tests / commands / pass-fail / verification
Local Linux CPython 3.13.5: from backend, python -m unittest discover -s tests -v. **28 P1-03 tests PASS, 0 FAIL, 0 SKIP** using reconstructed source-compatible P1-01/02 modules. Tested import data integrity, changed bids, idempotency, profile revisions, new/old assessment provenance, atomic rollback on simulated SQL faults, duplicate source isolation, SQL parameter binding, reopening persistent DB, backup integrity and schema rejection.
GitHub store.py blob = 1a0c5f842212a22fe35ede7bf49a1519b2332cc3, test_store.py blob = cdcf218fe08103c2e345973ab48721a89c21c585, __init__.py blob = 80da95c71a29084035e38f3084df278e9ff6a727, same as local tested files. Prior separate P1-01 21 PASS / P1-02 27 PASS reports are not a single integrated run. Full exact GitHub checkout 76-case suite has NOT been executed. Windows/real-source/official API/reports/production not verified.

## ④ Completed / ongoing / pending / blocked
Done P1-00..P1-03 module scope. NEXT P1-04 CLI/Excel/PDF and full regression, then P2 UI/7 themes, P3 PRO official API, P4 PREMIUM AI, P5 Windows install/security, P6 brand-sales readiness. Missing external government key, optional AI, Windows real device and trademark review do not block offline feature engineering but block relevant rollout validation.

## ⑤ Errors, causes, attempts, retry restrictions, alternatives
Found SQLite Python sqlite3.executescript implicitly commits; avoided nested transaction and moved initialization DDL into explicit BEGIN IMMEDIATE/COMMIT script. Test after correction 28/28 PASS. Tests inject SQLite triggers and verify rollback retains state. No external tool failure/deployment attempted. GitHub private clone from local container unavailable (DNS resolution failed), so previous GitHub modules were reconstructed from retrieved source for isolated P1-03 test; remote store+tests+init exact SHA matched. Do NOT claim full checkout integrated regression. Alternative: supported GitHub connector materialization or authorized local checkout/CI before P1-04 release gate. Avoid re-running failed git clone unchanged.

## ⑥ Repository, branches, SHAs, important paths
Private https://github.com/hibi89/Bid_Owl (same repo ID 1399359397, renamed project08-bid-insight), main c888c795bef72734f3f7016e54013b82453f11d8 unchanged. Feature feature/bid-owl-v1-basic-mvp P1-03 code commit e1f3befafe1590570a99879812f678a5a60b99a1. A subsequent docs-only commit will be latest HEAD; query it when resuming. Legacy rollback 2807a93a3e0deba98840712401fdd6025e6f5610. Paths backend/bidowl/store.py, backend/tests/test_store.py, backend/.gitignore, backend/README.md, STATUS.md, NEXT_TASK.md.

## ⑦ Production URL/project/run/environment
Old Vercel project project08-bid-insight ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ. Historic READY metadata, but actual Production URL, web/Console/API, Git rename link and deployed SHA are NOT VERIFIED. Python local branch no deployment (not applicable). Test: cd backend && python -m unittest discover -s tests -v. Default database Windows LOCALAPPDATA/BID_OWL/bidowl.sqlite3; Linux XDG_DATA_HOME/bidowl/bidowl.sqlite3 (or ~/.local/share/bidowl). Actual Windows execution NOT VERIFIED.

## ⑧ Source/backups/secrets/forbidden changes
Original 2025 PWA preserved on main; Git history provides rollback SHA; SQLite backup_to() makes a new separately verified copy and prevents overwrite. Never commit actual bid inputs, customer data, credentials, PDFs, generated reports, .env, SQLite files. .gitignore improves local protection but isn't secret scanning. No modifications to main, Vercel config/aliases, authentication, billing, API, domains. GitHub connection hibi89, verify author/committer after docs commit.

## ⑨ Next steps, procedure, success criteria, approvals
P1-04: obtain exact GitHub checkout if possible, rerun all 76 existing tests together, implement CLI minimal real CSV->local DB->profile->rules->PDF/Excel, check Korean fonts/licensing/output readability and formula injection, then unit regression/commit/docs. Any unexecuted platform/manual validation marked UNVERIFIED. Public release/trademark, API keys, external data transmission, paid service, live deploy and security changes require user approval. Development on authorized feature branch may continue.

## ⑩ Updated KST, evidence boundary, doc baseline
2026-10-26 KST, verified GitHub source commit e1f3befafe1590570a99879812f678a5a60b99a1 and 28 P1-03 tests in isolated Linux Python 3.13.5 test environment. Docs commit exact SHA determined by following GitHub update; verify feature HEAD next conversation. Verified local SQLite and new file byte equality only; not verified full exact checkout, actual Windows, official data, or production.
