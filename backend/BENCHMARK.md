# BID OWL P2-09 — isolated 10,000-bid local benchmark

## Purpose and evidence boundary

The real BASIC viewer searches the local SQLite database. Its current all-bid query reads and parses saved bid JSON before applying in-memory search, category and favorite filters. No measured 10,000-record latency has yet been obtained on the intended Windows 11 machine. This script provides a repeatable, synthetic workload to find actual bottlenecks before optimizing or claiming that a 10k-row dataset performs well.

**The GitHub commit contains the benchmark source, not execution results.** Do not advertise milliseconds, throughput, production readiness or an actual 10,000-bid PASS until an authorized full checkout executes it.

## Execution (from backend of exact private checkout)

Prerequisite: Python 3.11+; `benchmark_local.py` itself requires no ReportLab, font, procurement API, user database or browser.

    python benchmark_local.py --records 10000 --assessed 200

Short developer check (not equivalent to 10k measurement):

    python benchmark_local.py --records 31 --assessed 5

Windows integrated verification, if dependencies for the full unit tests are installed:

    powershell -ExecutionPolicy Bypass -File .\verify_local.ps1 -Benchmark

The benchmark always constructs a brand-new 1-to-10,000-record dataset under a Python `TemporaryDirectory`, inserts into a disposable SQLite v1 DB, assesses the first 200 records by default using a synthetic company, opens a separate read-only viewer connection, and deletes the DB and temp directory at normal completion. It NEVER points to a customer DB. Inputs outside the declared bounds are rejected before file creation.

## Output interpretation

JSON status `SYNTHETIC_BENCH_COMPLETE` means the benchmark script executed and its internal data/count/read-only assertions passed, **not** that speed or native browser quality passed.

`timings_ms` fields:
- `import_bids_ms`: 10k synthetic in-memory Bid objects imported in one transaction; excludes generating Python objects or decoding CSV
- `assess_subset_ms`: 200 saved rule evaluations, not 10k; measured separately
- `all_rows_page_1_ms`: list all-source query/parse/sort, return first 30
- `filter_category_search_ms`: filter category IT + text search, return first 30
- `single_bid_detail_ms`: exact key and source-evidence detail lookup
- `single_favorite_global_ms`: select one browser-favorite ID with global filter, still through existing query flow

`db_size_bytes` is synthetic SQLite size. The benchmark checks the selected detail and favorite ID, full count, category count, and rejected attempted DB mutation. It excludes browser DOM/CSS rendering, actual PDF/XLSX generation, true CSV parse time, filesystem antivirus, real user data/attributes, 24/7 operation and concurrent writers.

When timing data is measured, record source commit SHA, Python version, Windows/CPU/RAM/storage, record count, assessed count, each `timings_ms`, memory observations if collected, and repeated runs before setting any performance target. Local runtime matters; do not extrapolate one machine's numbers to all customers.

## Quality and privacy

`tests/test_benchmark_local.py` includes a small 31-record regression, an unassessed 1-record edge case and invalid input checks, not a heavy 10k CI test. An optional 10k benchmark is kept outside the always-on unittest suite for fast feedback. No API key or customer PDF/CSV is read or uploaded. Benchmarks are local, synchronous and contain only synthetic Korean bid text.
