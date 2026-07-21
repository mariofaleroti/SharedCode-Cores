"""Runtime models for external tools."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from date_time_core import (
    datetime_to_local_iso,
    datetime_to_utc_iso,
    ensure_timezone,
    format_utc_offset,
    utc_now,
)


@dataclass(frozen=True)
class ToolRuntimeContext:
    """Resolved execution context for one tool run."""

    tool_name: str
    tool_version: str
    run_id: str
    started_at_utc: datetime
    base_dir: Path
    output_dir: Path
    logs_dir: Path
    temp_dir: Path
    runtime_dir: Path

    @property
    def started_at_iso(self) -> str:
        """Return the UTC start time as an ISO-8601 string.

        NOTE:
        This property is kept for backward compatibility. New code should use
        started_at_utc_iso or started_at_local_iso depending on the audience.
        """
        return self.started_at_utc_iso

    @property
    def started_at_utc_iso(self) -> str:
        """Return the UTC start time as a compact ISO-8601 string."""
        return datetime_to_utc_iso(self.started_at_utc)

    @property
    def started_at_local(self) -> datetime:
        """Return the start time converted to the local timezone."""
        return ensure_timezone(self.started_at_utc).astimezone()

    @property
    def started_at_local_iso(self) -> str:
        """Return the local start time as an ISO-8601 string."""
        return datetime_to_local_iso(self.started_at_utc)

    @property
    def local_timezone_name(self) -> str:
        """Return the local timezone display name when available."""
        return self.started_at_local.tzname() or "local"

    @property
    def local_utc_offset(self) -> str:
        """Return the local UTC offset using +HH:MM or -HH:MM notation."""
        return format_utc_offset(self.started_at_local)

    def ensure_directories(self) -> None:
        """Create the standard runtime directories if they do not exist."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def get_log_path(self, file_name: str | None = None) -> Path:
        """Return a path inside the logs directory."""
        name = file_name or f"{self.tool_name}.log"
        return self.logs_dir / name

    def get_output_path(self, file_name: str) -> Path:
        """Return a path inside the output directory."""
        return self.output_dir / file_name

    def get_temp_path(self, file_name: str) -> Path:
        """Return a path inside the temp directory."""
        return self.temp_dir / file_name

    def get_runtime_path(self, file_name: str) -> Path:
        """Return a path inside the runtime directory."""
        return self.runtime_dir / file_name

    def to_meta(self, *, module_name: str | None = None, file_type: str | None = None) -> Dict[str, Any]:
        """Return metadata compatible with the ecosystem JSON contract."""
        # DESIGN:
        # UTC remains the stable technical timestamp. Local time is included as
        # companion metadata for human review without forcing consumers to infer
        # the workstation timezone.
        meta: Dict[str, Any] = {
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "run_id": self.run_id,
            "started_at_utc": self.started_at_utc_iso,
            "started_at_local": self.started_at_local_iso,
            "local_timezone": self.local_timezone_name,
            "local_utc_offset": self.local_utc_offset,
        }

        if module_name is not None:
            meta["module_name"] = module_name

        if file_type is not None:
            meta["file_type"] = file_type

        return meta

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation of the runtime context."""
        return {
            "tool_name": self.tool_name,
            "tool_version": self.tool_version,
            "run_id": self.run_id,
            "started_at_utc": self.started_at_utc_iso,
            "started_at_local": self.started_at_local_iso,
            "local_timezone": self.local_timezone_name,
            "local_utc_offset": self.local_utc_offset,
            "base_dir": str(self.base_dir),
            "output_dir": str(self.output_dir),
            "logs_dir": str(self.logs_dir),
            "temp_dir": str(self.temp_dir),
            "runtime_dir": str(self.runtime_dir),
        }

