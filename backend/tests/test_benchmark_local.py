"""P2-09 synthetic benchmark regression; runs small, not 10k in every unittest invocation."""
from __future__ import annotations

import unittest

from benchmark_local import run_benchmark


class BenchmarkLocalTests(unittest.TestCase):
    def test_small_real_sqlite_workload_counts_and_readonly(self):
        result = run_benchmark(records=31, assessed=5)
        self.assertEqual(result["status"], "SYNTHETIC_BENCH_COMPLETE")
        self.assertEqual(result["records"], 31)
        self.assertEqual(result["assessed"], 5)
        self.assertGreater(result["db_size_bytes"], 0)
        self.assertFalse(result["database_mutation_by_viewer"])
        self.assertEqual(set(result["timings_ms"]), {
            "import_bids_ms", "assess_subset_ms", "all_rows_page_1_ms",
            "filter_category_search_ms", "single_bid_detail_ms",
            "single_favorite_global_ms",
        })
        for elapsed in result["timings_ms"].values():
            self.assertGreaterEqual(elapsed, 0)

    def test_single_record_without_assessment(self):
        result = run_benchmark(records=1, assessed=0)
        self.assertEqual(result["records"], 1)
        self.assertEqual(result["assessed"], 0)
        self.assertFalse(result["database_mutation_by_viewer"])

    def test_invalid_limits_rejected_before_file_creation(self):
        for records, assessed in ((0,0), (10001,0), (3,-1),
                                  (3,4), (True,0), (3,False)):
            with self.subTest(records=records, assessed=assessed):
                with self.assertRaises(ValueError):
                    run_benchmark(records=records, assessed=assessed)


if __name__ == "__main__":
    unittest.main()
