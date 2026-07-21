"""Portable path helpers for Windows/Linux tools."""

from __future__ import annotations

import os
import re
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .constants import (
    DEFAULT_XDG_CACHE_HOME,
    DEFAULT_XDG_CONFIG_HOME,
    DEFAULT_XDG_DATA_HOME,
    DEFAULT_XDG_STATE_HOME,
    PLATFORM_LINUX,
    PLATFORM_WINDOWS,
)
from .detection import get_platform_name
from .exceptions import UnsupportedPlatformError

_FORBIDDEN_TOOL_NAME_CHARS = re.compile(r'[\\/:*?"<>|\x00-\x1f]+')
_WHITESPACE = re.compile(r"\s+")
_PORTABLE_TOKEN_PATTERN = re.compile(r"\$\{([A-Za-z0-9_]+)\}")


def normalize_tool_name(tool_name: str) -> str:
    """Return a filesystem-safe application directory name.

    The function keeps friendly names readable while removing path separators and
    characters that are invalid or problematic across Windows/Linux.
    """

    if tool_name is None:
        raise ValueError("tool_name is required")
    normalized = _FORBIDDEN_TOOL_NAME_CHARS.sub("_", str(tool_name)).strip(" ._-")
    normalized = _WHITESPACE.sub(" ", normalized).strip()
    if not normalized:
        raise ValueError("tool_name cannot be empty")
    return normalized


def normalize_path(path: str | os.PathLike[str], *, expand_user: bool = True, resolve: bool = False) -> Path:
    """Convert a path-like value to ``Path`` using safe common defaults."""

    if path is None:
        raise ValueError("path is required")
    result = Path(path)
    if expand_user:
        result = result.expanduser()
    if resolve:
        result = result.resolve(strict=False)
    return result


def path_to_display(path: str | os.PathLike[str]) -> str:
    """Return a user-facing path string without forcing absolute resolution."""

    return str(normalize_path(path, resolve=False))


def resolve_portable_path(
    path: str | os.PathLike[str],
    *,
    base_dir: str | os.PathLike[str] | None = None,
    project_root: str | os.PathLike[str] | None = None,
    config_dir: str | os.PathLike[str] | None = None,
    output_dir: str | os.PathLike[str] | None = None,
    logs_dir: str | os.PathLike[str] | None = None,
    temp_dir: str | os.PathLike[str] | None = None,
    runtime_dir: str | os.PathLike[str] | None = None,
    tool_name: str | None = None,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
    extra_variables: Mapping[str, str | os.PathLike[str]] | None = None,
    resolve: bool = True,
) -> Path:
    """Resolve a configurable path using shared portable tokens.

    Supported built-in tokens use the ``${TOKEN}`` format and are intentionally
    OS-neutral: ``${USER_HOME}``, ``${HOME}``, ``${DOCUMENTS}``,
    ``${BASE_DIR}``, ``${PROJECT_ROOT}``, ``${CONFIG_DIR}``, ``${OUTPUT_DIR}``,
    ``${LOGS_DIR}``, ``${TEMP_DIR}``, ``${RUNTIME_DIR}``, ``${APP_DATA}`` and
    ``${CACHE_DIR}``.

    Relative paths are resolved from ``base_dir`` when provided. When ``base_dir``
    is omitted, they are resolved from the current working directory.
    """

    if path is None:
        raise ValueError("path is required")

    variable_map = build_portable_path_variables(
        base_dir=base_dir,
        project_root=project_root,
        config_dir=config_dir,
        output_dir=output_dir,
        logs_dir=logs_dir,
        temp_dir=temp_dir,
        runtime_dir=runtime_dir,
        tool_name=tool_name,
        platform_name=platform_name,
        env=env,
        home=home,
        extra_variables=extra_variables,
    )

    path_text = str(path)

    def replace_token(match: re.Match[str]) -> str:
        token_name = match.group(1).upper()
        if token_name not in variable_map:
            available = ", ".join(sorted(variable_map))
            raise ValueError(f"Unsupported portable path token: ${{{token_name}}}. Available tokens: {available}")
        return str(variable_map[token_name])

    expanded_text = _PORTABLE_TOKEN_PATTERN.sub(replace_token, path_text)
    expanded_text = os.path.expandvars(expanded_text)
    candidate = Path(expanded_text).expanduser()

    if not candidate.is_absolute():
        root_dir = normalize_path(base_dir, resolve=True) if base_dir is not None else Path.cwd().resolve()
        candidate = root_dir / candidate

    return candidate.resolve(strict=False) if resolve else candidate


def resolve_portable_paths(
    paths: list[str | os.PathLike[str]] | tuple[str | os.PathLike[str], ...],
    **kwargs: Any,
) -> list[Path]:
    """Resolve multiple paths with the same portable-token context."""

    return [resolve_portable_path(path, **kwargs) for path in paths]


def build_portable_path_variables(
    *,
    base_dir: str | os.PathLike[str] | None = None,
    project_root: str | os.PathLike[str] | None = None,
    config_dir: str | os.PathLike[str] | None = None,
    output_dir: str | os.PathLike[str] | None = None,
    logs_dir: str | os.PathLike[str] | None = None,
    temp_dir: str | os.PathLike[str] | None = None,
    runtime_dir: str | os.PathLike[str] | None = None,
    tool_name: str | None = None,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
    extra_variables: Mapping[str, str | os.PathLike[str]] | None = None,
) -> dict[str, Path]:
    """Build the token map used by ``resolve_portable_path``."""

    home_dir = get_home_dir(home=home)
    current_platform = platform_name or get_platform_name()
    variables: dict[str, Path] = {
        "USER_HOME": home_dir,
        "HOME": home_dir,
        "DOCUMENTS": get_documents_dir(platform_name=current_platform, env=env, home=home_dir),
        "CWD": Path.cwd(),
    }

    if base_dir is not None:
        variables["BASE_DIR"] = normalize_path(base_dir, resolve=True)
    if project_root is not None:
        variables["PROJECT_ROOT"] = normalize_path(project_root, resolve=True)
    elif base_dir is not None:
        variables["PROJECT_ROOT"] = normalize_path(base_dir, resolve=True)
    if config_dir is not None:
        variables["CONFIG_DIR"] = normalize_path(config_dir, resolve=True)
    if output_dir is not None:
        variables["OUTPUT_DIR"] = normalize_path(output_dir, resolve=True)
    if logs_dir is not None:
        variables["LOGS_DIR"] = normalize_path(logs_dir, resolve=True)
    if temp_dir is not None:
        variables["TEMP_DIR"] = normalize_path(temp_dir, resolve=True)
    if runtime_dir is not None:
        variables["RUNTIME_DIR"] = normalize_path(runtime_dir, resolve=True)

    if tool_name:
        variables.setdefault("APP_DATA", get_app_data_dir(tool_name, platform_name=current_platform, env=env, home=home_dir))
        variables.setdefault("CONFIG_DIR", get_config_dir(tool_name, platform_name=current_platform, env=env, home=home_dir))
        variables.setdefault("LOGS_DIR", get_logs_dir(tool_name, platform_name=current_platform, env=env, home=home_dir))
        variables.setdefault("CACHE_DIR", get_cache_dir(tool_name, platform_name=current_platform, env=env, home=home_dir))
        variables.setdefault("TEMP_DIR", get_temp_dir(tool_name))

    if extra_variables:
        for key, value in extra_variables.items():
            normalized_key = str(key).strip().upper()
            if not normalized_key:
                continue
            variables[normalized_key] = normalize_path(value, resolve=True)

    return variables


def get_home_dir(*, home: str | os.PathLike[str] | None = None) -> Path:
    """Return the current user's home directory."""

    return normalize_path(home) if home is not None else Path.home()


def _env_path(env: Mapping[str, str] | None, key: str) -> Path | None:
    source = os.environ if env is None else env
    value = source.get(key)
    if not value:
        return None
    return normalize_path(value)


def _home_child(home_dir: Path, relative_path: str) -> Path:
    result = home_dir
    for part in relative_path.replace("\\", "/").split("/"):
        if part:
            result = result / part
    return result


def get_documents_dir(
    *,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the conventional Documents directory for Windows/Linux."""

    current_platform = platform_name or get_platform_name()
    home_dir = get_home_dir(home=home)

    if current_platform == PLATFORM_WINDOWS:
        user_profile = _env_path(env, "USERPROFILE") or home_dir
        return user_profile / "Documents"
    if current_platform == PLATFORM_LINUX:
        # XDG user dirs can be localized, but the neutral fallback is Documents.
        return home_dir / "Documents"
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def get_app_data_dir(
    tool_name: str,
    *,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the main writable application data directory for a tool."""

    current_platform = platform_name or get_platform_name()
    safe_tool_name = normalize_tool_name(tool_name)
    home_dir = get_home_dir(home=home)

    if current_platform == PLATFORM_WINDOWS:
        base = _env_path(env, "LOCALAPPDATA") or _env_path(env, "APPDATA") or (home_dir / "AppData" / "Local")
        return base / safe_tool_name
    if current_platform == PLATFORM_LINUX:
        base = _env_path(env, "XDG_DATA_HOME") or _home_child(home_dir, DEFAULT_XDG_DATA_HOME)
        return base / safe_tool_name
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def get_config_dir(
    tool_name: str,
    *,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the conventional configuration directory for a tool."""

    current_platform = platform_name or get_platform_name()
    safe_tool_name = normalize_tool_name(tool_name)
    home_dir = get_home_dir(home=home)

    if current_platform == PLATFORM_WINDOWS:
        return get_app_data_dir(safe_tool_name, platform_name=current_platform, env=env, home=home) / "config"
    if current_platform == PLATFORM_LINUX:
        base = _env_path(env, "XDG_CONFIG_HOME") or _home_child(home_dir, DEFAULT_XDG_CONFIG_HOME)
        return base / safe_tool_name
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def get_logs_dir(
    tool_name: str,
    *,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the conventional log directory for a tool."""

    current_platform = platform_name or get_platform_name()
    safe_tool_name = normalize_tool_name(tool_name)
    home_dir = get_home_dir(home=home)

    if current_platform == PLATFORM_WINDOWS:
        return get_app_data_dir(safe_tool_name, platform_name=current_platform, env=env, home=home) / "logs"
    if current_platform == PLATFORM_LINUX:
        base = _env_path(env, "XDG_STATE_HOME") or _home_child(home_dir, DEFAULT_XDG_STATE_HOME)
        return base / safe_tool_name / "logs"
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def get_cache_dir(
    tool_name: str,
    *,
    platform_name: str | None = None,
    env: Mapping[str, str] | None = None,
    home: str | os.PathLike[str] | None = None,
) -> Path:
    """Return the conventional cache/temp-storage directory for a tool."""

    current_platform = platform_name or get_platform_name()
    safe_tool_name = normalize_tool_name(tool_name)
    home_dir = get_home_dir(home=home)

    if current_platform == PLATFORM_WINDOWS:
        return get_app_data_dir(safe_tool_name, platform_name=current_platform, env=env, home=home) / "cache"
    if current_platform == PLATFORM_LINUX:
        base = _env_path(env, "XDG_CACHE_HOME") or _home_child(home_dir, DEFAULT_XDG_CACHE_HOME)
        return base / safe_tool_name
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def get_temp_dir(tool_name: str | None = None) -> Path:
    """Return a temp directory, optionally nested by tool name."""

    base = Path(tempfile.gettempdir())
    if not tool_name:
        return base
    return base / normalize_tool_name(tool_name)
