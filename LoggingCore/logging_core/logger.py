"""
Main logger implementation for LoggingCore.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from .constants import (
    DEBUG,
    DEFAULT_DEBUG_CODE,
    DEFAULT_ERROR_CODE,
    DEFAULT_INFO_CODE,
    DEFAULT_MIN_LEVEL,
    DEFAULT_WARNING_CODE,
    ERROR,
    INFO,
    WARNING,
    level_priority,
    normalize_level,
)
from .models import LogEntry, LoggerConfig
from .writer import TextLogWriter, create_writer


class SharedLogger:
    """Small structured logger for shared ecosystem tools."""

    def __init__(
        self,
        name: str,
        log_path: Optional[Path | str] = None,
        min_level: str = DEFAULT_MIN_LEVEL,
        keep_entries: bool = True,
    ) -> None:
        self.config = LoggerConfig(
            name=name,
            min_level=min_level,
            log_path=str(log_path) if log_path is not None else None,
            keep_entries=keep_entries,
        )
        self._writer: Optional[TextLogWriter] = create_writer(log_path)
        self._entries: List[LogEntry] = []

    @property
    def entries(self) -> List[LogEntry]:
        """Return a copy of retained log entries."""
        return list(self._entries)

    def log(
        self,
        level: str,
        message: str,
        code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LogEntry]:
        """Record one event when it passes the configured minimum level."""
        normalized_level = normalize_level(level)

        if level_priority(normalized_level) < level_priority(self.config.min_level):
            return None

        entry = LogEntry(
            level=normalized_level,
            message=message,
            code=code or _default_code_for_level(normalized_level),
            source=self.config.name,
            context=context or {},
        )

        if self.config.keep_entries:
            self._entries.append(entry)

        if self._writer is not None:
            self._writer.write(entry)

        return entry

    def debug(
        self,
        message: str,
        code: str = DEFAULT_DEBUG_CODE,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LogEntry]:
        """Record a debug event."""
        return self.log(DEBUG, message, code=code, context=context)

    def info(
        self,
        message: str,
        code: str = DEFAULT_INFO_CODE,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LogEntry]:
        """Record an informational event."""
        return self.log(INFO, message, code=code, context=context)

    def warning(
        self,
        message: str,
        code: str = DEFAULT_WARNING_CODE,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LogEntry]:
        """Record a warning event."""
        return self.log(WARNING, message, code=code, context=context)

    def error(
        self,
        message: str,
        code: str = DEFAULT_ERROR_CODE,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LogEntry]:
        """Record an error event."""
        return self.log(ERROR, message, code=code, context=context)

    def exception(
        self,
        message: str,
        error: BaseException,
        code: str = DEFAULT_ERROR_CODE,
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[LogEntry]:
        """Record an exception as a structured error event."""
        merged_context: Dict[str, Any] = dict(context or {})
        merged_context["exception"] = error
        return self.error(message, code=code, context=merged_context)

    def get_diagnostics(
        self,
        include_info: bool = False,
        include_debug: bool = False,
    ) -> List[Dict[str, Any]]:
        """Return retained entries formatted for the diagnostics contract list."""
        allowed_levels = {WARNING, ERROR}

        if include_info:
            allowed_levels.add(INFO)

        if include_debug:
            allowed_levels.add(DEBUG)

        return [
            entry.to_diagnostic_dict()
            for entry in self._entries
            if entry.level in allowed_levels
        ]

    def get_errors(self) -> List[Dict[str, Any]]:
        """Return retained error entries formatted for the errors contract list."""
        return [
            entry.to_error_dict()
            for entry in self._entries
            if entry.level == ERROR
        ]

    def has_errors(self) -> bool:
        """Return True when at least one retained error exists."""
        return any(entry.level == ERROR for entry in self._entries)

    def clear(self) -> None:
        """Clear retained in-memory entries without touching the log file."""
        self._entries.clear()


def create_logger(
    name: str,
    log_path: Optional[Path | str] = None,
    min_level: str = DEFAULT_MIN_LEVEL,
    keep_entries: bool = True,
) -> SharedLogger:
    """Create a SharedLogger instance."""
    return SharedLogger(
        name=name,
        log_path=log_path,
        min_level=min_level,
        keep_entries=keep_entries,
    )


def _default_code_for_level(level: str) -> str:
    """Return the default event code for a normalized level."""
    if level == DEBUG:
        return DEFAULT_DEBUG_CODE
    if level == INFO:
        return DEFAULT_INFO_CODE
    if level == WARNING:
        return DEFAULT_WARNING_CODE
    return DEFAULT_ERROR_CODE
