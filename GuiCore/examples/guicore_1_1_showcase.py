from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

try:
    from _bootstrap import ensure_project_root_on_path
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    CardHeaderAction,
    ChoiceOption,
    GuiActionButton,
    GuiAppConfig,
    GuiAppWindow,
    GuiMenuItem,
    KeyValueItem,
    KeyValueTable,
    MetricItem,
    ResultsTable,
    SidebarConfig,
    TableColumn,
    VISUAL_PREFERENCE_MODES,
    normalize_visual_preferences_mode,
)


def build_showcase(
    preference_mode: str = "basic",
) -> tuple[GuiAppWindow, dict[str, Any]]:
    resolved_mode = normalize_visual_preferences_mode(preference_mode)
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore 1.1 Showcase",
            app_subtitle="Contrato visual integrado y neutral",
            app_version="1.1.0.dev7",
            layout_profile="compact",
            visual_preferences=resolved_mode,
            width=1280,
            height=820,
            min_width=1080,
            min_height=700,
            maximize_on_start=False,
            sidebar_width=340,
            sidebar_config=SidebarConfig(
                footer_label_visible=False,
                footer_columns=2,
                primary_action_columns=2,
                scrollbar_width=8,
            ),
            primary_actions=(
                GuiActionButton("Ejecutar", "run", icon_text="▶"),
                GuiActionButton(
                    "Cancelar",
                    "cancel",
                    style="secondary",
                    enabled=False,
                ),
            ),
            footer_items=(
                GuiMenuItem("Configuración", "settings"),
                GuiMenuItem("Ayuda", "help"),
                GuiMenuItem("Acerca de", "about"),
                GuiMenuItem("Salir", "exit"),
            ),
            help_text=(
                "Esta demo reúne perfiles, sidebar, controles, tarjetas, "
                "métricas, tabla, tooltips y tareas en segundo plano."
            ),
            about_text=(
                "Aplicación neutral de integración para el contrato GuiCore 1.1."
            ),
        )
    )

    form = app.add_sidebar_section(
        "Operación",
        "Controles compactos administrados por GuiCore.",
    )
    query = form.add_labeled_entry(
        "Criterio",
        placeholder="Texto de ejemplo...",
        font_role="small",
    )
    mode = form.add_labeled_combo(
        "Modo",
        (
            ChoiceOption("Rápido", "fast"),
            ChoiceOption("Completo", "full"),
        ),
        font_role="small",
    )
    path = form.add_path_picker(
        "Ruta",
        placeholder="Seleccionar carpeta...",
        font_role="small",
        button_width=32,
    )
    category = form.add_labeled_combo_action(
        "Categoría",
        (
            ChoiceOption("Todas", "all"),
            ChoiceOption("Documentos", "documents"),
            ChoiceOption("Datos", "data"),
        ),
        button_text="...",
        button_command=lambda: app.set_status(
            "Acción auxiliar invocada desde LabeledComboAction."
        ),
        font_role="small",
    )
    remember = form.add_switch(
        "Recordar selección",
        default=True,
        font_role="small",
    )
    recursive = form.add_checkbox(
        "Incluir elementos relacionados",
        default=True,
        font_role="small",
    )

    metrics_card = app.add_content_card(
        "Resumen",
        "Las métricas presentan valores; la aplicación define su significado.",
        header_actions=(
            CardHeaderAction(
                "Restablecer",
                command_key="reset_metrics",
                command=lambda: app.set_status(
                    "Las métricas se restablecen desde la aplicación consumidora."
                ),
            ),
        ),
    )
    metrics = app.create_metric_strip(
        metrics_card.content_frame,
        (
            MetricItem(
                "status",
                "Estado",
                "Listo",
                semantic="ready",
                detail="Esperando ejecución",
                tooltip="Estado general de la operación simulada.",
            ),
            MetricItem(
                "processed",
                "Procesados",
                0,
                semantic="info",
                detail="Elementos",
                tooltip="Cantidad acumulada durante la tarea.",
            ),
            MetricItem(
                "warnings",
                "Advertencias",
                0,
                detail="Sin incidencias",
                tooltip="Advertencias generadas por la aplicación demo.",
            ),
            MetricItem(
                "mode",
                "Modo",
                "Rápido",
                detail="Configuración actual",
                tooltip="Valor estable seleccionado en el formulario.",
            ),
        ),
        columns=4,
        tooltip_delay_ms=450,
    )
    metrics.grid(row=0, column=0, sticky="ew")

    results_card = app.add_content_card(
        "Resultados",
        "ResultsTable opera sin filas falsas y sin acceso directo a Tk desde workers.",
        row_weight=3,
        min_height=300,
        sticky="nsew",
    )
    results_card.content_frame.grid_rowconfigure(0, weight=1)
    table = ResultsTable(
        results_card.content_frame,
        columns=(
            TableColumn("index", "#", width=60, anchor="center"),
            TableColumn("name", "Elemento", width=260),
            TableColumn("status", "Estado", width=140),
            TableColumn("detail", "Detalle", width=420),
        ),
        enable_sorting=True,
        enable_tooltips=True,
    )
    table.set_rows(
        (
            {
                "index": 1,
                "name": "Elemento inicial",
                "status": "Listo",
                "detail": "La tabla está preparada para recibir resultados.",
            },
        )
    )
    app.register_results_table(table)

    details_card = app.add_collapsible_card(
        "Detalle de configuración",
        "Vista clave/valor reutilizable.",
        row_weight=1,
        min_height=130,
        sticky="nsew",
        collapsed_summary="Configuración disponible",
    )
    details = KeyValueTable(
        details_card.content_frame,
        (
            KeyValueItem("Preferencias", resolved_mode, "info"),
            KeyValueItem("Perfil", "compact"),
            KeyValueItem("Categoría", "all"),
            KeyValueItem("Recursivo", "Sí", "success"),
        ),
        layout_profile="compact",
    )
    details.grid(row=0, column=0, sticky="nsew")
    app.register_visual_component(details)

    current_runner: dict[str, Any] = {"runner": None}

    def refresh_details() -> None:
        details.set_items(
            (
                KeyValueItem("Preferencias", resolved_mode, "info"),
                KeyValueItem("Perfil", "compact"),
                KeyValueItem("Criterio", query.get_value() or "(vacío)"),
                KeyValueItem("Modo", str(mode.get_value())),
                KeyValueItem("Ruta", path.get_value() or "(sin seleccionar)"),
                KeyValueItem("Categoría", str(category.get_value())),
                KeyValueItem(
                    "Recordar",
                    "Sí" if remember.get_value() else "No",
                ),
                KeyValueItem(
                    "Relacionado",
                    "Sí" if recursive.get_value() else "No",
                ),
            )
        )

    def start_operation() -> None:
        refresh_details()
        app.set_sidebar_action_enabled("run", False)
        app.set_sidebar_action_enabled("cancel", True)
        metrics.update_metric(
            "status",
            value="Ejecutando",
            semantic="info",
            detail="Tarea en segundo plano",
        )
        metrics.update_metric(
            "mode",
            value=mode.get_label(),
        )

        def worker(context):
            rows = []
            for index in range(1, 41):
                context.report_progress(
                    index,
                    40,
                    message=f"Procesando elemento {index} de 40",
                )
                context.sleep(0.035)
                rows.append(
                    {
                        "index": index,
                        "name": f"Elemento {index:02d}",
                        "status": "Correcto" if index % 9 else "Revisar",
                        "detail": "Resultado producido por la tarea simulada.",
                    }
                )
            return rows

        runner = app.start_task(
            worker,
            task_key="showcase_operation",
            name="showcase-operation",
            start_message="Preparando operación integrada...",
            success_message="Operación integrada finalizada",
            cancelled_message="Operación integrada cancelada",
            error_message="La operación integrada falló",
            disable_while_running=(
                app.get_sidebar_action_button("run"),
            ),
            on_progress=lambda progress: metrics.update_metric(
                "processed",
                value=int(progress.current),
                detail=f"{progress.percent}% completado",
            ),
            on_success=lambda rows: (
                table.set_rows(rows),
                metrics.update_metric(
                    "status",
                    value="Completado",
                    semantic="success",
                    detail="Sin bloqueos de interfaz",
                ),
                metrics.update_metric(
                    "warnings",
                    value=sum(1 for row in rows if row["status"] == "Revisar"),
                    semantic="warning",
                    detail="Elementos para revisar",
                ),
            ),
            on_cancelled=lambda _result: metrics.update_metric(
                "status",
                value="Cancelado",
                semantic="warning",
                detail="Cancelación cooperativa",
            ),
            on_error=lambda error: metrics.update_metric(
                "status",
                value="Error",
                semantic="error",
                detail=error.message,
            ),
            on_finished=lambda _result: (
                app.set_sidebar_action_enabled("run", True),
                app.set_sidebar_action_enabled("cancel", False),
            ),
        )
        current_runner["runner"] = runner

    def cancel_operation() -> None:
        runner = current_runner.get("runner")
        if runner is not None:
            runner.cancel()

    app.set_sidebar_action("run", start_operation)
    app.set_sidebar_action("cancel", cancel_operation)
    app.set_status(
        f"Showcase listo · preferencias={resolved_mode} · perfil=compact"
    )

    references = {
        "form": form,
        "query": query,
        "mode": mode,
        "path": path,
        "category": category,
        "metrics": metrics,
        "table": table,
        "details": details,
        "details_card": details_card,
    }
    return app, references


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="GuiCore 1.1 neutral integration showcase."
    )
    parser.add_argument(
        "--preferences",
        choices=VISUAL_PREFERENCE_MODES,
        default="basic",
        help="Visual preferences mode shown by the demo.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app, _references = build_showcase(args.preferences)
    app.mainloop()


if __name__ == "__main__":
    main()
