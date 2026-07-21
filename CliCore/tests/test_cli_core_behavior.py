from __future__ import annotations

import argparse
import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from cli_core import (
    EXIT_ERROR,
    EXIT_OK,
    EXIT_USAGE_ERROR,
    CliOptions,
    create_base_parser,
    exit_code_from_success,
    exit_code_from_validation,
    parse_cli_options,
    parse_known_cli_options,
)


class CliCoreBehaviorTests(unittest.TestCase):
    def test_parse_empty_args_returns_defaults(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options = parse_cli_options(parser, [])

        self.assertIsNone(options.config_path)
        self.assertIsNone(options.output_dir)
        self.assertFalse(options.quiet)
        self.assertEqual(options.verbose, 0)
        self.assertEqual(options.log_level, "info")

    def test_parse_common_paths_as_path_objects(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options = parse_cli_options(
            parser,
            [
                "--config",
                "config/tool.json",
                "--output-dir",
                "output",
                "--logs-dir",
                "output/logs",
                "--json-output",
                "output/result.json",
            ],
        )

        self.assertEqual(options.config_path, Path("config/tool.json"))
        self.assertEqual(options.output_dir, Path("output"))
        self.assertEqual(options.logs_dir, Path("output/logs"))
        self.assertEqual(options.json_output, Path("output/result.json"))

    def test_quiet_reduces_human_output(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options = parse_cli_options(parser, ["--quiet"])

        self.assertTrue(options.quiet)
        self.assertFalse(options.should_print_human_output)
        self.assertEqual(options.log_level, "warning")

    def test_verbose_increases_verbosity(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options = parse_cli_options(parser, ["-vv"])

        self.assertEqual(options.verbose, 2)
        self.assertEqual(options.log_level, "debug")

    def test_debug_sets_debug_log_level(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options = parse_cli_options(parser, ["--debug"])

        self.assertTrue(options.debug)
        self.assertEqual(options.log_level, "debug")

    def test_no_pause_and_validate_config_are_supported(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options = parse_cli_options(parser, ["--no-pause", "--validate-config"])

        self.assertTrue(options.no_pause)
        self.assertTrue(options.validate_config)

    def test_quiet_cannot_be_combined_with_verbose(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        with self.assertRaises(SystemExit) as context:
            parse_cli_options(parser, ["--quiet", "--verbose"])

        self.assertEqual(context.exception.code, EXIT_USAGE_ERROR)

    def test_quiet_cannot_be_combined_with_debug(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        with self.assertRaises(SystemExit) as context:
            parse_cli_options(parser, ["--quiet", "--debug"])

        self.assertEqual(context.exception.code, EXIT_USAGE_ERROR)

    def test_parser_can_include_tool_specific_arguments(self) -> None:
        parser = create_base_parser(tool_name="Tool")
        parser.add_argument("--scan-root")

        namespace = parser.parse_args(["--config", "config.json", "--scan-root", "C:/Projects"])
        options = CliOptions.from_namespace(namespace)

        self.assertEqual(options.config_path, Path("config.json"))
        self.assertEqual(namespace.scan_root, "C:/Projects")

    def test_parse_known_cli_options_preserves_unknown_args(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        options, remaining = parse_known_cli_options(
            parser,
            ["--config", "config.json", "--custom", "value"],
        )

        self.assertEqual(options.config_path, Path("config.json"))
        self.assertEqual(remaining, ["--custom", "value"])

    def test_version_option_prints_version_and_exits_ok(self) -> None:
        parser = create_base_parser(tool_name="Tool", version="1.2.3")

        output = io.StringIO()
        with redirect_stdout(output):
            with self.assertRaises(SystemExit) as context:
                parser.parse_args(["--version"])

        self.assertEqual(context.exception.code, EXIT_OK)
        self.assertIn("Tool 1.2.3", output.getvalue())

    def test_invalid_argument_exits_with_usage_error(self) -> None:
        parser = create_base_parser(tool_name="Tool")

        with self.assertRaises(SystemExit) as context:
            parser.parse_args(["--unknown"])

        self.assertEqual(context.exception.code, EXIT_USAGE_ERROR)

    def test_cli_options_to_dict_is_json_safe(self) -> None:
        parser = create_base_parser(tool_name="Tool")
        options = parse_cli_options(parser, ["--config", "config.json", "--debug"])

        data = options.to_dict()

        self.assertEqual(data["config_path"], "config.json")
        self.assertTrue(data["debug"])
        self.assertEqual(data["log_level"], "debug")

    def test_exit_code_from_success(self) -> None:
        self.assertEqual(exit_code_from_success(True), EXIT_OK)
        self.assertEqual(exit_code_from_success(False), EXIT_ERROR)

    def test_exit_code_from_validation(self) -> None:
        self.assertEqual(exit_code_from_validation(is_valid=True), EXIT_OK)
        self.assertEqual(exit_code_from_validation(is_valid=False), EXIT_ERROR)
        self.assertEqual(
            exit_code_from_validation(
                is_valid=True,
                has_warnings=True,
                fail_on_warnings=True,
            ),
            EXIT_ERROR,
        )


if __name__ == "__main__":
    unittest.main()
