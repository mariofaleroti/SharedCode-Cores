from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    CardHeaderAction,
    EmptyState,
    GuiAppConfig,
    GuiAppWindow,
    KeyValueItem,
    KeyValueTable,
    SidebarConfig,
)


def main() -> None:
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore Cards & State",
            app_subtitle="Paneles flexibles y estados reutilizables",
            app_version="1.1.0.dev4",
            layout_profile="compact",
            width=1150,
            height=760,
            maximize_on_start=False,
            sidebar_config=SidebarConfig(
                footer_label_visible=False,
                footer_columns=2,
            ),
        )
    )

    refresh_action = CardHeaderAction(
        "Actualizar",
        command=lambda: app.set_status("Estado actualizado."),
        command_key="refresh",
        style="secondary",
    )

    status_card = app.add_content_card(
        "Estado de la aplicación",
        "Panel principal declarado mediante la API pública.",
        row_weight=3,
        min_height=360,
        sticky="nsew",
        header_actions=(refresh_action,),
    )
    status_table = KeyValueTable(
        status_card.content_frame,
        (
            KeyValueItem("Estado general", "Operativo", "success"),
            KeyValueItem("Servicio principal", "Instalada"),
            KeyValueItem("Frecuencia", "Cada 10 minutos"),
            KeyValueItem("Sincronización", "Correcta", "ready"),
            KeyValueItem("Última ejecución", "Correcta", "success"),
        ),
        layout_profile="compact",
    )
    status_table.grid(row=0, column=0, sticky="nsew")
    app.register_visual_component(status_table)

    paths_card = app.add_collapsible_card(
        "Elementos supervisados",
        "Elementos configurados por la aplicación.",
        row_weight=1,
        min_height=150,
        sticky="nsew",
        collapsed_summary="2 elementos configurados",
    )
    empty = EmptyState(
        paths_card.content_frame,
        "Sin elementos adicionales",
        "Agregar elementos desde la configuración de la aplicación.",
        state="empty",
        action_text="Simular acción",
        action_command=lambda: app.set_status(
            "La acción pertenece al proyecto consumidor."
        ),
        layout_profile="compact",
    )
    empty.grid(row=0, column=0, sticky="nsew")
    app.register_visual_component(empty)

    app.set_status(
        "La proporción 3:1 y el colapso son declarados por GuiCore."
    )
    app.mainloop()


if __name__ == "__main__":
    main()
