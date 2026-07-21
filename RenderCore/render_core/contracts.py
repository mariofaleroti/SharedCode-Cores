from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .document import ReportDocument, ReportSection, ReportTable
from .normalizers import extract_profile_tables
from .exceptions import ContractValidationError

REQUIRED_KEYS = ("meta", "summary", "report_brief", "data", "diagnostics", "errors")
REQUIRED_META_KEYS = ("schema_version", "tool_name")


def load_report_json(input_path: str | Path) -> dict[str, Any]:
    path = Path(input_path).expanduser().resolve()
    with path.open("r", encoding="utf-8-sig") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ContractValidationError("The report JSON root must be an object/dictionary.")

    return data


def validate_report_contract(report_data: dict[str, Any]) -> None:
    """Assert RenderCore's required input shape after JsonContractCore validation.

    JsonContractCore is the authority for the ecosystem contract. This function is
    only a defensive boundary inside RenderCore: it does not complete missing
    fields, does not downgrade the contract and does not provide legacy fallback.
    """

    missing = [key for key in REQUIRED_KEYS if key not in report_data]
    if missing:
        raise ContractValidationError(f"Missing required contract keys: {', '.join(missing)}")

    if not isinstance(report_data["meta"], dict):
        raise ContractValidationError("meta must be an object/dictionary.")
    if not isinstance(report_data["summary"], dict):
        raise ContractValidationError("summary must be an object/dictionary.")
    if not isinstance(report_data["report_brief"], dict):
        raise ContractValidationError("report_brief must be an object/dictionary.")
    if not isinstance(report_data["data"], dict):
        raise ContractValidationError("data must be an object/dictionary.")
    if not isinstance(report_data["diagnostics"], list):
        raise ContractValidationError("diagnostics must be a list/array.")
    if not isinstance(report_data["errors"], list):
        raise ContractValidationError("errors must be a list/array.")

    missing_meta = [key for key in REQUIRED_META_KEYS if not report_data["meta"].get(key)]
    if missing_meta:
        raise ContractValidationError(f"Missing required meta values: {', '.join(missing_meta)}")

    document_kind = (
        report_data["meta"].get("report_type")
        or report_data["meta"].get("config_type")
        or report_data["meta"].get("file_type")
    )
    if not document_kind:
        raise ContractValidationError("meta must define report_type, config_type or file_type.")


def normalize_report_contract(report_data: dict[str, Any]) -> dict[str, Any]:
    """Return a safe copy of a validated contract without repairing invalid input."""

    validate_report_contract(report_data)
    return {
        "meta": dict(report_data["meta"]),
        "summary": dict(report_data["summary"]),
        "report_brief": dict(report_data["report_brief"]),
        "data": dict(report_data["data"]),
        "diagnostics": list(report_data["diagnostics"]),
        "errors": list(report_data["errors"]),
        **{key: value for key, value in report_data.items() if key not in REQUIRED_KEYS},
    }


def build_report_document(report_data: dict[str, Any]) -> ReportDocument:
    normalized = normalize_report_contract(report_data)
    meta = normalized["meta"]
    summary = normalized["summary"]
    brief = normalized["report_brief"]
    data = normalized["data"]

    report_type = str(
        meta.get("report_type")
        or meta.get("config_type")
        or meta.get("file_type")
        or "json_document"
    ).strip().lower()
    tool_name = str(meta["tool_name"]).strip()
    title = str(brief.get("title") or meta.get("title") or f"Informe {tool_name}")
    subtitle = str(
        brief.get("subtitle")
        or brief.get("description")
        or meta.get("description")
        or "Reporte generado desde contrato JSON estandar."
    )
    status = str(
        brief.get("status")
        or summary.get("status")
        or summary.get("health")
        or summary.get("reliability")
        or "info"
    ).strip().lower()

    sections = [
        ReportSection(name="summary", title="Resumen", content=summary),
        ReportSection(name="data", title="Datos", content=data),
        ReportSection(name="diagnostics", title="Diagnosticos", content=normalized["diagnostics"]),
        ReportSection(name="errors", title="Errores", content=normalized["errors"]),
    ]

    tables = extract_tables(normalized)

    return ReportDocument(
        report_type=report_type,
        title=title,
        subtitle=subtitle,
        status=status,
        meta=meta,
        summary=summary,
        report_brief=brief,
        data=data,
        diagnostics=normalized["diagnostics"],
        errors=normalized["errors"],
        sections=sections,
        tables=tables,
        raw=normalized,
    )


def extract_tables(report_data: dict[str, Any]) -> list[ReportTable]:
    profile_tables = extract_profile_tables(report_data)
    if profile_tables:
        tables = list(profile_tables)
        diagnostics = report_data.get("diagnostics", [])
        if diagnostics and all(isinstance(item, dict) for item in diagnostics):
            columns = _collect_columns(diagnostics)
            rows = [{column: row.get(column, "") for column in columns} for row in diagnostics]
            tables.append(ReportTable("diagnostics", "Diagnosticos", columns, rows, "diagnostics"))

        errors = report_data.get("errors", [])
        if errors and all(isinstance(item, dict) for item in errors):
            columns = _collect_columns(errors)
            rows = [{column: row.get(column, "") for column in columns} for row in errors]
            tables.append(ReportTable("errors", "Errores", columns, rows, "errors"))
        return tables

    tables: list[ReportTable] = []

    def visit(value: Any, path: list[str]) -> None:
        if (
            isinstance(value, dict)
            and value
            and all(isinstance(item, dict) for item in value.values())
            and any(any(not isinstance(child_value, dict) for child_value in item.values()) for item in value.values())
        ):
            name = "_".join(path) if path else "items"
            key_name = _singular_key(path[-1] if path else "item")
            rows_source = []
            for item_key, item_value in value.items():
                rows_source.append({key_name: item_key, **item_value})
            title = _human_title(path[-1] if path else "items")
            columns = _collect_columns(rows_source)
            rows = [{column: row.get(column, "") for column in columns} for row in rows_source]
            tables.append(
                ReportTable(
                    name=_safe_name(name),
                    title=title,
                    columns=columns,
                    rows=rows,
                    source_path=".".join(path),
                )
            )
            return

        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value):
                name = "_".join(path) if path else "items"
                title = _human_title(path[-1] if path else "items")
                columns = _collect_columns(value)
                rows = [{column: row.get(column, "") for column in columns} for row in value]
                tables.append(
                    ReportTable(
                        name=_safe_name(name),
                        title=title,
                        columns=columns,
                        rows=rows,
                        source_path=".".join(path),
                    )
                )
            else:
                for index, item in enumerate(value):
                    visit(item, [*path, str(index)])
        elif isinstance(value, dict):
            for key, child in value.items():
                visit(child, [*path, str(key)])

    visit(report_data.get("data", {}), ["data"])

    diagnostics = report_data.get("diagnostics", [])
    if diagnostics and all(isinstance(item, dict) for item in diagnostics):
        columns = _collect_columns(diagnostics)
        rows = [{column: row.get(column, "") for column in columns} for row in diagnostics]
        tables.append(ReportTable("diagnostics", "Diagnosticos", columns, rows, "diagnostics"))

    errors = report_data.get("errors", [])
    if errors and all(isinstance(item, dict) for item in errors):
        columns = _collect_columns(errors)
        rows = [{column: row.get(column, "") for column in columns} for row in errors]
        tables.append(ReportTable("errors", "Errores", columns, rows, "errors"))

    if not tables:
        summary = report_data.get("summary", {})
        rows = [{"key": key, "value": value} for key, value in summary.items()]
        if rows:
            tables.append(ReportTable("summary", "Resumen", ["key", "value"], rows, "summary"))

    return tables


def _collect_columns(rows: list[dict[str, Any]], *, sample_size: int = 50) -> list[str]:
    columns: list[str] = []
    for row in rows[:sample_size]:
        for key in row.keys():
            key_text = str(key)
            if key_text not in columns:
                columns.append(key_text)
    return columns


def _safe_name(value: str) -> str:
    allowed = []
    for char in value.lower().strip():
        if char.isalnum():
            allowed.append(char)
        elif char in ("_", "-", " ", "."):
            allowed.append("_")
    safe = "".join(allowed).strip("_")
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe or "table"


def _human_title(value: str) -> str:
    return value.replace("_", " ").replace("-", " ").strip().title() or "Datos"


def _singular_key(value: str) -> str:
    cleaned = _safe_name(value)
    if cleaned.endswith("ies"):
        return f"{cleaned[:-3]}y"
    if cleaned.endswith("s") and len(cleaned) > 1:
        return cleaned[:-1]
    return cleaned or "item"
