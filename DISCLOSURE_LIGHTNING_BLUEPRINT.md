# DISCLOSURE LIGHTNING — PRODUCT BLUEPRINT
**2026-10-27 KST · user-chosen product name · DESIGN STARTED / no engine migration or live SEC requests completed**
**Exact English spelling: Lightning, NOT Lightening.** Meaning: fast discovery/fetch/update of public disclosures with version-aware evidence, not predicting lightning-fast returns or circumventing official rate limits.
**This document is on an isolated transformation branch** `feature/disclosure-lightning` forked from `feature/bid-owl-v1-basic-mvp`. The original BID OWL source/product/branches and private source rights remain intact. GitHub repo is still `hibi89/Bid_Owl` until the owner manually renames the repo via GitHub Settings; do not represent it as already renamed. No new repository was created. No public repo or code copying to a public KIC repo without deliberate owner licensing and attribution decision.

## 1. Distinguish three products/pipelines
1. **Disclosure Lightning (THIS transformed BID OWL):** fetch and monitor *authorized public* global regulatory filings fast and accurately, maintain CIK/corp identifiers, filing type, official source URL, published/fetched/as_of times, amendments/revisions, content hashes, changed items, delta records and immutable raw evidence. Prime source SEC EDGAR for KIC global relevance, optional OpenDART for Korean markets. Do not pretend to hold KIC private deals or all-world realtime news.
2. **One new universal Data Preprocessor (USER WILL CREATE SEPARATELY):** source-independent cleaning, parsing, schema inference with human review, dates/currencies/units/entity mapping, missing/anomaly/duplicate checks, structured facts linked to original spans, versioned datasets and quality reports. Its source/owner repo/name NOT created or selected here, to honor user's "I will make one" and no unrelated new GitHub repo creation.
3. **Existing KIC ProofInvest Global:** validated financial/ownership/capital/industry reasoning, deterministic investment-memo checks, conditional ML on time/group-correct real labels, document DL for grounded extraction, user-facing due diligence report. This is not an automatic buy/sell bot. Inputs from Lightning/Preprocessor use a documented versioned interchange contract, not tight import of a private repo.

```text
SEC EDGAR official APIs (P0), OpenDART official APIs (P1)
    │ lawful incremental source discovery & retrieval
    v
Disclosure Lightning [source IDs + immutable raw filing + change feed + source provenance]
    │ RawFilingEnvelope schema v1 (json + raw content references, hash)
    v
Independent Data Preprocessor [type/unit/year/currency/period/entity/section → quality gates]
    │ NormalizedFactEnvelope schema v1 [quality + evidence + refusal]
    v
ProofInvest Global [financial deterministic checks + ML + pretrained DL + interactive due diligence]
    │ defensible source linked investor research report
    v
Human analyst
```

## 2. Core workflows
- User inputs CIK or approved issuer name+disambiguated ticker and selected filing types (10-K, 10-Q, 8-K, S-3, 424B etc.; 13F as a separately typed manager portfolio filing), date window, as-of cutoff and data scope. Never use ticker as sole legal identity; SEC CIK is central identifier. Track CIK and accession number. Track 13F manager ID and holdings quarter; 13F is delayed and incomplete, not live global holdings.
- First list official submissions; fetch only desired unread/accession/new/changed filings with caching, HTTP cache validators where official server supports them, hashes and bounded concurrency. Record request ID, status code, source published vs retrieved timestamp, retries, content type/size and immutable digest.
- Compare edition/amendment references, authoritative status and raw evidence; do not silently replace older report versions. A new 10-K/A may amend 10-K and still not justify overwriting every old fact. Preserve point-in-time reconstruction and document status.
- Search/filter by company, filed date, form type, financial-events facets, explicit uncertainty; show what changed, with source link and timestamps; export JSON and CSV evidence manifest. No invisible auto-notification/always-on server unless separately implemented.
- Network isolation and controls: contact-bearing transparent User-Agent as required by applicable official access policy, per-domain global rate limiter, bounded concurrency and exponential backoff with Retry-After where applicable. Respect published fair-access and robots/ToS (not evasion), streaming size limits, read-only provider endpoints, bounded disk use, secrets in OS store; no paid API as default.
- **Success is retrieval provenance/coverage and measured update latency UNDER permitted API limits, not reckless more-requests/second.** Record provider HTTP latency, cache hit rate, duplicate avoidance, missed-amendment rate, stale-feed detection; never promise instantly all-world coverage.

## 3. MVP in KIC deadline order
**P0 SEC demo (before KIC Nov12 prelim):**
- `SEC Submissions` (selected issuer metadata and listing) and `Company Facts` (annual/quarterly XBRL where available) as separate official read-only connectors. Full text 10-K/10-Q original HTML download only after explicitly verifying correct official URL and access. All request shapes and policies from https://www.sec.gov/edgar/sec-api-documentation and https://data.sec.gov.
- Demo on 2 US-listed issuers and a tiny set of dates, with source citation and form IDs. Import local fixtures first, then optional owner-authorized live one-shot. Do not claim as real data without verified HTTP evidence.
- SQLite schema for `issuers`, `filing_index`, `filing_versions`, `fetch_observations`, `source_hashes`, `sync_checkpoints`, `export_receipts`; uniqueness by provider/CIK/accession/filing part; append new observation, never erase original.
- API endpoints minimal: `POST /plan` (read-only simulated request), `POST /sync` (requires owner auth explicit network enablement), `GET /issuers/{id}/filings`, `GET /filings/{key}/provenance`, `GET /export/raw-manifest`. API proposal not implemented. Use local-first DB/version model; final app UI not priority.
- Verify: initial import, identical re-run creates zero duplicate filings, 10-K amendment preserved, stale/as-of exclusion, ticker CIK mismatch => unresolved, 429/retry and abort/resume, bad XML/JSON, malicious entity resolution, temp file failure, offline last-updated display. KIC must accept either direct official fetch or clearly documented fixture as appropriate; do not make Lightning compulsory for PDF completion.

**P1 post-initial:** OpenDART adapter (official corporate code, filings list, original XML, structured finance, shareholding, capital). APIs require applicant key; owner gets key, never in repo. https://opendart.fss.or.kr/guide/main.do. KIC uses SEC first due global institution alignment.
**P2 after valid submissions:** broader SEC forms and 13F manager holdings with limitations, industry changes, brokered user notifications, multi-country lawful connectors, eventual enterprise reliability/performance profile.

## 4. Reuse map from BID OWL private feature
| Source assets | Preserve/adapt | DO NOT copy verbatim |
| --- | --- | --- |
| `backend/bidowl/store.py` SQLite versioned imports / immutable evidence | adapt to issuer/accession and amendments, source hashes, no-overwrite backup/restore | procurement `bid_no`, `profile_id`, bid qualification states as financial facts |
| `backend/bidowl/engine_identity.py` deterministic fingerprint | fingerprint parser/adapter rule version for replay and stale result invalidation | call algorithm's PASS a disclosure verification result |
| `backend/viewer.py` local read-only HTTP list/detail & pagination | adapt filing metadata search, time/revision/historical data and provenance | original procurement bid deadline / region / profile joins |
| `backend/bidowl/eligibility.py` evidence status `PASS/FAIL/UNKNOWN` | adapt evidence verification to `VERIFIED/CONFLICT/UNKNOWN` with strict original-document source refs | staff/license/bidding company eligibility checks |
| report/export and local CLI | adapt source-backed export and QA receipts | label old synthetic demo data as real SEC or completed filing ingestion |

Keep old feature `feature/bid-owl-v1-basic-mvp` and `main` protected; transformations only on this new branch. Do not rewrite history or rename/move user files until verified. Respect GPL/third-party component terms if introduced.

## 5. Interface contracts
`RawFilingEnvelopeV1`:
```json
{
  "schema_version": "1.0",
  "provider": "SEC_EDGAR",
  "issuer_id": "CIK:0000000000",
  "filing_key": "CIK:0000000000/accession:EXAMPLE",
  "form_type": "10-K",
  "filed_at": "2025-01-01",
  "accepted_at": null,
  "collected_at": "2025-01-02T03:00:00Z",
  "source_uri": "https://www.sec.gov/...",
  "content_sha256": "HEX_OF_VERIFIED_BYTES",
  "raw_reference": "user-approved-local-file",
  "amends_filing_key": null,
  "as_of_cutoff": "2025-01-02",
  "evidence_status": "UNVERIFIED_SAMPLE"
}
```
Example keys and values are **placeholder format only**, not actual accepted SEC documents.
`NormalizedFactEnvelopeV1` produced by independent preprocessor:
```json
{
  "schema_version": "1.0",
  "filing_key": "CIK:.../accession:...",
  "metric": "operating_cash_flow",
  "value": null,
  "currency": null,
  "scale": null,
  "fiscal_period": null,
  "statement_basis": null,
  "source_span": null,
  "source_hash": null,
  "normalizer_version": "planned",
  "quality_status": "NEEDS_REVIEW",
  "human_review_required": true
}
```
**No fabricated value allowed.** Both data contracts are proposed and require KIC downstream approval. The preprocessor must produce a reproducible transformation log (source locator/span, rules, warnings) and never silently impute financial results as official evidence.

## 6. Quality / done gates
- `DESIGN`: this document committed; no change to primary old BID OWL behaviors.
- `IMPLEMENTED`: SEC connector and store code in isolated branch + offline unit tests and tested fixture mapping.
- `VERIFIED_LIVE`: explicit owner authorization, real official API received + IDs/hashes/links validated, measured rate/failure/retries and persisted receipts.
- `INTEGRATED_KIC`: versioned pipeline consumed by ProofInvest with no direct private source leak and end-to-end trace across a real filing, all rights checked.
- `RELEASED`: user-approved public or private distribution, original BID OWL license/branding decision, Windows/API/legal/security QA; not an assumed outcome.

## 7. Brand/repo migration and user approval
- User selected product label **Disclosure Lightning**, rationale "공시를 번개처럼 가져오는 느낌". Correct exact spelling is **Lightning**. Brand/trademark availability NOT legally cleared.
- No GitHub rename API action is currently exposed in this tool session. Owner can later rename **existing private** `hibi89/Bid_Owl` through **Settings → General → Repository name → Rename** to `Disclosure_Lightning`; links/CI/local clones must be reviewed for fallout. Do not rename until owner decides to stop separate Bid Owl commercial development and the new identity becomes primary. Branch + design is safe reversible step.
- One **separate user-requested preprocessing project** is an explicitly considered exception to prior no-new-projects rule; do not create that repository on user's behalf until they provide its final name/target or explicitly ask. No unrelated repos created.
