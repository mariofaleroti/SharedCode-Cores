from __future__ import annotations

from typing import Any

from ..document import ReportDocument, ReportTable
from ..options import RenderOptions
from ..paths import ensure_parent
from ..result import RenderResult
from ..utils import default_output_path, render_value


LINE_WIDTH = 88


def render_txt(document: ReportDocument, options: RenderOptions) -> RenderResult:
    output_path = options.output_path or default_output_path(options.input_path, "txt", options.output_dir)
    output_path = output_path.expanduser().resolve()
    ensure_parent(output_path)

    if document.report_type == "disk_smart":
        lines = _render_disk_smart_txt(document)
    else:
        lines = _render_generic_txt(document)

    output_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    return RenderResult(ok=True, format="txt", output_path=output_path, message="TXT report generated.")


def _render_disk_smart_txt(document: ReportDocument) -> list[str]:
    meta = document.meta
    summary = document.summary
    data = document.data
    disks = data.get("disks", []) if isinstance(data.get("disks"), list) else []

    lines: list[str] = []
    _append_header(lines, document.title or "Informe SMART de discos", document.subtitle)
    _append_kv_block(
        lines,
        "Contexto",
        [
            ("Herramienta", meta.get("tool_name")),
            ("Equipo", meta.get("computer_name")),
            ("Usuario", meta.get("user_name")),
            ("Generado", _generated_at(document)),
            ("Origen", meta.get("source")),
            ("Estado general", document.status.upper()),
        ],
    )

    _append_kv_block(
        lines,
        "Resumen ejecutivo",
        [
            ("Discos analizados", summary.get("disk_count")),
            ("Entradas detectadas", summary.get("detected_entry_count")),
            ("Duplicados removidos", summary.get("duplicated_entries_removed")),
            ("Discos OK", summary.get("ok_count")),
            ("Advertencias", summary.get("warnings_count")),
            ("Críticos", summary.get("critical_count")),
            ("Temperatura máxima", _format_temp(summary.get("max_temperature_c"))),
            ("smartctl disponible", _yes_no(summary.get("smartctl_available"))),
        ],
    )

    brief = document.report_brief
    _append_brief(lines, brief)

    lines.append(_section_title("Discos"))
    if not disks:
        lines.append("- No hay discos informados en data.disks.")
        lines.append("")
    else:
        for index, disk in enumerate(disks, start=1):
            if not isinstance(disk, dict):
                continue
            life = disk.get("life") if isinstance(disk.get("life"), dict) else {}
            status = str(disk.get("evaluation_status") or "INFO").upper()
            lines.append(f"[{status}] Disco {index}: {render_value(disk.get('model') or 'Sin modelo')}")
            details = [
                ("Dispositivo", disk.get("smart_device")),
                ("Tipo", disk.get("storage_family") or disk.get("detected_type")),
                ("Serial", disk.get("serial")),
                ("Firmware", disk.get("firmware")),
                ("Temperatura", _format_temp(disk.get("temperature_c"))),
                ("Horas encendido", disk.get("power_on_hours")),
                ("Vida usada", _format_percent(life.get("used_percent"))),
                ("Vida restante", _format_percent(life.get("remaining_percent"))),
                ("SMART global", "PASS" if disk.get("smart_global_passed") is True else "NO PASS" if disk.get("smart_global_passed") is False else None),
                ("Nivel de datos", disk.get("data_level")),
                ("Deduplicado", _yes_no(disk.get("deduplicated"))),
            ]
            for key, value in details:
                if value not in (None, ""):
                    lines.append(f"  - {key}: {render_value(value)}")
            reasons = disk.get("evaluation_reasons") if isinstance(disk.get("evaluation_reasons"), list) else []
            if reasons:
                lines.append("  - Motivos:")
                for reason in reasons:
                    lines.append(f"      · {render_value(reason)}")
            flagged = disk.get("flagged_items") if isinstance(disk.get("flagged_items"), list) else []
            if flagged:
                lines.append("  - Elementos marcados:")
                for item in flagged:
                    lines.append(f"      · {render_value(item)}")
            lines.append("")

    _append_technical_table_summary(lines, document.tables)
    _append_diagnostics_and_errors(lines, document)
    _append_footer(lines)
    return lines


def _render_generic_txt(document: ReportDocument) -> list[str]:
    lines: list[str] = []
    _append_header(lines, document.title, document.subtitle)
    _append_kv_block(
        lines,
        "Contexto",
        [
            ("Tipo", document.report_type),
            ("Herramienta", document.meta.get("tool_name")),
            ("Módulo", document.meta.get("module_name")),
            ("Generado/actualizado", _generated_at(document)),
            ("Estado", document.status.upper()),
        ],
    )

    if document.summary:
        _append_kv_block(lines, "Resumen", list(document.summary.items()))

    _append_brief(lines, document.report_brief)
    _append_technical_table_summary(lines, document.tables)
    _append_diagnostics_and_errors(lines, document)
    _append_footer(lines)
    return lines


def _append_header(lines: list[str], title: str, subtitle: str | None = None) -> None:
    clean_title = (title or "Reporte").strip()
    lines.append(clean_title.upper())
    lines.append("=" * min(max(len(clean_title), 12), LINE_WIDTH))
    if subtitle:
        lines.extend(_wrap_text(str(subtitle), prefix=""))
    lines.append("")


def _append_brief(lines: list[str], brief: dict[str, Any]) -> None:
    if not brief:
        return
    findings = brief.get("findings") if isinstance(brief.get("findings"), list) else []
    recommendations = brief.get("recommendations") if isinstance(brief.get("recommendations"), list) else []
    technician_notes = brief.get("technician_notes") if isinstance(brief.get("technician_notes"), list) else []

    if findings or recommendations or technician_notes:
        lines.append(_section_title("Lectura rápida"))
        _append_list(lines, "Hallazgos", findings)
        _append_list(lines, "Recomendaciones", recommendations)
        _append_list(lines, "Notas técnicas", technician_notes)
        lines.append("")


def _append_kv_block(lines: list[str], title: str, items: list[tuple[str, Any]]) -> None:
    visible = [(str(key), value) for key, value in items if value not in (None, "", [], {})]
    if not visible:
        return
    lines.append(_section_title(title))
    width = min(max(len(key) for key, _ in visible), 28)
    for key, value in visible:
        rendered = render_value(value)
        wrapped = _wrap_text(rendered, prefix="" * 0, width=LINE_WIDTH - width - 5)
        if not wrapped:
            lines.append(f"{key:<{width}} :")
        else:
            lines.append(f"{key:<{width}} : {wrapped[0]}")
            for extra in wrapped[1:]:
                lines.append(f"{'':<{width}}   {extra}")
    lines.append("")


def _append_list(lines: list[str], title: str, items: list[Any]) -> None:
    if not items:
        return
    lines.append(f"{title}:")
    for item in items:
        for idx, chunk in enumerate(_wrap_text(render_value(item), width=LINE_WIDTH - 4)):
            bullet = "- " if idx == 0 else "  "
            lines.append(f"  {bullet}{chunk}")


def _append_technical_table_summary(lines: list[str], tables: list[ReportTable]) -> None:
    if not tables:
        return
    lines.append(_section_title("Datos técnicos exportados"))
    for table in tables:
        lines.append(f"- {table.title}: {len(table.rows)} filas, {len(table.columns)} columnas ({table.name}.csv)")
    lines.append("- El detalle completo de atributos y métricas técnicas está en CSV/XLSX.")
    lines.append("")


def _append_diagnostics_and_errors(lines: list[str], document: ReportDocument) -> None:
    if document.diagnostics:
        lines.append(_section_title("Diagnósticos"))
        for item in document.diagnostics:
            lines.append(f"- {render_value(item)}")
        lines.append("")

    if document.errors:
        lines.append(_section_title("Errores"))
        for item in document.errors:
            lines.append(f"- {render_value(item)}")
        lines.append("")


def _append_footer(lines: list[str]) -> None:
    lines.append("-" * 72)
    lines.append("Reporte generado por RenderCore. El contrato JSON fue validado por JsonContractCore.")


def _section_title(value: str) -> str:
    return f"{value}\n" + "-" * len(value)


def _generated_at(document: ReportDocument) -> Any:
    return document.meta.get("generated_at") or document.meta.get("updated_at") or document.meta.get("created_at")


def _format_temp(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return f"{value} °C"


def _format_percent(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return f"{value}%"


def _yes_no(value: Any) -> str | None:
    if value is True:
        return "Sí"
    if value is False:
        return "No"
    return None if value in (None, "") else render_value(value)


def _wrap_text(value: str, *, prefix: str = "", width: int = LINE_WIDTH) -> list[str]:
    text = str(value or "").strip()
    if not text:
        return []
    width = max(width, 30)
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= width:
            current = candidate
        else:
            if current:
                lines.append(prefix + current)
            current = word
    if current:
        lines.append(prefix + current)
    return lines
