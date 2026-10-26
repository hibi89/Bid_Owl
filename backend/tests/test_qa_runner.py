"""P2-10 outcome recording tests; actual full suite runs only via qa_runner main."""
from __future__ import annotations

import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from qa_runner import _synthetic_smoke, _unit_suite, run_qa


class QAReportingTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory(prefix="bidowl-qa-test-")
        self.addCleanup(folder.cleanup)
        self.directory = Path(folder.name)
        original_cwd = Path.cwd()
        self.addCleanup(os.chdir, original_cwd)
        self.good_suite = {"status": "PASS", "tests_run": 137, "failures": 0,
                           "errors": 0, "skipped": 0, "failed_tests": []}

    def test_actual_run_record_fields_and_exclusive_json(self):
        with patch("qa_runner._source_revision", return_value="a" * 40), \
             patch("qa_runner._unit_suite", return_value=self.good_suite), \
             patch("qa_runner._synthetic_smoke", return_value={"status": "PASS"}), \
             patch("qa_runner._syntax_check", return_value={"status": "PASS"}), \
             patch("qa_runner._benchmark", side_effect=AssertionError("no benchmark requested")), \
             contextlib.redirect_stdout(io.StringIO()):
            result = run_qa(output_dir=self.directory)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["git_commit"], "a" * 40)
        files = list(self.directory.glob("bidowl_qa_*.json"))
        self.assertEqual(len(files), 1)
        stored = json.loads(files[0].read_text(encoding="utf-8"))
        self.assertEqual(stored["unit_tests"]["tests_run"], 137)
        self.assertEqual(stored["synthetic_benchmark"]["status"], "SKIP")
        self.assertFalse(stored["customer_data_used"])
        self.assertFalse(stored["browser_tested"])
        self.assertNotIn("local_result_path", stored)

    def test_python_failure_still_collects_independent_smoke_and_benchmark(self):
        failed_suite = dict(self.good_suite, status="FAIL", failures=1)
        with patch("qa_runner._unit_suite", return_value=failed_suite), \
             patch("qa_runner._synthetic_smoke", return_value={"status": "PASS"}), \
             patch("qa_runner._benchmark", return_value={"status": "PASS"}), \
             patch("qa_runner._syntax_check", return_value={"status": "SKIP"}), \
             patch("qa_runner._source_revision", return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            result = run_qa(benchmark=True, output_dir=self.directory)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["synthetic_smoke"]["status"], "PASS")
        self.assertEqual(result["synthetic_benchmark"]["status"], "PASS")
        self.assertIsNone(result["git_commit"])

    def test_smoke_failure_does_not_skip_requested_benchmark(self):
        with patch("qa_runner._unit_suite", return_value=self.good_suite), \
             patch("qa_runner._synthetic_smoke", return_value={"status": "FAIL"}), \
             patch("qa_runner._benchmark", return_value={"status": "PASS"}), \
             patch("qa_runner._syntax_check", return_value={"status": "PASS"}), \
             patch("qa_runner._source_revision", return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            result = run_qa(benchmark=True, output_dir=self.directory)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["synthetic_smoke"]["status"], "FAIL")
        self.assertEqual(result["synthetic_benchmark"]["status"], "PASS")

    def test_both_real_importer_mvp_and_legacy_smoke_are_required(self):
        legacy = {"status": "SYNTHETIC_E2E_PASS"}
        basic = {"status": "BASIC_MVP_SYNTHETIC_E2E_PASS"}
        with patch("smoke_local.run_smoke", return_value=legacy) as old, \
             patch("mvp_smoke.run_mvp_smoke", return_value=basic) as new:
            result = _synthetic_smoke()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["synthetic_result"]["basic_mvp"], basic)
        self.assertEqual(result["synthetic_result"]["legacy_cli"], legacy)
        old.assert_called_once_with()
        new.assert_called_once_with()

    def test_mvp_failure_marks_qa_smoke_failed_even_if_legacy_passes(self):
        with patch("smoke_local.run_smoke",
                   return_value={"status": "SYNTHETIC_E2E_PASS"}), \
             patch("mvp_smoke.run_mvp_smoke",
                   side_effect=RuntimeError("MVP_IMPORT_BROKEN")):
            result = _synthetic_smoke()
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["synthetic_result"]["basic_mvp"]["status"], "FAILED")
        self.assertIn("MVP_IMPORT_BROKEN",
                      result["synthetic_result"]["basic_mvp"]["reason"])

    def test_zero_discovered_python_tests_is_a_qa_failure(self):
        with patch("qa_runner.unittest.TestLoader.discover",
                   return_value=unittest.TestSuite()), \
             contextlib.redirect_stderr(io.StringIO()):
            result = _unit_suite()
        self.assertEqual(result["tests_run"], 0)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failures"], 0)
        self.assertEqual(result["errors"], 0)

    def test_javascript_failure_is_not_misreported_as_pass(self):
        with patch("qa_runner._unit_suite", return_value=self.good_suite), \
             patch("qa_runner._synthetic_smoke", return_value={"status": "PASS"}), \
             patch("qa_runner._syntax_check", return_value={"status": "FAIL"}), \
             patch("qa_runner._source_revision", return_value=None), \
             contextlib.redirect_stdout(io.StringIO()):
            result = run_qa(output_dir=self.directory)
        self.assertEqual(result["status"], "FAIL")
        saved = list(self.directory.glob("bidowl_qa_*.json"))
        self.assertEqual(len(saved), 1)
        self.assertEqual(json.loads(saved[0].read_text(encoding="utf-8"))["status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
