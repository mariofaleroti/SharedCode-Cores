"""PlatformCore exceptions."""

from __future__ import annotations


class PlatformCoreError(Exception):
    """Base exception for PlatformCore."""


class UnsupportedPlatformError(PlatformCoreError):
    """Raised when an operation is not supported by the current OS."""
