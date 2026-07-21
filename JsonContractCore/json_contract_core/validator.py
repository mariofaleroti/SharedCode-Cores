"""Validation helpers for ecosystem JSON contracts."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .constants import (
    ALLOWED_FILE_TYPES,
    DEFAULT_SCHEMA_VERSION,
    RECOMMENDED_SUBTYPE_KEY_BY_FILE_TYPE,
    REQUIRED_ROOT_KEYS,
    REQUIRED_ROOT_LIST_KEYS,
    REQUIRED_ROOT_OBJECT_KEYS,
)
from .models import ValidationResult


def validate_contract(
    contract: Any,
    *,
    source: str = "<memory>",
    expected_schema_version: str = DEFAULT_SCHEMA_VERSION,
    strict_schema_version: bool = False,
    allow_extra_root_keys: bool = False,
) -> ValidationResult:
    """Validate a JSON contract object and return structured issues.

    DESIGN: This validator checks the shared contract shape only. It does not
    validate tool-specific payloads inside the `data` object.
    """
    result = ValidationResult(source=source)

    if not isinstance(contract, Mapping):
        result.add_error(
            "ROOT_NOT_OBJECT",
            "The JSON root must be an object.",
            path="$",
        )
        return result

    _validate_root_keys(contract, result, allow_extra_root_keys=allow_extra_root_keys)
    _validate_meta(contract, result, expected_schema_version, strict_schema_version)
    _validate_summary(contract, result)
    _validate_report_brief(contract, result)
    _validate_diagnostics(contract, result)
    _validate_errors(contract, result)

    return result


def _validate_root_keys(
    contract: Mapping[str, Any],
    result: ValidationResult,
    *,
    allow_extra_root_keys: bool,
) -> None:
    for key in sorted(REQUIRED_ROOT_KEYS):
        if key not in contract:
            result.add_error(
                "ROOT_REQUIRED_KEY_MISSING",
                f"Required root key is missing: {key}.",
                path="$." + key,
                context={"key": key},
            )

    for key in sorted(REQUIRED_ROOT_OBJECT_KEYS):
        if key in contract and not isinstance(contract[key], Mapping):
            result.add_error(
                "ROOT_KEY_INVALID_TYPE",
                f"Root key must be an object: {key}.",
                path="$." + key,
                context={"key": key, "expected_type": "object"},
            )

    for key in sorted(REQUIRED_ROOT_LIST_KEYS):
        if key in contract and not isinstance(contract[key], list):
            result.add_error(
                "ROOT_KEY_INVALID_TYPE",
                f"Root key must be a list: {key}.",
                path="$." + key,
                context={"key": key, "expected_type": "list"},
            )

    extra_keys = sorted(set(contract.keys()) - REQUIRED_ROOT_KEYS)
    if extra_keys and not allow_extra_root_keys:
        result.add_warning(
            "ROOT_EXTRA_KEYS",
            "Extra root keys should be moved under data.",
            path="$",
            context={"extra_keys": extra_keys},
        )


def _validate_meta(
    contract: Mapping[str, Any],
    result: ValidationResult,
    expected_schema_version: str,
    strict_schema_version: bool,
) -> None:
    meta = contract.get("meta")
    if not isinstance(meta, Mapping):
        return

    schema_version = meta.get("schema_version")
    if schema_version is None:
        result.add_error(
            "META_SCHEMA_VERSION_MISSING",
            "meta.schema_version is required.",
            path="$.meta.schema_version",
        )
    elif schema_version != expected_schema_version:
        add_issue = result.add_error if strict_schema_version else result.add_warning
        add_issue(
            "META_SCHEMA_VERSION_UNEXPECTED",
            "meta.schema_version does not match the expected schema version.",
            path="$.meta.schema_version",
            context={
                "expected": expected_schema_version,
                "actual": schema_version,
            },
        )

    file_type = meta.get("file_type")
    if file_type is None:
        result.add_error(
            "META_FILE_TYPE_MISSING",
            "meta.file_type is required.",
            path="$.meta.file_type",
        )
    elif file_type not in ALLOWED_FILE_TYPES:
        result.add_warning(
            "META_FILE_TYPE_UNKNOWN",
            "meta.file_type is not in the known file type list.",
            path="$.meta.file_type",
            context={
                "allowed_values": sorted(ALLOWED_FILE_TYPES),
                "actual": file_type,
            },
        )

    if file_type in RECOMMENDED_SUBTYPE_KEY_BY_FILE_TYPE:
        subtype_key = RECOMMENDED_SUBTYPE_KEY_BY_FILE_TYPE[file_type]
        if subtype_key not in meta:
            result.add_warning(
                "META_RECOMMENDED_SUBTYPE_MISSING",
                f"meta.{subtype_key} is recommended for file_type={file_type}.",
                path="$.meta." + subtype_key,
                context={"file_type": file_type, "subtype_key": subtype_key},
            )

    if "tool_name" not in meta:
        result.add_warning(
            "META_TOOL_NAME_MISSING",
            "meta.tool_name is recommended.",
            path="$.meta.tool_name",
        )

    if "module_name" not in meta:
        result.add_warning(
            "META_MODULE_NAME_MISSING",
            "meta.module_name is recommended.",
            path="$.meta.module_name",
        )


def _validate_summary(contract: Mapping[str, Any], result: ValidationResult) -> None:
    summary = contract.get("summary")
    if not isinstance(summary, Mapping):
        return

    for key in ("status", "errors_count", "diagnostics_count"):
        if key not in summary:
            result.add_warning(
                "SUMMARY_RECOMMENDED_KEY_MISSING",
                f"summary.{key} is recommended.",
                path="$.summary." + key,
                context={"key": key},
            )


def _validate_report_brief(contract: Mapping[str, Any], result: ValidationResult) -> None:
    report_brief = contract.get("report_brief")
    if not isinstance(report_brief, Mapping):
        return

    # NOTE: Empty report_brief is valid when the producer has no display summary.
    if not report_brief:
        return

    for key in ("title", "description"):
        if key not in report_brief:
            result.add_warning(
                "REPORT_BRIEF_RECOMMENDED_KEY_MISSING",
                f"report_brief.{key} is recommended when report_brief is not empty.",
                path="$.report_brief." + key,
                context={"key": key},
            )


def _validate_diagnostics(contract: Mapping[str, Any], result: ValidationResult) -> None:
    diagnostics = contract.get("diagnostics")
    if not isinstance(diagnostics, list):
        return

    for index, item in enumerate(diagnostics):
        item_path = f"$.diagnostics[{index}]"
        if not isinstance(item, Mapping):
            result.add_error(
                "DIAGNOSTIC_ITEM_INVALID_TYPE",
                "Each diagnostics item must be an object.",
                path=item_path,
                context={"index": index},
            )
            continue

        for key in ("level", "code", "message"):
            if key not in item:
                result.add_warning(
                    "DIAGNOSTIC_ITEM_RECOMMENDED_KEY_MISSING",
                    f"diagnostics[{index}].{key} is recommended.",
                    path=f"{item_path}.{key}",
                    context={"index": index, "key": key},
                )


def _validate_errors(contract: Mapping[str, Any], result: ValidationResult) -> None:
    errors = contract.get("errors")
    if not isinstance(errors, list):
        return

    for index, item in enumerate(errors):
        item_path = f"$.errors[{index}]"
        if not isinstance(item, Mapping):
            result.add_error(
                "ERROR_ITEM_INVALID_TYPE",
                "Each errors item must be an object.",
                path=item_path,
                context={"index": index},
            )
            continue

        for key in ("code", "message"):
            if key not in item:
                result.add_warning(
                    "ERROR_ITEM_RECOMMENDED_KEY_MISSING",
                    f"errors[{index}].{key} is recommended.",
                    path=f"{item_path}.{key}",
                    context={"index": index, "key": key},
                )
