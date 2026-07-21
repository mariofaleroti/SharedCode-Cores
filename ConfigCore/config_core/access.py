"""Helpers for reading nested configuration values."""

from __future__ import annotations

from typing import Any, Iterable, Tuple

_MISSING = object()


def normalize_config_path(path: str | Iterable[str]) -> Tuple[str, ...]:
    """Normalize a dotted configuration path into a tuple of keys."""
    if isinstance(path, str):
        parts = tuple(part for part in path.split(".") if part)
    else:
        parts = tuple(str(part) for part in path if str(part))

    if not parts:
        raise ValueError("Configuration path cannot be empty.")

    return parts


def get_nested_value(data: dict[str, Any], path: str | Iterable[str], default: Any = None) -> Any:
    """Return a nested configuration value or a default when missing."""
    current: Any = data

    for key in normalize_config_path(path):
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]

    return current


def has_nested_key(data: dict[str, Any], path: str | Iterable[str]) -> bool:
    """Return True when a nested key exists."""
    return get_nested_value(data, path, default=_MISSING) is not _MISSING
