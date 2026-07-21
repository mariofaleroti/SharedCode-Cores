"""Application bootstrap helpers for tool projects."""

from __future__ import annotations

from typing import Any, Callable, Optional

from .constants import (
    EXIT_CODE_GENERAL_ERROR,
    EXIT_CODE_INTERRUPTED,
    EXIT_CODE_STARTUP_ERROR,
)
from .context import create_app_context
from .lifecycle import (
    build_run_result,
    calculate_duration_ms,
    create_error_payload,
    normalize_handler_result,
    now_monotonic_ms,
    safe_log,
)
from .models import AppContext, AppRunResult, AppSettings, ToolHandler

Factory = Callable[[], Any]


def build_app_context(
    *,
    settings: AppSettings,
    cli_options: Any = None,
    runtime: Any = None,
    logger: Any = None,
    config: Any = None,
) -> AppContext:
    """Build an AppContext from already-created lifecycle objects."""

    return create_app_context(
        tool_name=settings.tool_name,
        tool_version=settings.tool_version,
        description=settings.description,
        cli_options=cli_options,
        runtime=runtime,
        logger=logger,
        config=config,
    )


def run_tool_app(
    *,
    tool_name: str,
    tool_version: str = "0.1.0",
    description: str = "",
    run_handler: ToolHandler,
    cli_options: Any = None,
    runtime: Any = None,
    logger: Any = None,
    config: Any = None,
    include_traceback: bool = False,
    return_result: bool = False,
) -> int | AppRunResult:
    """Run a concrete tool handler inside the common AppCore lifecycle.

    DESIGN: AppCore receives ready-made objects and orchestrates the lifecycle.
    It does not parse CLI arguments, create runtime folders, load configuration,
    or implement tool-specific business logic.
    """

    settings = AppSettings(
        tool_name=tool_name,
        tool_version=tool_version,
        description=description,
    )

    context = build_app_context(
        settings=settings,
        cli_options=cli_options,
        runtime=runtime,
        logger=logger,
        config=config,
    )

    result = execute_app_context(
        context=context,
        run_handler=run_handler,
        include_traceback=include_traceback,
    )

    return result if return_result else result.exit_code


def run_tool_app_with_factories(
    *,
    tool_name: str,
    tool_version: str = "0.1.0",
    description: str = "",
    run_handler: ToolHandler,
    cli_options_factory: Optional[Factory] = None,
    runtime_factory: Optional[Factory] = None,
    logger_factory: Optional[Factory] = None,
    config_factory: Optional[Factory] = None,
    include_traceback: bool = False,
    return_result: bool = False,
) -> int | AppRunResult:
    """Run a tool app while creating optional lifecycle objects through factories."""

    start_ms = now_monotonic_ms()
    settings = AppSettings(
        tool_name=tool_name,
        tool_version=tool_version,
        description=description,
    )

    try:
        cli_options = cli_options_factory() if cli_options_factory else None
        runtime = runtime_factory() if runtime_factory else None
        logger = logger_factory() if logger_factory else None
        config = config_factory() if config_factory else None
    except KeyboardInterrupt:
        context = build_app_context(settings=settings)
        result = build_run_result(
            context=context,
            exit_code=EXIT_CODE_INTERRUPTED,
            duration_ms=calculate_duration_ms(start_ms),
            error={"type": "KeyboardInterrupt", "message": "Execution interrupted."},
        )
        return result if return_result else result.exit_code
    except Exception as error:
        context = build_app_context(settings=settings)
        payload = create_error_payload(error, include_traceback=include_traceback)
        result = build_run_result(
            context=context,
            exit_code=EXIT_CODE_STARTUP_ERROR,
            duration_ms=calculate_duration_ms(start_ms),
            error=payload,
        )
        return result if return_result else result.exit_code

    context = build_app_context(
        settings=settings,
        cli_options=cli_options,
        runtime=runtime,
        logger=logger,
        config=config,
    )

    result = execute_app_context(
        context=context,
        run_handler=run_handler,
        include_traceback=include_traceback,
        start_ms=start_ms,
    )

    return result if return_result else result.exit_code


def execute_app_context(
    *,
    context: AppContext,
    run_handler: ToolHandler,
    include_traceback: bool = False,
    start_ms: Optional[int] = None,
) -> AppRunResult:
    """Execute a concrete handler using an already-built AppContext."""

    start_ms = now_monotonic_ms() if start_ms is None else start_ms

    safe_log(
        context.logger,
        "info",
        "Application started.",
        code="APP_STARTED",
        context={"tool_name": context.tool_name, "tool_version": context.tool_version},
    )

    try:
        handler_result = run_handler(context)
        exit_code = normalize_handler_result(handler_result)
        result = build_run_result(
            context=context,
            exit_code=exit_code,
            duration_ms=calculate_duration_ms(start_ms),
        )
    except KeyboardInterrupt:
        result = build_run_result(
            context=context,
            exit_code=EXIT_CODE_INTERRUPTED,
            duration_ms=calculate_duration_ms(start_ms),
            error={"type": "KeyboardInterrupt", "message": "Execution interrupted."},
        )
    except Exception as error:
        payload = create_error_payload(error, include_traceback=include_traceback)
        result = build_run_result(
            context=context,
            exit_code=EXIT_CODE_GENERAL_ERROR,
            duration_ms=calculate_duration_ms(start_ms),
            error=payload,
        )

    if result.succeeded:
        safe_log(
            context.logger,
            "info",
            "Application finished successfully.",
            code="APP_FINISHED",
            context={"exit_code": result.exit_code, "duration_ms": result.duration_ms},
        )
    else:
        safe_log(
            context.logger,
            "error",
            "Application finished with errors.",
            code="APP_FAILED",
            context={
                "exit_code": result.exit_code,
                "duration_ms": result.duration_ms,
                "error": result.error,
            },
        )

    return result
