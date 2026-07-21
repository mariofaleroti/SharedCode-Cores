"""
Data models used by LoggingCore.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from date_time_core import (
    create_timestamp_pair,
    datetime_to_local_iso,
    datetime_to_utc_iso,
    ensure_timezone,
    format_iso_for_log,
    local_now_iso,
    parse_iso_datetime,
    utc_now_iso,
)

from .constants import normalize_level


def format_local_iso_for_log(value: str) -> str:
    """Return a local ISO timestamp using a human-readable log format."""
    return format_iso_for_log(value)


def make_json_safe(value: Any) -> Any:
    """Convert common Python values into JSON-safe structures."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, dict):
        return {str(key): make_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [make_json_safe(item) for item in value]

    if isinstance(value, datetime):
        return datetime_to_utc_iso(value)

    if isinstance(value, Exception):
        return {
            "type": value.__class__.__name__,
            "message": str(value),
        }

    return str(value)


@dataclass(frozen=True)
class LogEntry:
    """Single human-readable and structured log event."""

    level: str
    message: str
    code: str
    source: str
    timestamp_utc: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp_local: Optional[str] = None

    def __post_init__(self) -> None:
        timestamp_utc, timestamp_local = _resolve_timestamp_pair(
            self.timestamp_utc,
            self.timestamp_local,
        )

        object.__setattr__(self, "level", normalize_level(self.level))
        object.__setattr__(self, "message", str(self.message))
        object.__setattr__(self, "code", str(self.code).strip().upper())
        object.__setattr__(self, "source", str(self.source))
        object.__setattr__(self, "timestamp_utc", timestamp_utc)
        object.__setattr__(self, "timestamp_local", timestamp_local)
        object.__setattr__(self, "context", make_json_safe(self.context or {}))

    @property
    def timestamp_local_display(self) -> str:
        """Return the local timestamp formatted for text logs."""
        return format_local_iso_for_log(str(self.timestamp_local or ""))

    def to_diagnostic_dict(self) -> Dict[str, Any]:
        """Return this entry as a diagnostics-compatible dictionary."""
        return {
            "level": self.level,
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "source": self.source,
            "timestamp_utc": self.timestamp_utc,
            "timestamp_local": self.timestamp_local,
        }

    def to_error_dict(self) -> Dict[str, Any]:
        """Return this entry as an errors-compatible dictionary."""
        return {
            "code": self.code,
            "message": self.message,
            "context": self.context,
            "source": self.source,
            "timestamp_utc": self.timestamp_utc,
            "timestamp_local": self.timestamp_local,
        }


@dataclass(frozen=True)
class LoggerConfig:
    """Configuration for a SharedLogger instance."""

    name: str
    min_level: str = "info"
    log_path: Optional[str] = None
    keep_entries: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(self, "name", str(self.name))
        object.__setattr__(self, "min_level", normalize_level(self.min_level))


def _resolve_timestamp_pair(
    timestamp_utc: Optional[str],
    timestamp_local: Optional[str],
) -> tuple[str, str]:
    """Resolve UTC and local timestamp strings using one consistent standard."""
    if timestamp_utc is None and timestamp_local is None:
        return create_timestamp_pair()

    if timestamp_utc is not None:
        parsed_utc = parse_iso_datetime(str(timestamp_utc), default_timezone=timezone.utc)
        return datetime_to_utc_iso(parsed_utc), datetime_to_local_iso(parsed_utc)

    local_default_timezone = datetime.now().astimezone().tzinfo or timezone.utc
    parsed_local = parse_iso_datetime(str(timestamp_local), default_timezone=local_default_timezone)
    return datetime_to_utc_iso(parsed_local), datetime_to_local_iso(parsed_local)


def _ensure_timezone(value: datetime, *, default_timezone: timezone) -> datetime:
    """Return a timezone-aware datetime.

    Kept as a private compatibility wrapper for older internal imports.
    """
    return ensure_timezone(value, default_timezone=default_timezone)
