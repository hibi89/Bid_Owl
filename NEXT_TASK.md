# BID OWL NEXT_TASK — 2026-10-26 KST

Repo hibi89/Bid_Owl private; feature branch feature/bid-owl-v1-basic-mvp. main at c888c795bef72734f3f7016e54013b82453f11d8 preserved. User ㄱ advances to the first incomplete task.

## Completed verified stages
P1-01: CSV validation and import, 21 tests.
P1-02: profile and 3-state evidence-gated evaluator, 27 tests.
P1-03: local SQLite versioning/rollback/audit/backup, 28 tests.
P1-04: real local CLI flow + PDF/XLSX files + user source evidence, 20 tests.
Full locally reconstructed code suite was compared with GitHub exact blob SHA and run together: 96 PASS / 0 FAIL. Synthetic CSV 2 rows generated PDF 2 / XLSX 2. Korean font rendered, XLSX OOXML parsed and imported. See STATUS and HANDOFF for verification scope.
Pending: actual Windows device, Microsoft Excel native opening, official procurement input, installed Windows product, external API, Production web app, legal review.

## NEXT: P2 BASIC usable UI, localhost bridge, 7 themes
1. Confirm current feature HEAD and docs. Keep old static educational main unchanged. Do not display old 2025 precomputed result or 340/340 as live status.
2. Build safe localhost-only Python read bridge for SQLite-derived bids, company profiles and current assessments. Avoid unrestricted filesystem paths or network exposure; keep customer data local and requests read-only.
3. Search by bid title/agency/no, field/category, deadline, evaluation status. Show data timestamp, per-rule evidence, UNKNOWN review status, favorites and deadline risk.
4. Seven theme tokens: cloud, obsidian, midnight, graphite, emerald, sand, iris per DESIGN_SYSTEM.md. Mobile responsive.
5. Test supported backend and JS; actual browser where possible. No production deploy without approval.
6. Windows smoke test using Python/ReportLab/local TTF/native Excel and SQLite reopen/backup before commercial readiness.

Future: P3 official procurement API amendments/quotas, P4 opt-in AI, P5 Windows installer/security, P6 trademark/Kmong launch gate.

A storage commit and separate report generation are not cross-resource atomic. If PDF/Excel fails after DB save, explain partial output; do not present it as fully recovered. No real customer data or API secrets ever enter GitHub.
