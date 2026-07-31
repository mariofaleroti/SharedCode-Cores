from __future__ import annotations

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    ChoiceOption,
    GuiActionButton,
    GuiAppConfig,
    GuiAppWindow,
    GuiMenuItem,
    SidebarConfig,
)


def main() -> None:
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="GuiCore Compact Controls",
            app_subtitle="Controles reutilizables inspirados en SmartFilter",
            app_version="1.1.0.dev3",
            layout_profile="compact",
            width=1100,
            height=760,
            maximize_on_start=False,
            sidebar_width=350,
            sidebar_config=SidebarConfig(
                footer_label_visible=False,
                footer_columns=2,
                primary_action_columns=2,
            ),
            primary_actions=(
                GuiActionButton("Ejecutar", "run"),
                GuiActionButton(
                    "Limpiar",
                    "clear",
                    style="secondary",
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
        "Búsqueda",
        "El proyecto no crea clases compactas propias.",
    )
    search = section.add_labeled_entry(
        "Buscar",
        placeholder="Palabra o frase...",
        font_role="small",
    )
    section.add_labeled_combo(
        "Modo",
        ("Nombre", "Contenido"),
        font_role="small",
    )
    section.add_path_picker(
        "Ruta",
        placeholder="Seleccionar carpeta...",
        font_role="small",
        button_width=32,
    )
    section.add_labeled_combo_action(
        "Categoría",
        (
            ChoiceOption("Todas", "all"),
            ChoiceOption("Documentos", "documents"),
            ChoiceOption("Código", "code"),
        ),
        button_text="...",
        font_role="small",
    )
    section.add_switch(
        "Recordar ubicación",
        font_role="small",
    )
    section.add_checkbox(
        "Incluir subcarpetas",
        default=True,
        font_role="small",
    )

    app.set_sidebar_action(
        "run",
        lambda: app.set_status(
            f"Ejecutar · criterio={search.get_value() or '(vacío)'}"
        ),
    )
    app.set_sidebar_action(
        "clear",
        lambda: (
            search.clear(),
            app.set_status("Formulario limpiado."),
        ),
    )
    app.set_status(
        "Entry, Combo, PathPicker, Switch y ComboAction provienen de GuiCore."
    )
    app.mainloop()


if __name__ == "__main__":
    main()
