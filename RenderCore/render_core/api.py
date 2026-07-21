from __future__ import annotations

from pathlib import Path
from typing import Iterable

from .contracts import build_report_document, load_report_json
from .formats.csv_renderer import render_csv
from .formats.html_renderer import render_html
from .formats.txt_renderer import render_txt
from .formats.xlsx_renderer import render_xlsx
from .options import RenderOptions
from .validation import validate_contract
from .registry import FormatRegistry
from .result import RenderResult


def resolve_contract_profile(report_data: dict, requested_profile: str | None = "auto") -> str:
    """Resolve the JsonContractCore profile without weakening validation.

    `auto` does not mean permissive validation. It only selects the strict
    profile that matches the document kind declared in meta.
    """

    requested = (requested_profile or "auto").strip().lower()
    if requested and requested != "auto":
        return requested

    meta = report_data.get("meta") if isinstance(report_data, dict) else {}
    if not isinstance(meta, dict):
        return "tool_report"

    config_type = str(meta.get("config_type") or "").strip().lower()
    file_type = str(meta.get("file_type") or "").strip().lower()
    report_type = str(meta.get("report_type") or "").strip().lower()

    if config_type:
        return config_type
    if file_type == "config":
        return "config"
    if report_type:
        return "tool_report"
    return "standard_json"


def create_default_registry() -> FormatRegistry:
    registry = FormatRegistry()
    registry.register("html", render_html)
    registry.register("txt", render_txt)
    registry.register("csv", render_csv)
    registry.register("xlsx", render_xlsx)
    return registry


def render_report(
    input_path: str | Path,
    output_path: str | Path | None = None,
    *,
    output_dir: str | Path | None = None,
    output_format: str = "html",
    template_dir: str | Path | None = None,
    profile: str | None = None,
    theme: str = "dark",
    contract_profile: str = "auto",
) -> RenderResult:
    input_resolved = Path(input_path).expanduser().resolve()
    output_resolved = Path(output_path).expanduser().resolve() if output_path else None
    output_dir_resolved = Path(output_dir).expanduser().resolve() if output_dir else None
    template_dir_resolved = Path(template_dir).expanduser().resolve() if template_dir else None

    report_data = load_report_json(input_resolved)
    resolved_contract_profile = resolve_contract_profile(report_data, contract_profile)
    validation_result = validate_contract(
        report_data,
        contract_profile=resolved_contract_profile,
    )
    document = build_report_document(validation_result.data)

    options = RenderOptions(
        input_path=input_resolved,
        output_path=output_resolved,
        output_dir=output_dir_resolved,
        output_format=output_format,
        template_dir=template_dir_resolved,
        profile=profile,
        theme=theme,
        strict=True,
    )

    registry = create_default_registry()
    renderer = registry.get(output_format)
    result = renderer(document, options)
    result.diagnostics.append(
        {"level": "info", "message": f"Contract validator: {validation_result.source}"}
    )
    result.diagnostics.append(
        {"level": "info", "message": f"Contract profile: {resolved_contract_profile}"}
    )
    result.diagnostics.extend(validation_result.diagnostics)
    result.diagnostics.extend({"level": "warning", "message": item} for item in validation_result.warnings)
    return result


def render_report_data(
    report_data: dict,
    output_path: str | Path,
    *,
    output_format: str = "html",
    template_dir: str | Path | None = None,
    profile: str | None = None,
    theme: str = "dark",
    contract_profile: str = "auto",
    input_name: str = "render_data.json",
) -> RenderResult:
    """Render an in-memory strict contract without weakening validation.

    This is useful for tools that build a temporary document view on demand.
    The payload still passes through JsonContractCore and RenderCore's defensive
    contract boundary exactly like :func:`render_report`.
    """

    if not isinstance(report_data, dict):
        raise TypeError("report_data must be a dictionary")

    output_resolved = Path(output_path).expanduser().resolve()
    template_dir_resolved = Path(template_dir).expanduser().resolve() if template_dir else None
    resolved_contract_profile = resolve_contract_profile(report_data, contract_profile)
    validation_result = validate_contract(report_data, contract_profile=resolved_contract_profile)
    document = build_report_document(validation_result.data)

    options = RenderOptions(
        input_path=Path(input_name),
        output_path=output_resolved,
        output_dir=output_resolved.parent,
        output_format=output_format,
        template_dir=template_dir_resolved,
        profile=profile,
        theme=theme,
        strict=True,
    )

    registry = create_default_registry()
    renderer = registry.get(output_format)
    result = renderer(document, options)
    result.diagnostics.append(
        {"level": "info", "message": f"Contract validator: {validation_result.source}"}
    )
    result.diagnostics.append(
        {"level": "info", "message": f"Contract profile: {resolved_contract_profile}"}
    )
    result.diagnostics.extend(validation_result.diagnostics)
    result.diagnostics.extend({"level": "warning", "message": item} for item in validation_result.warnings)
    return result


def render_many(
    input_path: str | Path,
    formats: Iterable[str],
    *,
    output_dir: str | Path | None = None,
    template_dir: str | Path | None = None,
    profile: str | None = None,
    theme: str = "dark",
    contract_profile: str = "auto",
) -> list[RenderResult]:
    results: list[RenderResult] = []
    for output_format in formats:
        output_format = output_format.strip().lower()
        if not output_format:
            continue
        results.append(
            render_report(
                input_path=input_path,
                output_dir=output_dir,
                output_format=output_format,
                template_dir=template_dir,
                profile=profile,
                theme=theme,
                contract_profile=contract_profile,
            )
        )
    return results
