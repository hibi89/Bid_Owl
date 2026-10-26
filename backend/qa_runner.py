"""BID OWL full-checkout QA runner. Local synthetic tests only; never uploads results.

Run inside an authorized checkout:
    python qa_runner.py
    python qa_runner.py --benchmark
Generates an exclusive, timestamped local JSON outcome under qa_results/.
A JSON report is evidence of an actual run; source declarations alone are not.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import time
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _source_revision() -> str | None:
    if not shutil.which("git"):
        return None
    try:
        run = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD"],
            cwd=ROOT, capture_output=True, text=True, timeout=5,
            check=False,
        )
        sha = run.stdout.strip()
        if run.returncode == 0 and len(sha) == 40 and all(
            ch in "0123456789abcdef" for ch in sha
        ):
            return sha
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def _unit_suite() -> dict:
    loader = unittest.TestLoader()
    suite = loader.discover(start_dir=str(ROOT / "tests"), pattern="test_*.py")
    print("BID OWL: executing actual Python unittests", file=sys.stderr, flush=True)
    started = time.perf_counter()
    runner = unittest.TextTestRunner(stream=sys.stderr, verbosity=1)
    result = runner.run(suite)
    return {
        "status": "PASS" if result.wasSuccessful() and result.testsRun > 0 else "FAIL",
        "tests_run": result.testsRun,
        "failures": len(result.failures),
        "errors": len(result.errors),
        "skipped": len(result.skipped),
        "expected_failures": len(result.expectedFailures),
        "unexpected_successes": len(result.unexpectedSuccesses),
        "failed_tests": [str(test) for test, _ in result.failures + result.errors],
        # Keep the root exception in local JSON so sharing the entire
        # PowerShell transcript is not necessary. No raw environment dump.
        "failed_test_errors": [
            {
                "test": str(test),
                "error_summary": next(
                    (line.strip() for line in reversed(trace.splitlines()) if line.strip()),
                    "Unknown unittest error",
                )[:600],
            }
            for test, trace in result.failures + result.errors
        ],
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
    }


def _synthetic_smoke() -> dict:
    """Gate both legacy synthetic CLI and genuine BASIC customer-importer path."""
    from smoke_local import run_smoke
    from mvp_smoke import run_mvp_smoke

    started = time.perf_counter()
    outcomes = {}
    for label, check in (("legacy_cli", run_smoke), ("basic_mvp", run_mvp_smoke)):
        try:
            outcomes[label] = check()
        except Exception as exc:
            outcomes[label] = {
                "status": "FAILED", "error_type": type(exc).__name__,
                "reason": str(exc)[:500],
            }
    status = ("PASS" if
              outcomes["legacy_cli"].get("status") == "SYNTHETIC_E2E_PASS"
              and outcomes["basic_mvp"].get("status") == "BASIC_MVP_SYNTHETIC_E2E_PASS"
              else "FAIL")
    return {
        "status": status,
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        "synthetic_result": outcomes,
    }


def _syntax_check() -> dict:
    node = shutil.which("node")
    if not node:
        return {"status": "SKIP", "reason": "Node.js is not installed"}
    try:
        result = subprocess.run(
            [node, "--check", str(ROOT / "ui" / "ui.js")],
            capture_output=True, text=True, timeout=20, check=False,
        )
        return {
            "status": "PASS" if result.returncode == 0 else "FAIL",
            "exit_code": result.returncode,
            "reason": result.stderr[:500] if result.returncode else "",
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "FAIL", "error_type": type(exc).__name__}


def _benchmark() -> dict:
    from benchmark_local import run_benchmark

    started = time.perf_counter()
    try:
        result = run_benchmark(records=10000, assessed=200)
        return {
            "status": "PASS" if result.get("status") == "SYNTHETIC_BENCH_COMPLETE" else "FAIL",
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "synthetic_result": result,
        }
    except Exception as exc:
        return {
            "status": "FAIL",
            "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
            "error_type": type(exc).__name__,
            "reason": str(exc)[:500],
        }


def run_qa(*, benchmark: bool = False, output_dir: str | Path | None = None) -> dict:
    """Run the real suite, then synthetic smoke, optional benchmark and JS syntax.

    No customer DB/path arguments. All imported smoke and benchmark code creates
    TemporaryDirectory data only. A failing stage does not masquerade as PASS.
    """
    os.chdir(ROOT)
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    started_at = datetime.now(timezone.utc)
    outcome = {
        "status": "INCOMPLETE",
        "started_at_utc": started_at.isoformat(),
        "git_commit": _source_revision(),
        "runtime": {
            "python": platform.python_version(),
            "os": platform.system(),
            "machine": platform.machine(),
        },
        "unit_tests": None,
        "synthetic_smoke": None,
        "javascript_syntax": None,
        "synthetic_benchmark": None,
        "browser_tested": False,
        "native_excel_pdf_tested": False,
        "customer_data_used": False,
    }
    try:
        outcome["unit_tests"] = _unit_suite()
        # These stages use separate disposable synthetic databases.
        # Run independently even when another stage fails: one run should
        # collect all useful diagnostics, not force repeated user reruns.
        outcome["synthetic_smoke"] = _synthetic_smoke()
        outcome["javascript_syntax"] = _syntax_check()
        if benchmark:
            outcome["synthetic_benchmark"] = _benchmark()
        else:
            outcome["synthetic_benchmark"] = {
                "status": "SKIP", "reason": "Use --benchmark to run 10k synthetic records"
            }
        stages = ("unit_tests", "synthetic_smoke")
        if benchmark:
            stages += ("synthetic_benchmark",)
        outcome["status"] = (
            "PASS" if all(outcome[s]["status"] == "PASS" for s in stages)
            and outcome["javascript_syntax"]["status"] != "FAIL" else "FAIL"
        )
    except BaseException as exc:
        outcome["status"] = "FAIL"
        outcome["runner_error"] = type(exc).__name__
        # A KeyboardInterrupt is still written to disk as a failed/incomplete run.
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
    finally:
        outcome["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
        folder = (Path(output_dir).expanduser().resolve() if output_dir is not None
                  else ROOT / "qa_results")
        folder.mkdir(parents=True, exist_ok=True)
        name = "bidowl_qa_" + started_at.strftime("%Y%m%dT%H%M%SZ") + "_" + uuid.uuid4().hex[:8] + ".json"
        path = folder / name
        with path.open("x", encoding="utf-8") as stream:
            json.dump(outcome, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.write("\n")
        outcome["local_result_path"] = str(path)
        print(json.dumps({
            "status": outcome["status"],
            "unit_tests": outcome["unit_tests"],
            "synthetic_smoke": outcome["synthetic_smoke"]["status"] if outcome["synthetic_smoke"] else "NOT_RUN",
            "synthetic_benchmark": outcome["synthetic_benchmark"]["status"] if outcome["synthetic_benchmark"] else "NOT_RUN",
            "javascript_syntax": outcome["javascript_syntax"]["status"] if outcome["javascript_syntax"] else "NOT_RUN",
            "local_result_path": str(path),
        }, ensure_ascii=False, indent=2), flush=True)
    return outcome


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="BID OWL actual source QA and synthetic benchmark")
    parser.add_argument("--benchmark", action="store_true", help="Run additional 10k-record synthetic measurement")
    parser.add_argument("--output-dir", help="Directory to save new local QA result JSON")
    args = parser.parse_args(argv)
    return 0 if run_qa(benchmark=args.benchmark, output_dir=args.output_dir)["status"] == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
