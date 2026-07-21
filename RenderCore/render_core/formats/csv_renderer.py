from __future__ import annotations

import csv
from pathlib import Path

from ..document import ReportDocument, ReportTable
from ..options import RenderOptions
from ..paths import ensure_parent
from ..result import RenderResult
from ..utils import render_value, safe_filename


def render_csv(document: ReportDocument, options: RenderOptions) -> RenderResult:
    base_dir = _resolve_csv_output_dir(document, options)
    base_dir.mkdir(parents=True, exist_ok=True)

    output_paths: list[Path] = []
    tables = list(document.tables or [])

    if not tables:
        tables = [ReportTable("summary", "Resumen", ["key", "value"], _summary_rows(document), "summary")]

    for table in tables:
        filename = f"{safe_filename(table.name, 'table')}.csv"
        output_path = base_dir / filename
        _write_table_csv(output_path, table)
        output_paths.append(output_path)

    summary_path = base_dir / "report_summary.csv"
    _write_summary_csv(summary_path, document)
    if summary_path not in output_paths:
        output_paths.append(summary_path)

    primary = output_paths[0] if output_paths else base_dir
    extras = output_paths[1:] if len(output_paths) > 1 else []

    return RenderResult(
        ok=True,
        format="csv",
        output_path=primary,
        extra_paths=extras,
        message=f"CSV export generated: {len(output_paths)} file(s).",
    )


def _resolve_csv_output_dir(document: ReportDocument, options: RenderOptions) -> Path:
    if options.output_dir:
        return options.output_dir.expanduser().resolve()

    if options.output_path:
        output_path = options.output_path.expanduser().resolve()
        if output_path.suffix.lower() == ".csv" and len(document.tables) <= 1:
            ensure_parent(output_path)
            return output_path.parent
        if output_path.suffix:
            return output_path.with_suffix("")
        return output_path

    return options.input_path.with_name(f"{options.input_path.stem}_csv")


def _write_table_csv(output_path: Path, table: ReportTable) -> None:
    ensure_parent(output_path)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=table.columns, extrasaction="ignore")
        writer.writeheader()
        for row in table.rows:
            writer.writerow({column: render_value(row.get(column, "")) for column in table.columns})


def _write_summary_csv(output_path: Path, document: ReportDocument) -> None:
    table = ReportTable("report_summary", "Resumen del reporte", ["section", "key", "value"], _summary_rows(document), "summary")
    _write_table_csv(output_path, table)


def _summary_rows(document: ReportDocument) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    rows.extend(
        [
            {"section": "document", "key": "title", "value": document.title},
            {"section": "document", "key": "subtitle", "value": document.subtitle},
            {"section": "document", "key": "type", "value": document.report_type},
            {"section": "document", "key": "status", "value": document.status},
        ]
    )
    for key, value in document.meta.items():
        rows.append({"section": "meta", "key": str(key), "value": render_value(value)})
    for key, value in document.summary.items():
        rows.append({"section": "summary", "key": str(key), "value": render_value(value)})
    return rows
