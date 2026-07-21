"""
Filesystem error helpers for FileScanCore.

DESIGN:
This module classifies scan errors in a generic way.
It must not decide whether an error is critical for a specific tool.
"""

from __future__ import annotations

from pathlib import Path

from .models import ScanError


def build_scan_error(
    path: str | Path,
    error: BaseException,
    *,
    stage: str = "scan",
) -> ScanError:
    """Builds a structured ScanError from a filesystem exception."""

    if isinstance(error, PermissionError):
        error_type = "permission_denied"
    elif isinstance(error, FileNotFoundError):
        error_type = "path_not_found"
    elif isinstance(error, NotADirectoryError):
        error_type = "not_a_directory"
    elif isinstance(error, OSError):
        error_type = "os_error"
    else:
        error_type = "unknown_error"

    return ScanError(
        path=Path(path),
        error_type=error_type,
        message=str(error),
        exception_type=type(error).__name__,
        stage=stage,
    )


def build_validation_error(
    path: str | Path,
    error_type: str,
    message: str,
    *,
    stage: str = "validation",
) -> ScanError:
    """Builds a structured ScanError for invalid scan input."""

    return ScanError(
        path=Path(path),
        error_type=error_type,
        message=message,
        exception_type=None,
        stage=stage,
    )
