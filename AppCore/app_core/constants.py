"""Shared constants for AppCore."""

from __future__ import annotations

APP_STATUS_OK = "ok"
APP_STATUS_FAILED = "failed"
APP_STATUS_INTERRUPTED = "interrupted"
APP_STATUS_STARTUP_FAILED = "startup_failed"

EXIT_CODE_OK = 0
EXIT_CODE_GENERAL_ERROR = 1
EXIT_CODE_STARTUP_ERROR = 2
EXIT_CODE_INTERRUPTED = 130

DEFAULT_TOOL_VERSION = "0.1.0"
