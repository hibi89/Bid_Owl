"""BASIC MVP acceptance checks use temp files only; no customer DB/network."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mvp_smoke import main, run_mvp_smoke


class BasicMvpAcceptanceTests(unittest.TestCase):
    def test_actual_customer_importer_to_report_xlsx(self):
        result = run_mvp_smoke()
        self.assertEqual(result["status"], "BASIC_MVP_SYNTHETIC_E2E_PASS")
        self.assertEqual(result["bids"], 2)
        self.assertEqual(result["reports"], 2)
        self.assertEqual(result["format"], "xlsx")
        self.assertEqual(result["assessments_saved"], 2)
        self.assertEqual(result["assessments_reused_on_repeat"], 2)
        self.assertTrue(result["backup_verified"])
        self.assertTrue(result["original_reports_preserved"])
        self.assertFalse(result["customer_data_used"])
        self.assertFalse(result["pdf_tested"])
        self.assertFalse(result["windows_gui_tested"])

    def test_cli_exposes_real_status_and_scoped_capabilities(self):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            exit_code = main([])
        self.assertEqual(exit_code, 0)
        obj = json.loads(output.getvalue())
        self.assertEqual(obj["status"], "BASIC_MVP_SYNTHETIC_E2E_PASS")
        self.assertFalse(obj["real_browser_tested"])
        self.assertFalse(obj["windows_gui_tested"])

    def test_require_pdf_preflight_fails_without_fake_pass(self):
        with patch("mvp_smoke.check_pdf_support",
                   side_effect=RuntimeError("SYNTHETIC_NO_FONT")) as check:
            with self.assertRaisesRegex(RuntimeError, "SYNTHETIC_NO_FONT"):
                run_mvp_smoke(require_pdf=True)
        check.assert_called_once_with()

    def test_failed_import_does_not_return_mvp_pass(self):
        with patch("mvp_smoke.apply_import",
                   side_effect=RuntimeError("SYNTHETIC_IMPORT_FAIL")):
            with contextlib.redirect_stdout(io.StringIO()) as output:
                exit_code = main([])
        self.assertEqual(exit_code, 2)
        obj = json.loads(output.getvalue())
        self.assertEqual(obj["status"], "BASIC_MVP_SYNTHETIC_E2E_FAILED")
        self.assertIn("SYNTHETIC_IMPORT_FAIL", obj["error"])

    def test_invalid_pdf_option_type_rejected_before_work(self):
        for value in ("yes", 1, None):
            with self.subTest(value=value), self.assertRaises(TypeError):
                run_mvp_smoke(require_pdf=value)


if __name__ == "__main__":
    unittest.main()
