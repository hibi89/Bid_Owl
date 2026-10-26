# BID OWL NEXT_TASK — 2026-10-27 KST

Repository: hibi89/Bid_Owl (private). Only feature/bid-owl-v1-basic-mvp may be changed for these tasks. Main/Vercel untouched. Resume commands: [Bid_Owl 깃헙 레포지토리 보고 작업이어가셈], ㄱ.

## Completed in source (not all integration-verified)
- P1-01 importer, P1-02 eligibility, P1-03 SQLite, P1-04 CLI PDF/XLSX. Previously 96/96 PASS Linux on 2026-10-26.
- P2-01 127.0.0.1 SQLite mode=ro read API, responsive UI, seven themes, evidence panel, profile/status/category/expiry/text search, conservative stale result UNKNOWN; 5 synthetic P2 tests previously isolated PASS.
- P2-02 global favorites read-only JSON POST /api/bids/favorites, 1,000-ID/1-MiB bounds, same-origin policy, allowed filter fields, global search+filter+pagination before slicing. Browser-local favorites do not mutate SQLite. Added 2 regression test methods (total 7 P2).
- SOURCE code commits: 016ab8c251f92628e17ccd6e102b374284d20608 (Python), 823edf48d31ed0077cdd0c700f20594f59b44b68 (JS), cd05d6d56daf6613c7f7ebe11c558a60f3cfe7d9 (tests). Documentation follows; always query current GitHub SHA.
- JS exact GitHub source syntax parse PASS (via JavaScript Function compiler). Python added helper snippet local ast.parse PASS. New integration tests committed, NOT RUN. Container GitHub raw signed-download failed DNS resolution: no actual full repo checkout, no 103-test success claim.

## NEXT P2-03: integration verification, profile workflow and BASIC UI closure
1. Fetch current GitHub HEAD, HANDOFF, STATUS, AGENTS, REQUIREMENTS and source. Check no concurrent changes.
2. Using **authorized original repository checkout**, run `cd backend && python -m unittest discover -s tests -v` (expected 103 tests, NOT verified), `node --check ui/ui.js` and a synthetic complete CSV -> SQLite -> PDF/XLSX -> GET UI -> global POST favorites smoke. If a test fails, fix minimally before more features. Do not retry raw.githubusercontent.com from this restricted container unchanged.
3. Design profile editing/evaluation flow comparing CLI-only and a controlled localhost write API. Make backup/restore, source revision audit, explicit user action, CSRF protection, safe path handling and data preservation first-class. User approval required for original source/data/security modifications; do not silently add an unrestricted write route. Implement safe local functions/UI after decision.
4. Replace static/prototype screen nav labels with accurate live functionality when available, ensure correct no-profile/unknown/stale/expired outputs and category filters. Measure 10k-bid query performance.
5. Windows 11 real Chrome/Edge desktop+mobile/7-theme keyboard/screen reader/contrast and native Excel/PDF integration. Browser automation from previous environment blocked with ERR_BLOCKED_BY_ADMINISTRATOR; stop unchanged attempts here, use another permitted environment.
6. Update STATUS and HANDOFF with measured tests/sha/actual product verification. Keep all customer DBs, document uploads, keys, reports and fonts out of GitHub; main/Vercel untouched.

## Future and guardrails
P3 official government tender API (approved key, incremental amendments, quota recovery); P4 optional user-key AI; P5 Windows installer/data safety/security; P6 pricing/branding/KIPRIS and sales release gate. Do not claim procurement qualification, official API connectivity, product release or Windows verification before actually proven. No paid service, external upload, GitHub main merge or production deployment without explicit approval.

## Remaining blocker
Full private-repository checkout/tests in this execution container impossible due DNS; signed raw single-file fetch was attempted after earlier clone auth/DNS and also failed. JS syntax passed, Python patch local isolated syntax passed. Actual new HTTP POST tests and browser interaction, official data and Windows machine remain UNVERIFIED. Same-browser localStorage favorites cap 1000; no cross-browser persistence until a designed migration.