"""Validation helpers for tool-specific configuration data."""

from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping, Tuple, Type

from .access import get_nested_value, has_nested_key, normalize_config_path
from .models import ConfigValidationResult

ExpectedType = Type[Any] | Tuple[Type[Any], ...]

_TYPE_NAMES = {
    str: "str",
    int: "int",
    float: "float",
    bool: "bool",
    list: "list",
    dict: "dict",
}


def _expected_type_name(expected_type: ExpectedType) -> str:
    if isinstance(expected_type, tuple):
        return " or ".join(_TYPE_NAMES.get(item, item.__name__) for item in expected_type)
    return _TYPE_NAMES.get(expected_type, expected_type.__name__)


def _is_expected_type(value: Any, expected_type: ExpectedType) -> bool:
    """Return True when value matches expected_type using JSON-safe strictness."""
    expected_types = expected_type if isinstance(expected_type, tuple) else (expected_type,)

    # DESIGN: bool is a subclass of int in Python, but JSON configuration
    # should not accept true/false where a numeric value is expected.
    if int in expected_types and bool not in expected_types and isinstance(value, bool):
        return False

    if float in expected_types and bool not in expected_types and isinstance(value, bool):
        return False

    return isinstance(value, expected_types)


def validate_config_data(
    config: Dict[str, Any],
    *,
    required_paths: Iterable[str] | None = None,
    type_rules: Mapping[str, ExpectedType] | None = None,
    allowed_values: Mapping[str, Iterable[Any]] | None = None,
) -> ConfigValidationResult:
    """Validate tool-specific configuration data.

    NOTE: ConfigCore validates generic structure and simple rules only. Each
    tool remains responsible for business decisions that belong to its domain.
    """
    result = ConfigValidationResult()

    if not isinstance(config, dict):
        result.add_error(
            "CONFIG_NOT_OBJECT",
            "Configuration data must be a JSON object.",
        )
        return result

    for path in required_paths or []:
        normalized_path = ".".join(normalize_config_path(path))
        if not has_nested_key(config, normalized_path):
            result.add_error(
                "CONFIG_REQUIRED_PATH_MISSING",
                "Required configuration path is missing.",
                path=normalized_path,
            )

    for path, expected_type in (type_rules or {}).items():
        normalized_path = ".".join(normalize_config_path(path))
        if not has_nested_key(config, normalized_path):
            continue

        value = get_nested_value(config, normalized_path)
        if not _is_expected_type(value, expected_type):
            result.add_error(
                "CONFIG_INVALID_TYPE",
                f"Configuration value must be {_expected_type_name(expected_type)}.",
                path=normalized_path,
                context={
                    "actual_type": type(value).__name__,
                },
            )

    for path, allowed in (allowed_values or {}).items():
        normalized_path = ".".join(normalize_config_path(path))
        if not has_nested_key(config, normalized_path):
            continue

        allowed_list = list(allowed)
        value = get_nested_value(config, normalized_path)
        if value not in allowed_list:
            result.add_error(
                "CONFIG_VALUE_NOT_ALLOWED",
                "Configuration value is not allowed.",
                path=normalized_path,
                context={
                    "allowed_values": allowed_list,
                    "actual_value": value,
                },
            )

    return result
