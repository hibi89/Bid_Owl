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

    def test_opt_in_small_synthetic_recovery_benchmark(self):
        result = run_benchmark(records=31, assessed=5, measure_recovery=True)
        self.assertEqual(result["status"], "SYNTHETIC_BENCH_COMPLETE")
        self.assertTrue(result["recovery_verified"])
        self.assertEqual(len(result["recovery_evidence_sha256"]), 64)
        for field in (
            "sqlite_backup_ms", "recovery_validate_and_hash_ms",
            "recovery_copy_verify_ms",
        ):
            self.assertIn(field, result["timings_ms"])
            self.assertGreaterEqual(result["timings_ms"][field], 0)

    def test_recovery_measurement_rejects_non_boolean_flag(self):
        with self.assertRaisesRegex(ValueError, "measure_recovery"):
            run_benchmark(records=1, assessed=0, measure_recovery="yes")

    def test_comparison_matches_legacy_full_scan_on_synthetic_rows(self):
        result = run_benchmark(
            records=41, assessed=7, measure_viewer_baseline=True,
        )
        self.assertEqual(result["status"], "SYNTHETIC_BENCH_COMPLETE")
        self.assertTrue(result["viewer_baseline_compared"])
        self.assertIn("legacy_full_scan_page_1_ms", result["timings_ms"])
        self.assertIn("all_rows_page_1_ms", result["timings_ms"])
        self.assertGreaterEqual(result["timings_ms"]["legacy_full_scan_page_1_ms"], 0)

    def test_comparison_mode_requires_real_bool(self):
        with self.assertRaisesRegex(ValueError, "measure_viewer_baseline"):
            run_benchmark(records=1, assessed=0, measure_viewer_baseline="true")

    def test_invalid_limits_rejected_before_file_creation(self):
        for records, assessed in ((0,0), (10001,0), (3,-1),
                                  (3,4), (True,0), (3,False)):
            with self.subTest(records=records, assessed=assessed):
                with self.assertRaises(ValueError):
                    run_benchmark(records=records, assessed=assessed)


if __name__ == "__main__":
    unittest.main()
