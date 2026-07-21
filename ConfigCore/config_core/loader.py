"""Configuration loading functions."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, Mapping, Tuple

from .merger import deep_merge
from .models import ConfigLoadResult
from .validator import ExpectedType, validate_config_data

ContractValidator = Callable[[Any], Any]


def load_json_file(file_path: str | Path) -> Tuple[Any | None, str | None]:
    """Load JSON using UTF-8 with BOM tolerance."""
    path = Path(file_path)

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file), None
    except json.JSONDecodeError as error:
        return None, f"Invalid JSON: {error}"
    except OSError as error:
        return None, f"Unable to read file: {error}"


def _import_json_contract_validator() -> ContractValidator | None:
    try:
        from json_contract_core import validate_contract  # type: ignore
    except ImportError:
        return None
    return validate_contract


def _apply_contract_validation(
    raw_content: Any,
    result: ConfigLoadResult,
    *,
    contract_validator: ContractValidator | None,
    require_contract_validator: bool,
) -> None:
    validator = contract_validator or _import_json_contract_validator()

    if validator is None:
        message = "JsonContractCore validator is not available in the current Python path."
        if require_contract_validator:
            result.add_error(
                "JSON_CONTRACT_CORE_UNAVAILABLE",
                message,
            )
        else:
            result.add_warning(
                "JSON_CONTRACT_CORE_UNAVAILABLE",
                message,
            )
        return

    validation = validator(raw_content)
    is_valid = bool(getattr(validation, "is_valid", False))

    if is_valid:
        return

    for issue in getattr(validation, "errors", []):
        result.add_error(
            getattr(issue, "code", "CONTRACT_VALIDATION_ERROR"),
            getattr(issue, "message", "The JSON contract is invalid."),
            path=getattr(issue, "path", None),
            context=getattr(issue, "context", {}) or {},
        )

    for issue in getattr(validation, "diagnostics", []):
        result.add_warning(
            getattr(issue, "code", "CONTRACT_VALIDATION_WARNING"),
            getattr(issue, "message", "The JSON contract has a diagnostic."),
            path=getattr(issue, "path", None),
            context=getattr(issue, "context", {}) or {},
        )


def _extract_config_data(raw_content: Any, result: ConfigLoadResult, *, contract_mode: bool) -> Dict[str, Any]:
    if not isinstance(raw_content, dict):
        result.add_error(
            "CONFIG_ROOT_NOT_OBJECT",
            "Configuration file root must be a JSON object.",
        )
        return {}

    if not contract_mode:
        return raw_content

    data = raw_content.get("data")
    if not isinstance(data, dict):
        result.add_error(
            "CONFIG_DATA_NOT_OBJECT",
            "Standard configuration contract must contain data as a JSON object.",
            path="data",
        )
        return {}

    return data


def load_config(
    config_path: str | Path,
    *,
    defaults: Dict[str, Any] | None = None,
    required_paths: Iterable[str] | None = None,
    type_rules: Mapping[str, ExpectedType] | None = None,
    allowed_values: Mapping[str, Iterable[Any]] | None = None,
    contract_mode: bool = True,
    validate_standard_contract: bool = True,
    require_contract_validator: bool = False,
    contract_validator: ContractValidator | None = None,
) -> ConfigLoadResult:
    """Load a configuration file and apply generic validation.

    DESIGN: In contract mode, JsonContractCore validates the envelope while
    ConfigCore validates the configuration data inside the data object.
    """
    path = Path(config_path)
    result = ConfigLoadResult.from_path(path)

    if not path.exists():
        result.add_error(
            "CONFIG_FILE_NOT_FOUND",
            "Configuration file does not exist.",
            context={"path": str(path)},
        )
        return result

    if not path.is_file():
        result.add_error(
            "CONFIG_PATH_NOT_FILE",
            "Configuration path must point to a file.",
            context={"path": str(path)},
        )
        return result

    raw_content, load_error = load_json_file(path)
    result.raw_content = raw_content

    if load_error:
        result.add_error(
            "CONFIG_JSON_LOAD_ERROR",
            load_error,
            context={"path": str(path)},
        )
        return result

    if contract_mode and validate_standard_contract:
        _apply_contract_validation(
            raw_content,
            result,
            contract_validator=contract_validator,
            require_contract_validator=require_contract_validator,
        )

    config_data = _extract_config_data(raw_content, result, contract_mode=contract_mode)
    result.config = deep_merge(defaults, config_data)

    validation = validate_config_data(
        result.config,
        required_paths=required_paths,
        type_rules=type_rules,
        allowed_values=allowed_values,
    )
    result.extend_validation(validation)

    return result
