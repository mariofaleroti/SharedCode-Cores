"""Lifecycle utilities for AppCore."""

from __future__ import annotations

import time
import traceback
from typing import Any, Dict, Optional

from .constants import (
    APP_STATUS_FAILED,
    APP_STATUS_INTERRUPTED,
    APP_STATUS_OK,
    EXIT_CODE_GENERAL_ERROR,
    EXIT_CODE_INTERRUPTED,
    EXIT_CODE_OK,
)
from .models import AppContext, AppRunResult


def now_monotonic_ms() -> int:
    """Return a monotonic timestamp in milliseconds."""

    return int(time.perf_counter() * 1000)


def calculate_duration_ms(start_ms: int) -> int:
    """Calculate elapsed milliseconds from a monotonic timestamp."""

    return max(0, now_monotonic_ms() - start_ms)


def safe_log(logger: Any, level: str, message: str, **kwargs: Any) -> None:
    """Write a log message if the provided logger supports the requested level."""

    if logger is None:
        return

    log_method = getattr(logger, level, None)
    if not callable(log_method):
        return

    try:
        log_method(message, **kwargs)
    except TypeError:
        # NOTE: Some logger implementations may accept only a message argument.
        try:
            log_method(message)
        except Exception:
            return
    except Exception:
        return


def create_error_payload(error: BaseException, *, include_traceback: bool = False) -> Dict[str, Any]:
    """Create a JSON-safe error payload from an exception."""

    payload: Dict[str, Any] = {
        "type": type(error).__name__,
        "message": str(error),
    }

    if include_traceback:
        payload["traceback"] = traceback.format_exception(
            type(error),
            error,
            error.__traceback__,
        )

    return payload


def normalize_handler_result(value: Any) -> int:
    """Convert a concrete handler return value into an exit code.

    Supported return values:
    - None -> 0
    - bool -> 0 for True, 1 for False
    - int -> that value
    - object with exit_code attribute -> int(exit_code)
    """

    if value is None:
        return EXIT_CODE_OK

    if isinstance(value, bool):
        return EXIT_CODE_OK if value else EXIT_CODE_GENERAL_ERROR

    if isinstance(value, int):
        return value

    exit_code = getattr(value, "exit_code", None)
    if isinstance(exit_code, int):
        return exit_code

    return EXIT_CODE_OK


def build_run_result(
    *,
    context: AppContext,
    exit_code: int,
    duration_ms: int,
    error: Optional[Dict[str, Any]] = None,
) -> AppRunResult:
    """Build the final lifecycle result from normalized values."""

    if exit_code == EXIT_CODE_INTERRUPTED:
        status = APP_STATUS_INTERRUPTED
    elif exit_code == EXIT_CODE_OK and error is None:
        status = APP_STATUS_OK
    else:
        status = APP_STATUS_FAILED

    return AppRunResult(
        status=status,
        exit_code=exit_code,
        duration_ms=duration_ms,
        error=error,
        context=context,
    )
