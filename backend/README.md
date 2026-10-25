# BID OWL BASIC engine — P1-01 CSV input

Python 3.13.5 / standard library. This branch provides CSV import validation, not eligibility/SQLite/PDF/Excel/UI/Windows/API.

## Contract
Required header: bid_no,title,agency,category,bid_deadline,budget,requirements
Optional header: source_ref,data_as_of

- UTF-8 and UTF-8-SIG input.
- Budget: positive integer KRW, max 20 digits, no commas.
- Deadline/data_as_of: ISO8601 with seconds AND timezone (e.g. 2027-11-01T17:00:00+09:00).
- requirements: JSON array with id, kind, value and optional source: {text,locator}.
- Kind: region_any/category_any/license_all require nonempty arrays of strings; staff_min/experience_total_min_krw require nonnegative integers. Unknown kinds and missing evidence are retained for UNKNOWN evaluation in P1-02.
- Empty requirements are not a PASS. Expired bid is a separate state, not a schema error.
- Limit: 10 MiB CSV / 10,000 rows / 100 requirements per bid.
- Any validation issue rejects the ENTIRE batch. No network calls.

## Run tests and sample
From repository root:

    cd backend
    python -m unittest discover -s tests -v
    python -c "from bidowl import load_csv; print(len(load_csv('fixtures/sample_bids.csv')))"

Sample CSV includes two synthetic bids only; never treat as real procurement data.

2026-10-26: Local Python 3.13.5 Linux: 21 PASS, 0 FAIL. GitHub Python code/tests blob hashes matched local tested files. GitHub fixture saved UTF-8 (local generated fixture UTF-8-SIG), direct remote fixture runtime verification not performed. Windows and real input testing pending.
