"""Shared constants for ProcessRunnerCore."""

from __future__ import annotations

DEFAULT_ENCODING = "utf-8"
DEFAULT_TIMEOUT_SECONDS = 60

PROCESS_STATUS_OK = "ok"
PROCESS_STATUS_FAILED = "failed"
PROCESS_STATUS_TIMEOUT = "timeout"
PROCESS_STATUS_EXECUTION_ERROR = "execution_error"

DEFAULT_ENVIRONMENT_OVERRIDES: dict[str, str] = {}
