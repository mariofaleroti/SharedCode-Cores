from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

from process_runner_core import (
    PROCESS_STATUS_EXECUTION_ERROR,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_OK,
    PROCESS_STATUS_TIMEOUT,
    ProcessRunner,
    normalize_command,
    run_process,
)


class ProcessRunnerCoreBehaviorTests(unittest.TestCase):
    def test_normalize_command_accepts_single_executable_string(self) -> None:
        self.assertEqual(normalize_command("python"), ("python",))

    def test_normalize_command_accepts_argument_sequence(self) -> None:
        self.assertEqual(normalize_command(["python", "--version"]), ("python", "--version"))

    def test_normalize_command_rejects_empty_command(self) -> None:
        with self.assertRaises(ValueError):
            normalize_command([])

    def test_normalize_command_rejects_blank_argument(self) -> None:
        with self.assertRaises(ValueError):
            normalize_command(["python", ""])

    def test_run_process_success_captures_output(self) -> None:
        result = run_process(
            [sys.executable, "-c", "print('hello')"],
            timeout_seconds=10,
            trim_output=True,
        )

        self.assertEqual(result.status, PROCESS_STATUS_OK)
        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.succeeded)
        self.assertEqual(result.stdout, "hello")
        self.assertEqual(result.stderr, "")

    def test_run_process_failure_captures_exit_code_and_stderr(self) -> None:
        result = run_process(
            [
                sys.executable,
                "-c",
                "import sys; print('bad', file=sys.stderr); raise SystemExit(7)",
            ],
            timeout_seconds=10,
            trim_output=True,
        )

        self.assertEqual(result.status, PROCESS_STATUS_FAILED)
        self.assertEqual(result.exit_code, 7)
        self.assertTrue(result.failed)
        self.assertEqual(result.stderr, "bad")

    def test_run_process_timeout_returns_structured_result(self) -> None:
        result = run_process(
            [sys.executable, "-c", "import time; time.sleep(2)"],
            timeout_seconds=0.1,
        )

        self.assertEqual(result.status, PROCESS_STATUS_TIMEOUT)
        self.assertIsNone(result.exit_code)
        self.assertTrue(result.timed_out)
        self.assertTrue(result.failed)
        self.assertEqual(result.exception_type, "TimeoutExpired")

    def test_run_process_missing_executable_returns_execution_error(self) -> None:
        result = run_process(
            ["definitely_missing_executable_for_process_runner_core"],
            timeout_seconds=1,
        )

        self.assertEqual(result.status, PROCESS_STATUS_EXECUTION_ERROR)
        self.assertIsNone(result.exit_code)
        self.assertTrue(result.failed)
        self.assertIsNotNone(result.exception_type)

    def test_run_process_uses_cwd(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = run_process(
                [sys.executable, "-c", "from pathlib import Path; print(Path.cwd())"],
                cwd=temp_dir,
                timeout_seconds=10,
                trim_output=True,
            )

            self.assertEqual(result.status, PROCESS_STATUS_OK)
            self.assertEqual(Path(result.stdout), Path(temp_dir))

    def test_run_process_merges_environment_overrides(self) -> None:
        result = run_process(
            [sys.executable, "-c", "import os; print(os.environ.get('PRC_TEST_VALUE'))"],
            env={"PRC_TEST_VALUE": "expected"},
            timeout_seconds=10,
            trim_output=True,
        )

        self.assertEqual(result.status, PROCESS_STATUS_OK)
        self.assertEqual(result.stdout, "expected")

    def test_to_dict_is_json_safe(self) -> None:
        result = run_process(
            [sys.executable, "-c", "print('json-safe')"],
            timeout_seconds=10,
            trim_output=True,
        )

        payload = result.to_dict()
        self.assertEqual(payload["status"], PROCESS_STATUS_OK)
        self.assertEqual(payload["stdout"], "json-safe")
        self.assertIn("command", payload)
        self.assertTrue(payload["started_at"].endswith("Z"))
        self.assertTrue(payload["ended_at"].endswith("Z"))
        self.assertNotIn("+00:00", payload["started_at"])

    def test_to_diagnostic_for_success(self) -> None:
        result = run_process(
            [sys.executable, "-c", "print('ok')"],
            timeout_seconds=10,
        )

        diagnostic = result.to_diagnostic()
        self.assertEqual(diagnostic["level"], "info")
        self.assertEqual(diagnostic["code"], "PROCESS_COMPLETED")
        self.assertIsNone(result.to_error())

    def test_to_error_for_failure(self) -> None:
        result = run_process(
            [sys.executable, "-c", "raise SystemExit(3)"],
            timeout_seconds=10,
        )

        error = result.to_error()
        self.assertIsNotNone(error)
        self.assertEqual(error["code"], "PROCESS_FAILED")
        self.assertEqual(error["context"]["exit_code"], 3)

    def test_process_runner_class_can_be_reused(self) -> None:
        runner = ProcessRunner()
        result = runner.run([sys.executable, "-c", "print('runner')"])
        self.assertEqual(result.status, PROCESS_STATUS_OK)

    @unittest.skipIf(os.name == "nt", "POSIX shell syntax test only")
    def test_shell_true_is_explicitly_supported(self) -> None:
        result = run_process(
            "echo shell-ok",
            shell=True,
            timeout_seconds=10,
            trim_output=True,
        )
        self.assertEqual(result.stdout, "shell-ok")


if __name__ == "__main__":
    unittest.main()
