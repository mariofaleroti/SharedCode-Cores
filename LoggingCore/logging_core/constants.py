"""
Shared constants for LoggingCore.
"""

from __future__ import annotations

DEBUG = "debug"
INFO = "info"
WARNING = "warning"
ERROR = "error"

LOG_LEVELS = (DEBUG, INFO, WARNING, ERROR)

_LEVEL_PRIORITY = {
    DEBUG: 10,
    INFO: 20,
    WARNING: 30,
    ERROR: 40,
}

DEFAULT_MIN_LEVEL = INFO
DEFAULT_ERROR_CODE = "ERROR"
DEFAULT_WARNING_CODE = "WARNING"
DEFAULT_INFO_CODE = "INFO"
DEFAULT_DEBUG_CODE = "DEBUG"


def normalize_level(level: str) -> str:
    """Return a normalized log level or raise ValueError for unsupported levels."""
    normalized = str(level).strip().lower()

    if normalized not in LOG_LEVELS:
        raise ValueError(f"Unsupported log level: {level!r}")

    return normalized


def level_priority(level: str) -> int:
    """Return the numeric priority for a normalized log level."""
    return _LEVEL_PRIORITY[normalize_level(level)]
