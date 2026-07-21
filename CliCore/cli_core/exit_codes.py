"""Exit code helpers shared by command-line tools."""

from __future__ import annotations

from .constants import EXIT_ERROR, EXIT_OK, EXIT_USAGE_ERROR


def exit_code_from_success(success: bool) -> int:
    """Return the standard exit code for a boolean success value."""

    return EXIT_OK if success else EXIT_ERROR


def exit_code_from_validation(
    *,
    is_valid: bool,
    has_warnings: bool = False,
    fail_on_warnings: bool = False,
) -> int:
    """Return a standard exit code for validation-style commands."""

    if not is_valid:
        return EXIT_ERROR

    if has_warnings and fail_on_warnings:
        return EXIT_ERROR

    return EXIT_OK
