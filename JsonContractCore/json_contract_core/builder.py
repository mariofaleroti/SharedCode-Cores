"""Builders for ecosystem JSON contracts."""

from __future__ import annotations

from typing import Any

from .constants import DEFAULT_SCHEMA_VERSION


def create_contract(
    *,
    file_type: str,
    data: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    report_brief: dict[str, Any] | None = None,
    diagnostics: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    tool_name: str | None = None,
    module_name: str | None = None,
    subtype_key: str | None = None,
    subtype_value: str | None = None,
    extra_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standard JSON contract dictionary.

    DESIGN: This helper creates the shared envelope only. Tool-specific content
    belongs inside `data`, `summary`, `report_brief`, `diagnostics`, or `errors`.
    """
    meta: dict[str, Any] = {
        "schema_version": schema_version,
        "file_type": file_type,
    }

    if subtype_key and subtype_value:
        meta[subtype_key] = subtype_value

    if tool_name:
        meta["tool_name"] = tool_name

    if module_name:
        meta["module_name"] = module_name

    if extra_meta:
        meta.update(extra_meta)

    return {
        "meta": meta,
        "summary": dict(summary or {}),
        "report_brief": dict(report_brief or {}),
        "data": dict(data or {}),
        "diagnostics": list(diagnostics or []),
        "errors": list(errors or []),
    }


def create_result_contract(
    *,
    result_type: str,
    data: dict[str, Any] | None = None,
    summary: dict[str, Any] | None = None,
    report_brief: dict[str, Any] | None = None,
    diagnostics: list[dict[str, Any]] | None = None,
    errors: list[dict[str, Any]] | None = None,
    tool_name: str | None = None,
    module_name: str | None = None,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    extra_meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standard result contract."""
    return create_contract(
        file_type="result",
        subtype_key="result_type",
        subtype_value=result_type,
        data=data,
        summary=summary,
        report_brief=report_brief,
        diagnostics=diagnostics,
        errors=errors,
        tool_name=tool_name,
        module_name=module_name,
        schema_version=schema_version,
        extra_meta=extra_meta,
    )


def create_error_entry(
    code: str,
    message: str,
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standard error entry for the contract errors list."""
    payload: dict[str, Any] = {
        "code": code,
        "message": message,
    }

    if context:
        payload["context"] = context

    return payload


def create_diagnostic_entry(
    level: str,
    code: str,
    message: str,
    *,
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a standard diagnostic entry for the contract diagnostics list."""
    payload: dict[str, Any] = {
        "level": level,
        "code": code,
        "message": message,
    }

    if context:
        payload["context"] = context

    return payload
