"""PlatformCore public API."""

from __future__ import annotations

from .constants import PLATFORM_LINUX, PLATFORM_UNSUPPORTED, PLATFORM_WINDOWS, SUPPORTED_PLATFORMS
from .detection import get_platform_name, is_linux, is_supported_platform, is_windows
from .exceptions import PlatformCoreError, UnsupportedPlatformError
from .filesystem import is_hidden, is_symlink_or_reparse
from .opener import (
    OpenCommand,
    build_open_folder_command,
    build_open_path_command,
    build_reveal_in_folder_command,
    open_folder,
    open_path,
    reveal_in_folder,
)
from .paths import (
    get_app_data_dir,
    get_cache_dir,
    get_config_dir,
    get_documents_dir,
    get_home_dir,
    get_logs_dir,
    get_temp_dir,
    build_portable_path_variables,
    normalize_path,
    resolve_portable_path,
    resolve_portable_paths,
    normalize_tool_name,
    path_to_display,
)
from .process import get_executable_suffix, get_script_suffix

__all__ = [
    "PLATFORM_LINUX",
    "PLATFORM_UNSUPPORTED",
    "PLATFORM_WINDOWS",
    "SUPPORTED_PLATFORMS",
    "OpenCommand",
    "PlatformCoreError",
    "UnsupportedPlatformError",
    "build_open_folder_command",
    "build_open_path_command",
    "build_reveal_in_folder_command",
    "get_app_data_dir",
    "get_cache_dir",
    "get_config_dir",
    "get_documents_dir",
    "get_executable_suffix",
    "get_home_dir",
    "get_logs_dir",
    "get_platform_name",
    "build_portable_path_variables",
    "get_script_suffix",
    "get_temp_dir",
    "is_hidden",
    "is_linux",
    "is_supported_platform",
    "is_symlink_or_reparse",
    "is_windows",
    "normalize_path",
    "normalize_tool_name",
    "resolve_portable_path",
    "resolve_portable_paths",
    "open_folder",
    "open_path",
    "path_to_display",
    "reveal_in_folder",
]
