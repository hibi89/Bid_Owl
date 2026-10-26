# BID OWL P2-21 — local viewer query behavior and performance

The Windows/local browser remains read-only and binds only to 127.0.0.1. This change is backend-only: no CSS, layout, product tiers, private customer files or live procurement API changes.

## Before (P2-20)
`query_bids` called `_latest_rows` for **every stored bid** before applying category, keyword, deadline, favorite or pagination filters in Python. The SQL join included a correlated query to find a saved assessment for every bid, plus company profile and engine provenance. Even page 1 with 30 rows therefore caused up to all 10,000 bids to join assessment history and decode their full bid payload.

## P2-21 fast path
1. Validate all HTTP filter parameters with the existing `_arg` bounded parser. If a `status` filter was requested, retain the existing full historical logic, including UNKNOWN-first and current rule-engine fingerprint checks.
2. With no status filter, read `bids JOIN bid_versions` for the current bid metadata only, without joining `assessments`, `profiles`, or `assessment_engine_provenance` for every row.
3. Preserve original Python Unicode `casefold()` substring search, category equality, latest bid/source identifiers, actual timezone-aware `_timestamp` deadline comparison, and lexicographic deadline/source/bid sort. Build categories from the entire corpus **before** restricting favorites/search/category, matching legacy semantics.
4. Count filtered matches and choose requested page keys (max 100), then call `_latest_rows(..., candidate_keys=keys, as_of=now)` ONCE to get their full latest assessment/evidence/provenance. A parameterized row-value `IN ((?,?),(?,?))` query avoids user-input SQL construction and honors the 100-result page bound. Reorder by the Python selected key sequence, not arbitrary SQLite IN order.
5. Use one readonly SQLite snapshot (`BEGIN`/`ROLLBACK` only if the caller has not already started a transaction) so list metadata and saved assessments cannot come from different intermediate commits. Page selection and row expiration use the same UTC cutoff.
6. Return the unchanged output shape: `items`, `total`, `categories`, `page`, `page_size`, `generated_at`, and `notice`. No persistence, customer data upload, cache or writable route.

## Correctness and performance gates

- `backend/tests/test_viewer.py` adds an exact before/after comparison across **17** combinations: Unicode/casefold, category, open/expired, paging, empty page, long profile selection, explicit status (legacy branch), favorites including empty/unknown, and sort ties. Two additional tests assert only page-sized assessment lookup and avoid a full assessment scan for empty favorites.
- `backend/tests/test_benchmark_local.py` adds two tests for the opt-in baseline comparison. `backend/benchmark_local.py --compare-full-scan` measures actual legacy full-assessment page 1 against the new metadata-first page 1 with the *same* temporary 10,000-bid test data, verifying identical full-page items/count/categories. No new expensive 10k baseline during ordinary unit tests.
- A separate Python/sqlite3 sandbox probe with 10,000 fake bid metadata rows confirmed SQLite row-tuple parameter binding, 30-key selection, readonly transaction ending. It is **NOT the actual private BID OWL suite or its measured Windows speed**. Current full Python test definitions total 238; actual complete run and Windows GUI/Excel/PDF/installer/performance are still unverified.

## Limits and next task

All bids are still decoded from JSON for metadata sorting, so this is not an indexed LIMIT/O(log N) query or proof of specific latency improvements. Status filters still use full `_latest_rows`; next backend task P2-22 should consider a safe status-filter optimization with differential tests including stale provenance and UNKNOWN semantics. Avoid applying SQL date or Unicode lower/LIKE filters that change existing Python semantics. Never present benchmark fixtures as real customers or verified bid data.

UI visual redesign remains explicitly deferred by user request.
