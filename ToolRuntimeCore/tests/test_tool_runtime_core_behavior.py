from __future__ import annotations

import re
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from tool_runtime_core import (
    ToolRuntimeContext,
    create_run_id,
    create_runtime_context,
    normalize_runtime_name,
)


class ToolRuntimeCoreBehaviorTests(unittest.TestCase):
    def test_create_runtime_context_creates_standard_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(
                tool_name="ShadowBackup",
                tool_version="0.1.0",
                base_dir=temp_dir,
            )

            self.assertTrue(context.output_dir.is_dir())
            self.assertTrue(context.logs_dir.is_dir())
            self.assertTrue(context.temp_dir.is_dir())
            self.assertTrue(context.runtime_dir.is_dir())

    def test_create_runtime_context_can_skip_directory_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(
                tool_name="ShadowBackup",
                base_dir=temp_dir,
                create_directories=False,
            )

            self.assertFalse(context.output_dir.exists())
            self.assertFalse(context.logs_dir.exists())
            self.assertFalse(context.temp_dir.exists())
            self.assertFalse(context.runtime_dir.exists())

    def test_default_directories_are_resolved_from_base_dir(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir).resolve()
            context = create_runtime_context(tool_name="Tool", base_dir=base_dir)

            self.assertEqual(context.base_dir, base_dir)
            self.assertEqual(context.output_dir, base_dir / "output")
            self.assertEqual(context.logs_dir, base_dir / "output" / "logs")
            self.assertEqual(context.temp_dir, base_dir / "output" / "temp")
            self.assertEqual(context.runtime_dir, base_dir / "output" / "runtime")

    def test_custom_relative_directories_are_resolved_correctly(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            base_dir = Path(temp_dir).resolve()
            context = create_runtime_context(
                tool_name="Tool",
                base_dir=base_dir,
                output_dir="custom_output",
                logs_dir="custom_logs",
                temp_dir="custom_temp",
                runtime_dir="custom_runtime",
            )

            self.assertEqual(context.output_dir, base_dir / "custom_output")
            self.assertEqual(context.logs_dir, context.output_dir / "custom_logs")
            self.assertEqual(context.temp_dir, context.output_dir / "custom_temp")
            self.assertEqual(context.runtime_dir, context.output_dir / "custom_runtime")

    def test_custom_absolute_output_directory_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as base_temp_dir, tempfile.TemporaryDirectory() as output_temp_dir:
            output_dir = Path(output_temp_dir).resolve()
            context = create_runtime_context(
                tool_name="Tool",
                base_dir=base_temp_dir,
                output_dir=output_dir,
            )

            self.assertEqual(context.output_dir, output_dir)
            self.assertEqual(context.logs_dir, output_dir / "logs")

    def test_tool_name_is_normalized(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(
                tool_name="Smart Filter / Archivos",
                base_dir=temp_dir,
            )

            self.assertEqual(context.tool_name, "Smart_Filter_Archivos")

    def test_normalize_runtime_name_uses_fallback_for_empty_result(self) -> None:
        self.assertEqual(normalize_runtime_name(" /// ", fallback="fallback"), "fallback")

    def test_empty_tool_name_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(ValueError):
                create_runtime_context(tool_name="   ", base_dir=temp_dir)

    def test_create_run_id_contains_timestamp_and_suffix(self) -> None:
        started_at = datetime(2026, 6, 30, 15, 4, 5, tzinfo=timezone.utc)
        run_id = create_run_id(started_at)

        self.assertRegex(run_id, r"^20260630_150405_[a-f0-9]{8}$")

    def test_naive_started_at_is_treated_as_utc(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            started_at = datetime(2026, 6, 30, 15, 4, 5)
            context = create_runtime_context(
                tool_name="Tool",
                base_dir=temp_dir,
                started_at_utc=started_at,
            )

            self.assertIsNotNone(context.started_at_utc.tzinfo)
            self.assertEqual(context.started_at_utc.tzinfo, timezone.utc)

    def test_context_path_helpers_return_expected_locations(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(tool_name="Tool", base_dir=temp_dir)

            self.assertEqual(context.get_log_path(), context.logs_dir / "Tool.log")
            self.assertEqual(context.get_log_path("custom.log"), context.logs_dir / "custom.log")
            self.assertEqual(context.get_output_path("result.json"), context.output_dir / "result.json")
            self.assertEqual(context.get_temp_path("scratch.tmp"), context.temp_dir / "scratch.tmp")
            self.assertEqual(context.get_runtime_path("state.json"), context.runtime_dir / "state.json")

    def test_context_to_dict_is_json_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(tool_name="Tool", base_dir=temp_dir, run_id="run-1")
            data = context.to_dict()

            self.assertEqual(data["tool_name"], "Tool")
            self.assertEqual(data["run_id"], "run-1")
            self.assertIsInstance(data["base_dir"], str)
            self.assertIsInstance(data["started_at_utc"], str)

    def test_context_to_meta_contains_runtime_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(tool_name="Tool", base_dir=temp_dir, run_id="run-1")
            meta = context.to_meta(module_name="Scanner", file_type="result")

            self.assertEqual(meta["tool_name"], "Tool")
            self.assertEqual(meta["tool_version"], "0.1.0")
            self.assertEqual(meta["run_id"], "run-1")
            self.assertEqual(meta["module_name"], "Scanner")
            self.assertEqual(meta["file_type"], "result")

    def test_context_type_is_exported(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(tool_name="Tool", base_dir=temp_dir)
            self.assertIsInstance(context, ToolRuntimeContext)

    def test_run_ids_are_unique(self) -> None:
        first = create_run_id(datetime(2026, 6, 30, 15, 4, 5, tzinfo=timezone.utc))
        second = create_run_id(datetime(2026, 6, 30, 15, 4, 5, tzinfo=timezone.utc))

        self.assertNotEqual(first, second)

    def test_started_at_iso_uses_shared_utc_format(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(tool_name="Tool", base_dir=temp_dir)
            self.assertTrue(context.started_at_iso.endswith("Z"))
            self.assertNotIn("+00:00", context.started_at_iso)

    def test_meta_includes_utc_and_local_timestamps(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            context = create_runtime_context(tool_name="Tool", base_dir=temp_dir)
            meta = context.to_meta()

            self.assertTrue(meta["started_at_utc"].endswith("Z"))
            self.assertIn("started_at_local", meta)
            self.assertIn("local_utc_offset", meta)


if __name__ == "__main__":
    unittest.main()
