"""
Behavior tests for LoggingCore.
"""

from __future__ import annotations

import json
import re
import tempfile
import unittest
from pathlib import Path

from logging_core import (
    ERROR,
    INFO,
    WARNING,
    LogEntry,
    create_logger,
    format_log_line,
)


class LoggingCoreBehaviorTests(unittest.TestCase):
    def test_logger_records_warning_and_error_as_structured_entries(self) -> None:
        logger = create_logger(name="TestTool")

        logger.info("Started", code="STARTED")
        logger.warning("Skipped", code="SKIPPED", context={"path": "C:/Temp"})
        logger.error("Failed", code="FAILED", context={"exit_code": 1})

        diagnostics = logger.get_diagnostics()
        errors = logger.get_errors()

        self.assertEqual(len(diagnostics), 2)
        self.assertEqual(diagnostics[0]["level"], WARNING)
        self.assertEqual(diagnostics[1]["level"], ERROR)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["code"], "FAILED")
        self.assertEqual(errors[0]["context"]["exit_code"], 1)

    def test_info_can_be_included_in_diagnostics_when_requested(self) -> None:
        logger = create_logger(name="TestTool")
        logger.info("Started", code="STARTED")

        self.assertEqual(logger.get_diagnostics(), [])

        diagnostics = logger.get_diagnostics(include_info=True)

        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0]["level"], INFO)

    def test_debug_is_filtered_by_default_min_level(self) -> None:
        logger = create_logger(name="TestTool")

        entry = logger.debug("Debug message", code="DEBUG_TEST")

        self.assertIsNone(entry)
        self.assertEqual(logger.entries, [])

    def test_min_level_debug_keeps_debug_entries(self) -> None:
        logger = create_logger(name="TestTool", min_level="debug")

        entry = logger.debug("Debug message", code="DEBUG_TEST")

        self.assertIsNotNone(entry)
        diagnostics = logger.get_diagnostics(include_debug=True)
        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0]["code"], "DEBUG_TEST")

    def test_log_file_is_written_as_utf8_text(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "logs" / "tool.log"
            logger = create_logger(name="TestTool", log_path=log_path)

            logger.info("Inicio correcto", code="STARTED", context={"área": "red"})

            content = log_path.read_text(encoding="utf-8")

        self.assertIn("STARTED", content)
        self.assertIn("Inicio correcto", content)
        self.assertIn('"área":"red"', content)

    def test_context_is_json_safe(self) -> None:
        logger = create_logger(name="TestTool")

        try:
            raise RuntimeError("Boom")
        except RuntimeError as error:
            logger.exception("Unexpected failure", error, code="UNEXPECTED")

        errors = logger.get_errors()

        self.assertEqual(errors[0]["context"]["exception"]["type"], "RuntimeError")
        self.assertEqual(errors[0]["context"]["exception"]["message"], "Boom")

    def test_format_log_line_includes_context_when_present(self) -> None:
        entry = LogEntry(
            level="warning",
            message="Skipped",
            code="SKIPPED",
            source="TestTool",
            timestamp_utc="2026-06-30T12:00:00Z",
            context={"path": "C:/Temp"},
        )

        line = format_log_line(entry)

        self.assertEqual(entry.timestamp_utc, "2026-06-30T12:00:00Z")
        self.assertTrue(entry.timestamp_utc.endswith("Z"))
        self.assertNotIn("+00:00", entry.timestamp_utc)
        self.assertRegex(line, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} [+-]\d{2}:\d{2} \| WARNING")
        self.assertIn("SKIPPED", line)
        self.assertIn('context={"path":"C:/Temp"}', line)

    def test_invalid_level_raises_value_error(self) -> None:
        logger = create_logger(name="TestTool")

        with self.assertRaises(ValueError):
            logger.log("critical", "Unsupported")

    def test_has_errors_returns_true_when_error_exists(self) -> None:
        logger = create_logger(name="TestTool")

        self.assertFalse(logger.has_errors())

        logger.error("Failed", code="FAILED")

        self.assertTrue(logger.has_errors())

    def test_clear_removes_retained_entries(self) -> None:
        logger = create_logger(name="TestTool")

        logger.warning("Skipped", code="SKIPPED")
        logger.clear()

        self.assertEqual(logger.entries, [])
        self.assertEqual(logger.get_diagnostics(), [])

    def test_keep_entries_false_writes_file_but_does_not_retain_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            log_path = Path(temp_dir) / "tool.log"
            logger = create_logger(
                name="TestTool",
                log_path=log_path,
                keep_entries=False,
            )

            logger.error("Failed", code="FAILED")

            content = log_path.read_text(encoding="utf-8")

        self.assertIn("FAILED", content)
        self.assertEqual(logger.entries, [])
        self.assertEqual(logger.get_errors(), [])

    def test_diagnostic_and_error_entries_are_json_serializable(self) -> None:
        logger = create_logger(name="TestTool")
        logger.warning("Skipped", code="SKIPPED", context={"items": {1, 2, 3}})
        logger.error("Failed", code="FAILED", context={"path": Path("C:/Temp")})

        payload = {
            "diagnostics": logger.get_diagnostics(),
            "errors": logger.get_errors(),
        }

        json.dumps(payload, ensure_ascii=False)


if __name__ == "__main__":
    unittest.main()
