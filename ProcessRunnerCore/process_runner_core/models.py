"""Data models used by ProcessRunnerCore."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

from date_time_core import utc_now_iso

from .constants import (
    PROCESS_STATUS_EXECUTION_ERROR,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_OK,
    PROCESS_STATUS_TIMEOUT,
)

JsonDict = dict[str, Any]


@dataclass(frozen=True)
class ProcessCommand:
    """Normalized external command definition.

    DESIGN: Commands are represented as argument lists to avoid shell parsing by
    default. This keeps callers explicit and avoids accidental shell injection.
    """

    args: tuple[str, ...]
    cwd: Path | None = None
    env: Mapping[str, str] | None = None
    shell: bool = False

    def display(self) -> str:
        """Return a readable command representation for logs and diagnostics."""
        return " ".join(self.args)

    def to_dict(self) -> JsonDict:
        return {
            "args": list(self.args),
            "display": self.display(),
            "cwd": str(self.cwd) if self.cwd is not None else None,
            "shell": self.shell,
        }


@dataclass(frozen=True)
class ProcessRunResult:
    """Structured result returned after running an external process."""

    command: ProcessCommand
    status: str
    exit_code: int | None
    stdout: str = ""
    stderr: str = ""
    duration_ms: int = 0
    started_at: str = field(default_factory=utc_now_iso)
    ended_at: str | None = None
    timed_out: bool = False
    timeout_seconds: float | None = None
    exception_type: str | None = None
    exception_message: str | None = None

    @property
    def succeeded(self) -> bool:
        """Return True when the command completed with exit code 0."""
        return self.status == PROCESS_STATUS_OK and self.exit_code == 0

    @property
    def failed(self) -> bool:
        """Return True when the command did not succeed."""
        return not self.succeeded

    def to_dict(self) -> JsonDict:
        """Return a JSON-safe representation of the result."""
        return {
            "command": self.command.to_dict(),
            "status": self.status,
            "exit_code": self.exit_code,
            "succeeded": self.succeeded,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "duration_ms": self.duration_ms,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "timed_out": self.timed_out,
            "timeout_seconds": self.timeout_seconds,
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
        }

    def to_diagnostic(self, code: str = "PROCESS_COMPLETED") -> JsonDict:
        """Return a diagnostic entry compatible with JsonContractCore."""
        level = "info" if self.succeeded else "warning"
        message = "Process completed successfully." if self.succeeded else "Process completed with a non-zero or abnormal status."

        return {
            "level": level,
            "code": code,
            "message": message,
            "context": self._context_summary(),
        }

    def to_error(self, code: str = "PROCESS_FAILED") -> JsonDict | None:
        """Return an error entry compatible with JsonContractCore, if needed."""
        if self.succeeded:
            return None

        if self.status == PROCESS_STATUS_TIMEOUT:
            message = "Process timed out."
        elif self.status == PROCESS_STATUS_EXECUTION_ERROR:
            message = "Process could not be started."
        elif self.status == PROCESS_STATUS_FAILED:
            message = "Process finished with a non-zero exit code."
        else:
            message = "Process failed."

        return {
            "code": code,
            "message": message,
            "context": self._context_summary(),
        }

    def _context_summary(self) -> JsonDict:
        return {
            "command": self.command.display(),
            "args": list(self.command.args),
            "cwd": str(self.command.cwd) if self.command.cwd is not None else None,
            "exit_code": self.exit_code,
            "status": self.status,
            "duration_ms": self.duration_ms,
            "timed_out": self.timed_out,
            "timeout_seconds": self.timeout_seconds,
            "stderr_preview": self.stderr[:500],
            "exception_type": self.exception_type,
            "exception_message": self.exception_message,
        }


@dataclass(frozen=True)
class ProcessRunOptions:
    """Execution options for an external process."""

    timeout_seconds: float | None = None
    cwd: Path | None = None
    env: Mapping[str, str] | None = None
    shell: bool = False
    encoding: str = "utf-8"
    trim_output: bool = False
