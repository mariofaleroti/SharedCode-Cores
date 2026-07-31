from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    CardHeaderAction,
    GuiAppConfig,
    GuiAppWindow,
    MetricItem,
    SidebarConfig,
)


def main() -> None:
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore Metrics Demo",
            app_subtitle="Métricas y ayudas contextuales reutilizables",
            app_version="1.1.0.dev5",
            layout_profile="compact",
            width=1120,
            height=700,
            maximize_on_start=False,
            sidebar_config=SidebarConfig(
                footer_label_visible=False,
                footer_columns=2,
            ),
        )
    )

    card = app.add_content_card(
        "Resumen de operación",
        "Los valores y su significado pertenecen a la aplicación consumidora.",
        row_weight=1,
        sticky="nsew",
        header_actions=(
            CardHeaderAction(
                "Actualizar",
                command=lambda: metrics.update_metric(
                    "processed",
                    value=148,
                    detail="Actualizado",
                ),
                command_key="refresh",
            ),
        ),
    )

    metrics = app.create_metric_strip(
        card.content_frame,
        (
            MetricItem(
                "processed",
                "Procesados",
                120,
                semantic="info",
                detail="Elementos",
                tooltip="Cantidad total procesada por la operación.",
            ),
            MetricItem(
                "warnings",
                "Advertencias",
                2,
                semantic="warning",
                detail="Revisar",
                tooltip="Situaciones que requieren atención.",
            ),
            MetricItem(
                "duration",
                "Duración",
                "00:32",
                detail="Minutos y segundos",
                tooltip="Tiempo transcurrido desde el inicio.",
            ),
            MetricItem(
                "status",
                "Estado",
                "Operativo",
                semantic="success",
                detail="Sin bloqueos",
                tooltip="Estado visual informado por la aplicación.",
            ),
        ),
        columns=4,
        tooltip_delay_ms=450,
    )
    metrics.grid(row=0, column=0, sticky="nsew")

    info = app.ctk.CTkLabel(
        card.content_frame,
        text=(
            "Mantener el puntero sobre una métrica para mostrar su ayuda. "
            "Moverlo, hacer clic o desplazar la rueda oculta el tooltip."
        ),
        font=app.font_config.tuple("body"),
        anchor="w",
        justify="left",
        wraplength=760,
    )
    info.grid(
        row=1,
        column=0,
        pady=(app.layout_profile.widget_gap, 0),
        sticky="ew",
    )
    app.add_tooltip(
        info,
        "WidgetTooltip también puede añadirse a cualquier widget existente.",
        title="Ayuda contextual",
        delay_ms=450,
    )

    app.set_status(
        "MetricCard, MetricStrip y WidgetTooltip pertenecen a GuiCore."
    )
    app.mainloop()


if __name__ == "__main__":
    main()
