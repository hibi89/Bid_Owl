# BID OWL HANDOFF — 2026-10-26 KST

## 1 Goal, requirements, architecture
BID OWL/비드아울 Windows 11 local procurement screener for small businesses. BASIC KRW 59,000 CSV/profile/evidence PASS-FAIL-UNKNOWN/Excel-PDF; PRO KRW 149,000 government API incremental records and local-PC-running alerts; PREMIUM KRW 299,000 opt-in customer-key AI document analysis and cost simulation. One-time fees and 0 KRW required recurring fee are targets, not validated. Python+SQLite with existing static HTML/JS/CSS assets selectively reused, 7 themes. No legal qualification guarantee, autobidding or award guarantee.

## 2 Completed functionality and decisions
P1-00 repository protection; P1-01 CSV parser; P1-02 5-category literal-rule decision engine with provenance; P1-03 local SQLite revision history/profiles/assessment evidence/backup; P1-04 complete CLI path CSV+profile→SQLite→3-state evaluation→Excel and Korean PDF. report.py + cli.py + tests/test_report.py + fixtures/sample_profile.json + requirements.txt. PDF uses ReportLab BSD, local Korean system TTF/NanumGothic SIL OFL; never commit font files. XLSX uses Python stdlib ZIP/OOXML. Old 2025 education demo/340/340 legacy display preserved, not new product QA.

## 3 Tests, counts, verified and unverified
Run cd backend then python -m unittest discover -s tests -v. CPython 3.13.5 Linux: 96 PASS / 0 FAIL / 0 SKIP; breakdown 21 importer + 27 eligibility + 28 SQLite + 20 CLI/report. All 9 pre-existing Python source/test files reconstituted from locally retained original files and matched their GitHub git blob SHA; new SHA report.py 676537995c6f697d30cb773062a0b3bc6e6fe585, cli.py 8561fb39bdb1a037ad6bdc48f329d31ab6766a68, tests/test_report.py 17f31db5ce4050b019eb35dc5631ef8e704cd20f, sample_profile.json 67d8d2d3d21ecf915d4a2322fd9a585c5f624b88. Synthetic 2-bid complete run produced 2 PDF + 2 XLSX; PDF Korean render and embedded font, XLSX valid XML/ZIP and artifact_tool opened. Windows 11/native Excel/real official procurement/legal determination unverified.

## 4 Complete/in-progress/pending/blocked
P1 BASIC CLI module MVP done, not yet customer product. Next P2 BASIC UI/search/filter/7 themes and safe read-only localhost DB bridge; P3 PRO official API, P4 optional AI, P5 Windows installer/security/regression, P6 branding and sales. Windows actual execution and live official data pending, can continue local UI engineering. Trademark/KIPRIS and similar BiddingOwl unresolved, so public sales blocked.

## 5 Errors, causes, attempts, alternatives and avoid-repeat
Previous P1-01/02/03 suite had not run together; fixed by reusing local files with remote matching SHA, now 76 prior+20 new=96 PASS. Errors in input abort before DB creation. Missing PDF Korean TTF fails early but xlsx-only works. SQLite write and reports filesystem outputs are sequential; report failure may leave valid DB/audit persisted. Do not promise cross-resource atomic rollback; later implement re-export/resume. No repeated private Git clone attempt (prior DNS/auth), use connected GitHub read/write tools.

## 6 Repo, branch, SHA, paths
https://github.com/hibi89/Bid_Owl private repo id 1399359397. main HEAD c888c795bef72734f3f7016e54013b82453f11d8 unchanged; restore education snapshot 2807a93a3e0deba98840712401fdd6025e6f5610. Feature feature/bid-owl-v1-basic-mvp. Prior baseline 3de92cbb9f6b969ed2bf3abe83eb3060da2a391b; new P1-04 feature HEAD obtained by querying GitHub after commit. Paths backend/bidowl/{schema,importer,profile,eligibility,store,report}.py, backend/cli.py, backend/tests/test_*.py, backend/fixtures, backend/README.md.

## 7 Production URL, Vercel, run/environment
Old Vercel project project08-bid-insight id prj_YcrN7OdOjKl6M457HelGIItLeeXZ; previous READY metadata only. Current Production URL/SHA/HTTP/UI/API/browser not verified. New Python feature is NOT deployed (not applicable). Local run cd backend, python -m pip install -r requirements.txt, python -m unittest discover -s tests -v; synthetic CLI example in backend/README.md. Python 3.13.5 Linux tested, Windows 11 unverified.

## 8 Original, backup, secrets and no-modification boundaries
Original static education project stays at main, with Git rollback references. SQLite local backups via backup_to() disallow overwrite. Never push customer bids/PDF/Excel/database/API keys/.env/secrets/sensitive information. No font files distributed. GitHub writer connected account hibi89; check author/committer SHA. Do not modify main/Vercel/project rights, domain, authentication, paid API, public brand release without prior approval.

## 9 Next priority, procedure, completion and approvals
Read latest HANDOFF→STATUS→AGENTS→REQUIREMENTS→NEXT_TASK→code; implement P2 localhost read-only bridge and actual SQLite-derived searchable UI, not legacy 2025 scores. Add filters, favorites, drawer evidence, seven tokens, accessible responsive design. Unit/browser tests and Windows smoke as available; commits only feature, recheck remote SHA and docs. External keys/cost/data transmission, public sale, production environment changes require user approval.

## 10 KST update, verification boundary and document baseline
Updated 2026-10-26 KST; source baseline feature 3de92cbb9f6b969ed2bf3abe83eb3060da2a391b plus exact-source-tested P1-04 additions; commit SHA obtained after writing. Only local Python, PDF/XLSX and GitHub source-byte verification achieved; no native Windows or production app test. Resume prompt [Bid_Owl 깃헙 레포지토리 보고 작업이어가셈] or ㄱ for P2.
