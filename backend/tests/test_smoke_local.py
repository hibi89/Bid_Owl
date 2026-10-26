"""Synthetic end-to-end check using only temporary local files and loopback HTTP."""
import unittest

from smoke_local import run_smoke


class SyntheticEndToEndTests(unittest.TestCase):
    def test_csv_sqlite_viewer_favorites_reports_profile_reassess_and_backup(self):
        result = run_smoke()
        self.assertEqual(result["status"], "SYNTHETIC_E2E_PASS")
        self.assertTrue(result["historical_assessment_preserved"])
        self.assertTrue(result["backup_verified"])
        self.assertEqual(result["new_assessments"], 2)
        self.assertFalse(result["browser_tested"])
        self.assertFalse(result["windows_tested"])


if __name__ == "__main__":
    unittest.main()
