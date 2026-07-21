"""Configuration merge helpers."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict


def deep_merge(defaults: Dict[str, Any] | None, overrides: Dict[str, Any] | None) -> Dict[str, Any]:
    """Merge overrides into defaults without mutating either input.

    DESIGN: Dictionaries are merged recursively. Lists and scalar values are
    replaced by the explicit override because list-merge semantics are
    tool-specific and should not be guessed by ConfigCore.
    """
    if defaults is None:
        return deepcopy(overrides or {})

    merged = deepcopy(defaults)

    if not overrides:
        return merged

    for key, override_value in overrides.items():
        default_value = merged.get(key)
        if isinstance(default_value, dict) and isinstance(override_value, dict):
            merged[key] = deep_merge(default_value, override_value)
        else:
            merged[key] = deepcopy(override_value)

    return merged
