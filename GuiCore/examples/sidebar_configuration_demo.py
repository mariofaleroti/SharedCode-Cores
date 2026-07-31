from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    GuiActionButton,
    GuiAppConfig,
    GuiAppWindow,
    GuiMenuItem,
    ResultsTable,
    SidebarConfig,
    TableColumn,
)


def main() -> None:
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore Sidebar Demo",
            app_subtitle="Sidebar compacto y declarativo",
            app_version="1.1.0.dev2",
            layout_profile="compact",
            width=1180,
            height=760,
            maximize_on_start=False,
            sidebar_config=SidebarConfig(
                footer_label_visible=False,
                footer_columns=2,
                primary_action_columns=2,
                scrollbar_width=8,
            ),
            primary_actions=(
                GuiActionButton(
                    "Ejecutar",
                    "run",
                    icon_text="▶",
                ),
                GuiActionButton(
                    "Limpiar",
                    "clear",
                    style="secondary",
                    icon_text="⌫",
                ),
            ),
            footer_items=(
                GuiMenuItem("Configuración", "settings"),
                GuiMenuItem("Ayuda", "help"),
                GuiMenuItem("Acerca de", "about"),
                GuiMenuItem("Salir", "exit"),
            ),
        )
    )

    section = app.add_sidebar_section(
        "Configuración",
        "Las acciones principales permanecen visibles fuera del scroll.",
    )
    section.add_labeled_entry("Nombre", value="Aplicación Demo")
    section.add_labeled_combo(
        "Modo",
        ("Automático", "Manual", "Simulación"),
    )
    section.add_path_picker(
        "Ruta",
        placeholder="Seleccionar carpeta...",
    )
    for index in range(8):
        section.add_switch(
            f"Opción adicional {index + 1}",
            default=index % 2 == 0,
        )

    card = app.add_content_card(
        "Estado de la aplicación",
        "La estructura del sidebar proviene completamente de GuiCore.",
        row_weight=1,
    )
    card.frame.grid(sticky="nsew")
    card.content_frame.grid_rowconfigure(0, weight=1)

    table = ResultsTable(
        card.content_frame,
        columns=(
            TableColumn("field", "Campo", width=260),
            TableColumn("value", "Valor", width=420),
        ),
        enable_sorting=False,
        enable_tooltips=False,
    )
    table.set_rows(
        (
            {"field": "Perfil", "value": "compact"},
            {"field": "Acciones fijas", "value": "2 columnas"},
            {"field": "Footer", "value": "2 columnas sin etiqueta"},
            {"field": "Scroll", "value": "Solo formulario"},
        )
    )
    app.register_results_table(table)

    app.set_sidebar_action(
        "run",
        lambda: app.set_status(
            "Acción principal Ejecutar invocada."
        ),
    )
    app.set_sidebar_action(
        "clear",
        lambda: app.set_status(
            "Acción principal Limpiar invocada."
        ),
    )
    app.set_status(
        "La aplicación no manipula footer_frame, footer_buttons ni _scrollbar."
    )
    app.mainloop()


if __name__ == "__main__":
    main()
