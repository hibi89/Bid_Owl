# P2-05 Saved report re-export and local synthetic verification

Use only on a local copy of BID OWL with an existing schema-v1 SQLite database.

From backend, re-export a prior saved assessment without re-importing/re-evaluating or writing to the source DB:

    python report_existing.py --db ./demo.sqlite3 --assessment-id 1 --output ./replayed_reports --format both

This opens SQLite read-only; it uses the original saved profile/bid versions and evidence. Historical PASS/FAIL is not a new/current legal eligibility result. Existing report output paths are not overwritten. For machines without ReportLab/Korean TTF use --format xlsx.

The detail drawer displays the matching assessment ID and local command. The browser cannot mutate DB data.

For a real end-to-end synthetic check (all files go into a new disposable temporary directory):

    python smoke_local.py

The runner imports fixtures/sample_bids.csv and fixtures/sample_profile.json, tests XLSX and localhost HTTP list/detail/favorites/profile, re-exports a saved report, applies a versioned profile revision with a backup, re-assesses, and verifies the old assessment and backup. It does not use customer data, official APIs, external services or PDFs.

Full Python regression:

    python -m unittest discover -s tests -v

Current GitHub test inventory should include 116 prior methods plus 6 report re-export and 1 synthetic smoke = 123. **These 123 have not yet been run in an authenticated full checkout**. The new source/tests are committed but runtime and Windows/native browser and PDF validation remain pending.
