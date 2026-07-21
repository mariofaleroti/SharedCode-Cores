from __future__ import annotations

import unittest

from app_core import (
    APP_STATUS_FAILED,
    APP_STATUS_INTERRUPTED,
    APP_STATUS_OK,
    EXIT_CODE_GENERAL_ERROR,
    EXIT_CODE_INTERRUPTED,
    EXIT_CODE_OK,
    EXIT_CODE_STARTUP_ERROR,
    AppRunResult,
    create_app_context,
    execute_app_context,
    run_tool_app,
    run_tool_app_with_factories,
)


class FakeLogger:
    def __init__(self):
        self.entries = []

    def info(self, message, **kwargs):
        self.entries.append(("info", message, kwargs))

    def error(self, message, **kwargs):
        self.entries.append(("error", message, kwargs))


class MinimalResult:
    def __init__(self, exit_code):
        self.exit_code = exit_code


class TestAppCoreBehavior(unittest.TestCase):
    def test_create_app_context_sets_basic_fields(self):
        context = create_app_context(tool_name="ToolA", tool_version="1.2.3")

        self.assertEqual(context.tool_name, "ToolA")
        self.assertEqual(context.tool_version, "1.2.3")

    def test_context_state_helpers(self):
        context = create_app_context(tool_name="ToolA")
        context.set_state("key", "value")

        self.assertEqual(context.get_state("key"), "value")
        self.assertEqual(context.get_state("missing", "fallback"), "fallback")

    def test_run_tool_app_returns_zero_for_none_handler_result(self):
        exit_code = run_tool_app(
            tool_name="ToolA",
            run_handler=lambda context: None,
        )

        self.assertEqual(exit_code, EXIT_CODE_OK)

    def test_run_tool_app_returns_handler_exit_code(self):
        exit_code = run_tool_app(
            tool_name="ToolA",
            run_handler=lambda context: 7,
        )

        self.assertEqual(exit_code, 7)

    def test_run_tool_app_normalizes_bool_result(self):
        self.assertEqual(
            run_tool_app(tool_name="ToolA", run_handler=lambda context: True),
            EXIT_CODE_OK,
        )
        self.assertEqual(
            run_tool_app(tool_name="ToolA", run_handler=lambda context: False),
            EXIT_CODE_GENERAL_ERROR,
        )

    def test_run_tool_app_uses_exit_code_attribute(self):
        exit_code = run_tool_app(
            tool_name="ToolA",
            run_handler=lambda context: MinimalResult(5),
        )

        self.assertEqual(exit_code, 5)

    def test_run_tool_app_can_return_structured_result(self):
        result = run_tool_app(
            tool_name="ToolA",
            run_handler=lambda context: 0,
            return_result=True,
        )

        self.assertIsInstance(result, AppRunResult)
        self.assertEqual(result.status, APP_STATUS_OK)
        self.assertEqual(result.exit_code, EXIT_CODE_OK)
        self.assertTrue(result.succeeded)
        self.assertGreaterEqual(result.duration_ms, 0)

    def test_execute_app_context_logs_start_and_success(self):
        logger = FakeLogger()
        context = create_app_context(tool_name="ToolA", logger=logger)

        result = execute_app_context(
            context=context,
            run_handler=lambda app_context: 0,
        )

        self.assertTrue(result.succeeded)
        self.assertEqual(logger.entries[0][0], "info")
        self.assertEqual(logger.entries[-1][0], "info")

    def test_unhandled_exception_is_captured(self):
        def broken_handler(context):
            raise ValueError("boom")

        result = run_tool_app(
            tool_name="ToolA",
            run_handler=broken_handler,
            return_result=True,
        )

        self.assertEqual(result.status, APP_STATUS_FAILED)
        self.assertEqual(result.exit_code, EXIT_CODE_GENERAL_ERROR)
        self.assertEqual(result.error["type"], "ValueError")
        self.assertEqual(result.error["message"], "boom")

    def test_unhandled_exception_can_include_traceback(self):
        def broken_handler(context):
            raise RuntimeError("trace")

        result = run_tool_app(
            tool_name="ToolA",
            run_handler=broken_handler,
            include_traceback=True,
            return_result=True,
        )

        self.assertIn("traceback", result.error)
        self.assertTrue(any("RuntimeError" in line for line in result.error["traceback"]))

    def test_keyboard_interrupt_is_captured(self):
        def interrupted_handler(context):
            raise KeyboardInterrupt()

        result = run_tool_app(
            tool_name="ToolA",
            run_handler=interrupted_handler,
            return_result=True,
        )

        self.assertEqual(result.status, APP_STATUS_INTERRUPTED)
        self.assertEqual(result.exit_code, EXIT_CODE_INTERRUPTED)

    def test_run_tool_app_with_factories_passes_objects_to_context(self):
        cli = {"quiet": True}
        runtime = {"run_id": "abc"}
        logger = FakeLogger()
        config = {"scan": {}}

        def handler(context):
            self.assertIs(context.cli_options, cli)
            self.assertIs(context.runtime, runtime)
            self.assertIs(context.logger, logger)
            self.assertIs(context.config, config)
            return 0

        result = run_tool_app_with_factories(
            tool_name="ToolA",
            cli_options_factory=lambda: cli,
            runtime_factory=lambda: runtime,
            logger_factory=lambda: logger,
            config_factory=lambda: config,
            run_handler=handler,
            return_result=True,
        )

        self.assertTrue(result.succeeded)

    def test_factory_exception_returns_startup_error(self):
        def broken_factory():
            raise RuntimeError("factory failed")

        result = run_tool_app_with_factories(
            tool_name="ToolA",
            cli_options_factory=broken_factory,
            run_handler=lambda context: 0,
            return_result=True,
        )

        self.assertEqual(result.exit_code, EXIT_CODE_STARTUP_ERROR)
        self.assertEqual(result.error["type"], "RuntimeError")

    def test_factory_keyboard_interrupt_returns_interrupted(self):
        def interrupted_factory():
            raise KeyboardInterrupt()

        result = run_tool_app_with_factories(
            tool_name="ToolA",
            cli_options_factory=interrupted_factory,
            run_handler=lambda context: 0,
            return_result=True,
        )

        self.assertEqual(result.exit_code, EXIT_CODE_INTERRUPTED)
        self.assertEqual(result.status, APP_STATUS_INTERRUPTED)

    def test_failed_exit_code_logs_error(self):
        logger = FakeLogger()
        result = run_tool_app(
            tool_name="ToolA",
            logger=logger,
            run_handler=lambda context: 9,
            return_result=True,
        )

        self.assertEqual(result.status, APP_STATUS_FAILED)
        self.assertEqual(logger.entries[-1][0], "error")

    def test_result_to_dict_is_json_safe(self):
        result = run_tool_app(
            tool_name="ToolA",
            tool_version="1.0.0",
            run_handler=lambda context: 0,
            return_result=True,
        )

        data = result.to_dict()

        self.assertEqual(data["tool"]["name"], "ToolA")
        self.assertEqual(data["tool"]["version"], "1.0.0")
        self.assertEqual(data["status"], APP_STATUS_OK)

    def test_public_imports_are_available(self):
        import app_core

        self.assertTrue(hasattr(app_core, "run_tool_app"))
        self.assertTrue(hasattr(app_core, "create_app_context"))
        self.assertTrue(hasattr(app_core, "EXIT_CODE_OK"))


if __name__ == "__main__":
    unittest.main()
