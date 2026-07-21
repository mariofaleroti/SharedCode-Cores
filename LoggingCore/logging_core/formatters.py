"""
Formatting helpers for human-readable logs.
"""

from __future__ import annotations

import json

from .models import LogEntry


def format_log_line(entry: LogEntry) -> str:
    """Format a LogEntry as one human-readable log line."""
    # DESIGN:
    # Text logs are optimized for humans. The structured LogEntry still keeps
    # UTC timestamps for contracts, diagnostics, and machine processing.
    parts = [
        entry.timestamp_local_display,
        entry.level.upper(),
        entry.source,
        entry.code,
        entry.message,
    ]

    if entry.context:
        context_json = json.dumps(
            entry.context,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        parts.append(f"context={context_json}")

    return " | ".join(parts)
