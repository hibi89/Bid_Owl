# BID OWL — HANDOFF (2026-10-26 KST)
Continue with \`[Bid_Owl 깃헙 레포지토리 보고 작업이어가셈]\` or \`ㄱ\`. Read HANDOFF → STATUS → AGENTS → REQUIREMENTS → NEXT_TASK → source. No repeated design questions.

## ① Goal / confirmed scope / stack
BID OWL (비드아울), Windows 11 local procurement screener for small businesses (not legal advice or bidding execution). BASIC 59,000 KRW: CSV/company profile/PASS-FAIL-UNKNOWN evidence/filter/report. PRO 149,000 KRW: official procurement API incremental updates and local alerts only while computer is running. PREMIUM 299,000 KRW: opt-in customer AI key, PDF/DOCX source evidence, cost simulation. One-time fees, mandatory subscription 0 KRW target (not verified); 7 themes cloud/obsidian/midnight/graphite/emerald/sand/iris. Python + SQLite + selectively reused web UI. Definitive source: REQUIREMENTS.md / ROADMAP.md.

## ② Completed features / changes / decisions
Main retains old BID INSIGHT 2025-08-10 static educational web demo with 20 static records, simulation and displayed "340/340" (NOT live test). P1-01 CSV importer+schema+synthetic example+unit tests completed previously. P1-02 now completed in separate feature branch: CompanyProfile strict typing (None unknown, empty list explicitly none), evaluation of 5 rules, exact string matching, FAIL > UNKNOWN > PASS aggregate, each condition's code/source/explanation/needs-review, checked_at/data_as_of and expired separate, final_approval_required always True. Missing text or locator, unsupported rule, missing company data => UNKNOWN. Mixed FAIL+UNKNOWN remains FAIL but unresolved rules are still reviewed. New files backend/bidowl/profile.py, eligibility.py, tests/test_eligibility.py; __init__.py exports extended, legacy untouched.

## ③ Test commands / counts / verified and unverified
From backend: \`python -m unittest discover -s tests -v\` (expected full suite when exact checkout available). This turn P1-02 tests run locally via Python 3.13.5 Linux with local matching Bid/Requirement schema stub: **27 PASS / 0 FAIL / 0 SKIP**; blob SHA matches GitHub for profile.py (db0268504d45260f0046d2e5bd62adf529a5a2bb), eligibility.py (2fb113598a2c7a24c79b8fb26bc904994edd5670), test_eligibility.py (50ad4872f1f8219809b8c4429b50a54197c20537). Previous P1-01 run 21 PASS / 0 FAIL separately; FULL combined regression not run now. User-facing 48 combined PASS cannot be claimed yet. Official CSV, SQLite, Windows, generated reports, actual legal rules not verified.

## ④ Done / work-in-progress / pending / blockers
Done P1-00/01/02 at module level. NEXT P1-03 SQLite storage+tests. Then P1-04 CLI/report, P2 UI+themes, P3 PRO API, P4 PREMIUM AI, P5 Windows packaging/security, P6 sales. Windows, service API key, third-party AI and brand sales verification pending; local engineering can continue without them.

## ⑤ Errors/evidence/retry restrictions/alternatives
Prior P1-01 test_missing_header had incorrect fixture, was corrected then passed; don't reintroduce. During P1-02 review found mixed FAIL+UNKNOWN had aggregate requires_human_review False; fixed to reflect unresolved condition, added assertion; final 27 PASS. No external/prod errors observed. Private repo not cloned into Linux runtime; copied exact class surface in local test stub, so combined importer regression unverified. Obtain source checkout or deterministic full bundle next for 48-case suite rather than pretending integrated verification. No force push or codebase replacement.

## ⑥ Repo/branch/SHA/paths
Private GitHub https://github.com/hibi89/Bid_Owl, repo ID 1399359397. main **c888c795bef72734f3f7016e54013b82453f11d8** unchanged. feature **feature/bid-owl-v1-basic-mvp**, P1-02 code commit **fa2ed6aea6c634490d1f467bc1a3c3788df6adb1**; subsequent docs commit becomes feature HEAD, read latest before next work. Earlier P1-01 SHA 3e4faa759693ea4343dd73ae0d7ac6053eb0e30b. Restore demo snapshot 2807a93a3e0deba98840712401fdd6025e6f5610. Work in backend/bidowl and backend/tests.

## ⑦ Production URL/Vercel/runtime
Previous Vercel legacy project project08-bid-insight, ID prj_YcrN7OdOjKl6M457HelGIItLeeXZ. Production URL/actual SHA/UI/API/HTTP behavior not verified, only prior READY metadata. Python feature branch is not deployed (not applicable). Local run Python 3.13.5 Linux, \`cd backend && python -m unittest discover -s tests -v\`; actual Windows 11 unverified. No Vercel configuration changes.

## ⑧ Original/backup/auth/immutable assets
Main is original static educational demo; retain original Git SHAs above for restore. No credential, env, personal/bid file, report PDF, customer SQLite database in GitHub. Code+schema+synthetic fixtures only. GitHub connected account hibi89; no changes to auth/committer identities/domain. No external AI requests nor paid calls. Never interpret simulated old UI data as real current bids.

## ⑨ Next actions/priority/done/approvals
NEXT_TASK.md P1-03: SQLite schema version, SQLite transactional imports, bid revision/idempotence, normalized source and profile, evidence/decision snapshots, audit trail, reopen/rollback tests. Obtain exact GitHub project source in test runtime if possible, then run entire 48+ tests together. Source review → edit feature only → tests → source SHA/committer check → STATUS/HANDOFF update. P1-04 afterward. User approvals only needed for production changes, paid API, credentials, source/customer data external transfer, or public brand release; not local module development.

## ⑩ KST update/check/time/scope
Updated 2026-10-26 KST. Confirmed through GitHub code SHA **fa2ed6aea6c634490d1f467bc1a3c3788df6adb1** and Linux P1-02 27-test run, with new blob hashes matching remote. Docs live commit SHA must be checked at next resume (cannot refer to itself before commit). No live Windows/Production verification or sales assertions.
