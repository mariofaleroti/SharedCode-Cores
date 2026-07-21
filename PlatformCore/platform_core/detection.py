"""Operating-system detection helpers for Windows/Linux tools."""

from __future__ import annotations

import platform
import sys

from .constants import PLATFORM_LINUX, PLATFORM_UNSUPPORTED, PLATFORM_WINDOWS, SUPPORTED_PLATFORMS


def get_platform_name(system_name: str | None = None, sys_platform: str | None = None) -> str:
    """Return the normalized platform name used by ShareCode.

    PlatformCore intentionally supports only Windows and Linux. Other systems are
    reported as ``unsupported`` instead of being guessed implicitly.
    """

    raw_system = (system_name if system_name is not None else platform.system()).strip().lower()
    raw_sys_platform = (sys_platform if sys_platform is not None else sys.platform).strip().lower()

    if raw_system.startswith("win") or raw_sys_platform.startswith("win"):
        return PLATFORM_WINDOWS
    if raw_system == "linux" or raw_sys_platform.startswith("linux"):
        return PLATFORM_LINUX
    return PLATFORM_UNSUPPORTED


def is_windows(platform_name: str | None = None) -> bool:
    """Return True when the provided/current platform is Windows."""

    return (platform_name or get_platform_name()) == PLATFORM_WINDOWS


def is_linux(platform_name: str | None = None) -> bool:
    """Return True when the provided/current platform is Linux."""

    return (platform_name or get_platform_name()) == PLATFORM_LINUX


def is_supported_platform(platform_name: str | None = None) -> bool:
    """Return True for platforms intentionally supported by PlatformCore."""

    return (platform_name or get_platform_name()) in SUPPORTED_PLATFORMS
