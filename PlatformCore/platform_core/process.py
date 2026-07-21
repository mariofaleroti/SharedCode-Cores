"""Small platform helpers for executable/script naming."""

from __future__ import annotations

from .constants import PLATFORM_LINUX, PLATFORM_WINDOWS
from .detection import get_platform_name
from .exceptions import UnsupportedPlatformError


def get_executable_suffix(platform_name: str | None = None) -> str:
    """Return the executable suffix for the target platform."""

    current_platform = platform_name or get_platform_name()
    if current_platform == PLATFORM_WINDOWS:
        return ".exe"
    if current_platform == PLATFORM_LINUX:
        return ""
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def get_script_suffix(platform_name: str | None = None) -> str:
    """Return the preferred helper-script suffix for the target platform."""

    current_platform = platform_name or get_platform_name()
    if current_platform == PLATFORM_WINDOWS:
        return ".cmd"
    if current_platform == PLATFORM_LINUX:
        return ".sh"
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")
