# BID OWL BASIC — offline engine (P1-01 + P1-02)

Development modules only. CSV import validation + company profile + evidence-gated 3-state eligibility implemented. SQLite/PDF/Excel/CLI/UI/Windows and real API are NOT IMPLEMENTED.

## CSV input contract
- Required: bid_no,title,agency,category,bid_deadline,budget,requirements; optional source_ref,data_as_of.
- UTF-8 or UTF-8-SIG; budget positive integer KRW; timestamps ISO 8601 with seconds and explicit timezone.
- requirements: JSON array of objects with id/kind/value/source. Source is a dictionary with both text and locator. Missing evidence is parsed but yields UNKNOWN on evaluation.
- Supported kinds: region_any, category_any, license_all (array of nonempty strings); staff_min, experience_total_min_krw (nonnegative integer).
- Unknown kinds are retained but their verdict is UNKNOWN. Missing/empty requirements -> UNKNOWN. Expired bid is an independent status, not CSV validation failure.
- Limit 10 MiB/10k rows/100 rules per bid. Any validation issue rejects the whole import batch. No remote data calls.

## Company profile (in-memory, persistence upcoming in P1-03)
Fields: profile_id (required), region, categories, licenses, staff_count, experience_total_krw. None = missing, empty categories/licenses tuple = explicitly no registered values. Nonnegative integer staff/experience; strict input field checks.

Example from repository root:

    cd backend
    python -m unittest discover -s tests -v

    python -c "from bidowl import load_csv, CompanyProfile, evaluate_bid; bids=load_csv('fixtures/sample_bids.csv'); company=CompanyProfile.from_mapping({'profile_id':'DEMO', 'region':'부산광역시', 'licenses':['소프트웨어사업자'], 'staff_count':3}); print([(b.bid_no,evaluate_bid(b,company).status) for b in bids])"

Sample fixture is SYNTHETIC, not actual public tender data. Conditions are interpreted as literal exact values, not geographic synonyms or government qualification law; final human approval is always required. UNKNOWN sources/rules/profile missing must be reviewed. Evidence text and location surfaced with reason codes.

## Test evidence
- Prior P1-01 run: 21 PASS/0 FAIL (separate previous run).
- P1-02 new suite: 27 PASS/0 FAIL on Linux CPython 3.13.5 against local copied schema interface, new GitHub code/test Git blob SHA exactly matched.
- **Combined 48-case execution not yet conducted** on a full GitHub checkout; no Windows or real public data tests. Tests assert synthetic rules, not actual legal validity.
