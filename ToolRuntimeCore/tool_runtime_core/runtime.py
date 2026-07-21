"""Runtime context factory for external tools."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from date_time_core import datetime_to_run_id_timestamp, ensure_timezone, utc_now

from .constants import (
    DEFAULT_LOGS_DIRECTORY_NAME,
    DEFAULT_OUTPUT_DIRECTORY_NAME,
    DEFAULT_RUNTIME_DIRECTORY_NAME,
    DEFAULT_TEMP_DIRECTORY_NAME,
    DEFAULT_TOOL_VERSION,
)
from .models import ToolRuntimeContext

_SAFE_NAME_PATTERN = re.compile(r"[^A-Za-z0-9_.-]+")


def normalize_runtime_name(value: str, *, fallback: str = "tool") -> str:
    """Normalize a name so it can be safely used in generated file names."""
    cleaned = _SAFE_NAME_PATTERN.sub("_", value.strip()).strip("._-")
    return cleaned or fallback


def create_run_id(started_at: Optional[datetime] = None) -> str:
    """Create a unique run identifier based on UTC time and a short random suffix."""
    timestamp_source = ensure_timezone(started_at or utc_now())
    timestamp = datetime_to_run_id_timestamp(timestamp_source)
    suffix = uuid.uuid4().hex[:8]
    return f"{timestamp}_{suffix}"


def create_runtime_context(
    *,
    tool_name: str,
    tool_version: str = DEFAULT_TOOL_VERSION,
    base_dir: str | Path | None = None,
    output_dir: str | Path | None = None,
    logs_dir: str | Path | None = None,
    temp_dir: str | Path | None = None,
    runtime_dir: str | Path | None = None,
    run_id: str | None = None,
    started_at_utc: datetime | None = None,
    create_directories: bool = True,
) -> ToolRuntimeContext:
    """Create a resolved runtime context for a tool execution."""
    if not tool_name or not tool_name.strip():
        raise ValueError("tool_name is required.")

    started_at = ensure_timezone(started_at_utc or utc_now()).astimezone(timezone.utc)

    resolved_base_dir = Path(base_dir or Path.cwd()).expanduser().resolve()
    resolved_output_dir = _resolve_child_or_absolute(
        output_dir,
        default_parent=resolved_base_dir,
        default_name=DEFAULT_OUTPUT_DIRECTORY_NAME,
    )
    resolved_logs_dir = _resolve_child_or_absolute(
        logs_dir,
        default_parent=resolved_output_dir,
        default_name=DEFAULT_LOGS_DIRECTORY_NAME,
    )
    resolved_temp_dir = _resolve_child_or_absolute(
        temp_dir,
        default_parent=resolved_output_dir,
        default_name=DEFAULT_TEMP_DIRECTORY_NAME,
    )
    resolved_runtime_dir = _resolve_child_or_absolute(
        runtime_dir,
        default_parent=resolved_output_dir,
        default_name=DEFAULT_RUNTIME_DIRECTORY_NAME,
    )

    context = ToolRuntimeContext(
        tool_name=normalize_runtime_name(tool_name),
        tool_version=tool_version,
        run_id=run_id or create_run_id(started_at),
        started_at_utc=started_at,
        base_dir=resolved_base_dir,
        output_dir=resolved_output_dir,
        logs_dir=resolved_logs_dir,
        temp_dir=resolved_temp_dir,
        runtime_dir=resolved_runtime_dir,
    )

    if create_directories:
        context.ensure_directories()

    return context


def _resolve_child_or_absolute(
    value: str | Path | None,
    *,
    default_parent: Path,
    default_name: str,
) -> Path:
    """Resolve a configured directory path."""
    if value is None:
        return (default_parent / default_name).resolve()

    candidate = Path(value).expanduser()
    if candidate.is_absolute():
        return candidate.resolve()

    return (default_parent / candidate).resolve()
