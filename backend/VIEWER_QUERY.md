## P2-22 — PASS·FAIL·UNKNOWN 상태 검색 최적화

기존 P2-21 메타데이터 우선 방식에 **상태 필터**도 포함했습니다. `query_bids`는 현재 공고 메타데이터를 읽고 키워드·카테고리·마감 상태·즐겨찾기를 먼저 좁힌 후, `_status_for_candidate_keys`로 남은 공고의 **최소 판정 현재성 정보**만 조회합니다. 공고 200건씩 최대 402개의 SQLite 바인딩 변수로 나누기 때문에 오래된 SQLite 파라미터 제한에도 대응합니다.

현재 상태가 PASS 또는 FAIL이려면 최신 공고 버전, 프로필 버전, 해당 프로필의 최신 평가, 저장된 규칙 엔진 SHA-256이 모두 맞아야 합니다. 하나라도 부족하면 UNKNOWN으로 분류합니다. 엔진 지문 테이블이 없는 구형 DB, 판정이 아예 없는 공고, 다른 프로필을 마지막에 평가한 공고 모두 보수적으로 처리합니다. 전체 판정·근거·상세 payload는 **상태 필터를 통과한 현재 페이지(최대 100건)**에 대해서만 조회합니다. SQL에 사용자 문자열을 삽입하지 않고 바인딩 파라미터로 처리합니다.

정렬·범주 목록·페이지·영문/한글 Unicode casefold·마감일·즐겨찾기 결과는 기존 `_latest_rows` 전체 평가 조회와 동일하게 유지하는 것을 목표로 회귀 테스트를 추가했습니다. 한 DB 읽기 트랜잭션 안에서 메타데이터 필터, 상태 판정, 페이지 상세를 모두 읽으며 호출자가 이미 시작한 트랜잭션은 종료하지 않습니다.

`backend/tests/test_viewer.py`에서 신규 7개 테스트 메서드: 상태 필터 비교, 구형/불일치 엔진 지문, 425건/3개 묶음, 즐겨찾기, 빈 즐겨찾기, 2개 회사 프로필, 호출자 소유 트랜잭션. `backend/benchmark_local.py --compare-full-scan`는 PASS와 UNKNOWN 페이지도 과거 전체 조회 방식과 **동일한 원본 데이터**로 비교하고 별도 시간을 기록합니다. 1만 건 합성 SQLite의 상태 분류 SQL을 독립적으로 50묶음 실행해 10,000/10,000 기준 결과 일치를 확인했으나, 이는 **BID OWL 전체 소스 실행이 아님**. 현재 Python 테스트 함수 245개 정의, 전수 실행 검증과 Windows 실제 성능 측정은 남아 있습니다.

---

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
