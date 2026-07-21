"""Safe external process runner."""

from __future__ import annotations

import os
import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from time import perf_counter
from typing import Any

from date_time_core import utc_now_iso

from .constants import (
    DEFAULT_ENCODING,
    DEFAULT_TIMEOUT_SECONDS,
    PROCESS_STATUS_EXECUTION_ERROR,
    PROCESS_STATUS_FAILED,
    PROCESS_STATUS_OK,
    PROCESS_STATUS_TIMEOUT,
)
from .models import ProcessCommand, ProcessRunOptions, ProcessRunResult


def normalize_command(command: str | os.PathLike[str] | Sequence[str | os.PathLike[str]]) -> tuple[str, ...]:
    """Normalize a command into a tuple of string arguments.

    DESIGN: A plain string is accepted as one executable token, not split into
    arguments. Callers must pass a list/tuple when arguments are needed.
    """
    if isinstance(command, (str, os.PathLike)):
        value = os.fspath(command)
        if not value.strip():
            raise ValueError("Command cannot be empty.")
        return (value,)

    if not isinstance(command, Sequence):
        raise TypeError("Command must be a string, path-like object, or a sequence of arguments.")

    args = tuple(os.fspath(item) for item in command)
    if not args:
        raise ValueError("Command cannot be empty.")

    if any(not item.strip() for item in args):
        raise ValueError("Command arguments cannot be empty.")

    return args


def run_process(
    command: str | os.PathLike[str] | Sequence[str | os.PathLike[str]],
    *,
    timeout_seconds: float | None = DEFAULT_TIMEOUT_SECONDS,
    cwd: str | os.PathLike[str] | None = None,
    env: Mapping[str, str] | None = None,
    shell: bool = False,
    encoding: str = DEFAULT_ENCODING,
    trim_output: bool = False,
) -> ProcessRunResult:
    """Run an external process and return a structured result.

    WARNING: shell=True should only be used when the caller intentionally needs
    shell behavior. The safe default is shell=False with explicit arguments.
    """
    options = ProcessRunOptions(
        timeout_seconds=timeout_seconds,
        cwd=Path(cwd) if cwd is not None else None,
        env=env,
        shell=shell,
        encoding=encoding,
        trim_output=trim_output,
    )
    return ProcessRunner().run(command, options=options)


class ProcessRunner:
    """Small reusable runner for external commands."""

    def run(
        self,
        command: str | os.PathLike[str] | Sequence[str | os.PathLike[str]],
        *,
        options: ProcessRunOptions | None = None,
    ) -> ProcessRunResult:
        """Run a command with the provided options."""
        options = options or ProcessRunOptions(timeout_seconds=DEFAULT_TIMEOUT_SECONDS)
        args = normalize_command(command)
        process_command = ProcessCommand(
            args=args,
            cwd=options.cwd,
            env=options.env,
            shell=options.shell,
        )

        started_at = utc_now_iso()
        start_time = perf_counter()

        try:
            completed = subprocess.run(
                args if not options.shell else process_command.display(),
                cwd=str(options.cwd) if options.cwd is not None else None,
                env=_build_environment(options.env),
                shell=options.shell,
                capture_output=True,
                text=True,
                encoding=options.encoding,
                errors="replace",
                timeout=options.timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as error:
            return _build_timeout_result(process_command, options, started_at, start_time, error)
        except OSError as error:
            return _build_execution_error_result(process_command, options, started_at, start_time, error)

        duration_ms = _elapsed_ms(start_time)
        stdout = completed.stdout or ""
        stderr = completed.stderr or ""

        if options.trim_output:
            stdout = stdout.strip()
            stderr = stderr.strip()

        status = PROCESS_STATUS_OK if completed.returncode == 0 else PROCESS_STATUS_FAILED

        return ProcessRunResult(
            command=process_command,
            status=status,
            exit_code=completed.returncode,
            stdout=stdout,
            stderr=stderr,
            duration_ms=duration_ms,
            started_at=started_at,
            ended_at=utc_now_iso(),
            timeout_seconds=options.timeout_seconds,
        )


def _build_environment(overrides: Mapping[str, str] | None) -> dict[str, str] | None:
    if overrides is None:
        return None

    environment = dict(os.environ)
    environment.update({str(key): str(value) for key, value in overrides.items()})
    return environment


def _build_timeout_result(
    command: ProcessCommand,
    options: ProcessRunOptions,
    started_at: str,
    start_time: float,
    error: subprocess.TimeoutExpired,
) -> ProcessRunResult:
    stdout = _safe_process_output(error.stdout)
    stderr = _safe_process_output(error.stderr)

    if not stderr:
        stderr = f"Process timed out after {options.timeout_seconds} seconds."

    return ProcessRunResult(
        command=command,
        status=PROCESS_STATUS_TIMEOUT,
        exit_code=None,
        stdout=stdout,
        stderr=stderr,
        duration_ms=_elapsed_ms(start_time),
        started_at=started_at,
        ended_at=utc_now_iso(),
        timed_out=True,
        timeout_seconds=options.timeout_seconds,
        exception_type=type(error).__name__,
        exception_message=str(error),
    )


def _build_execution_error_result(
    command: ProcessCommand,
    options: ProcessRunOptions,
    started_at: str,
    start_time: float,
    error: OSError,
) -> ProcessRunResult:
    return ProcessRunResult(
        command=command,
        status=PROCESS_STATUS_EXECUTION_ERROR,
        exit_code=None,
        stdout="",
        stderr=str(error),
        duration_ms=_elapsed_ms(start_time),
        started_at=started_at,
        ended_at=utc_now_iso(),
        timeout_seconds=options.timeout_seconds,
        exception_type=type(error).__name__,
        exception_message=str(error),
    )


def _safe_process_output(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(DEFAULT_ENCODING, errors="replace")
    return str(value)


def _elapsed_ms(start_time: float) -> int:
    return max(0, round((perf_counter() - start_time) * 1000))
