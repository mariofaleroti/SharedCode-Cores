from pathlib import Path

from _bootstrap import ensure_project_root_on_path

ensure_project_root_on_path()

from gui_core import (
    FontConfig,
    GuiAppConfig,
    GuiAppWindow,
    GuiMenuItem,
    GuiPreferences,
    ResultsTable,
    load_preferences_from_json,
    save_preferences_to_json,
    SecondaryWindow,
    SecondaryWindowConfig,
    TableCell,
    TableColumn,
    ThemeConfig,
    require_customtkinter,
)

ctk = require_customtkinter()

DEMO_PREFERENCES_PATH = Path(__file__).with_name("demo_gui_preferences.json")


def main() -> None:
    demo_preferences = load_preferences_from_json(DEMO_PREFERENCES_PATH)
    app = GuiAppWindow(
        GuiAppConfig(
            app_name="Demo GuiCore",
            app_subtitle="Base visual estilo SmartFilter",
            app_version="v0.1.0",
            theme_config=ThemeConfig(appearance_mode=demo_preferences.appearance_mode, color_theme=demo_preferences.color_theme),
            preferences=demo_preferences,
            footer_items=(
                GuiMenuItem("Configuración", "settings"),
                GuiMenuItem("Ayuda", "help"),
                GuiMenuItem("Acerca de", "about"),
                GuiMenuItem("Salir", "exit"),
            ),
        ),
    )
    app.register_preferences_callback(lambda preferences: save_preferences_to_json(DEMO_PREFERENCES_PATH, preferences))

    # Controles de ejemplo para el sidebar. Cada herramienta real enchufa aquí sus filtros propios.
    search_section = app.add_sidebar_section(
        "Búsqueda",
        "Sección reusable: inputs, combos, pickers, switches y botón principal.",
    )
    search_entry = search_section.add_labeled_entry("Texto", placeholder="Ej: soporte técnico")
    mode_combo = search_section.add_labeled_combo(
        "Modo",
        ["Carpeta", "Archivo individual", "Modo rápido"],
        default_value="Carpeta",
    )
    path_picker = search_section.add_path_picker(
        "Ruta",
        mode="folder",
        placeholder="Seleccionar carpeta...",
    )
    remember_switch = search_section.add_switch("Recordar última ruta", default=True)

    def simulate_run() -> None:
        selected_mode = mode_combo.get_label()
        selected_text = search_entry.get_value() or "sin texto"
        remembered = "sí" if remember_switch.get_value() else "no"
        app.show_progress("Preparando análisis...", 0)
        app.root.after(180, lambda: app.update_progress(35, 100, "elementos"))
        app.root.after(360, lambda: app.update_progress(70, 100, "elementos"))
        app.root.after(540, lambda: app.complete_progress("Análisis finalizado correctamente"))
        app.root.after(560, lambda: app.set_status(f"Demo finalizada · modo={selected_mode} · texto={selected_text} · recordar={remembered}"))

    search_section.add_action_button("Ejecutar demo", command=simulate_run, style="primary")

    summary_card = app.add_content_card(
        "Panel principal",
        "Esta estructura queda lista para que cada herramienta conecte su lógica sin reconstruir la GUI.",
    )
    summary_text = ctk.CTkLabel(
        summary_card.content_frame,
        text="GuiCore aporta ventana, sidebar, controles de formulario, cards, progreso arriba de resultados, tabla, diálogos, estado inferior y paletas separadas de acento/base. La herramienta solo aporta su motor.",
        font=app.font_config.tuple("body"),
        text_color="gray",
        justify="left",
        anchor="w",
        wraplength=840,
    )
    summary_text.grid(row=0, column=0, sticky="ew")

    def open_secondary_demo() -> None:
        child = SecondaryWindow(
            app.root,
            SecondaryWindowConfig(
                title="Ventana secundaria",
                subtitle="Base reutilizable para Categorías, Historial, Detalles o paneles avanzados.",
                width=620,
                height=380,
                modal=True,
            ),
            app.font_config,
        )
        child.content_frame.grid_rowconfigure(0, weight=1)
        label = ctk.CTkLabel(
            child.content_frame,
            text="Esta ventana usa el mismo estilo de GuiCore y no contiene lógica de SmartFilter. Cada herramienta puede llenar este cuerpo con su propia administración.",
            font=app.font_config.tuple("body"),
            text_color="gray",
            justify="left",
            wraplength=520,
        )
        label.grid(row=0, column=0, padx=18, pady=18, sticky="nsew")
        child.add_footer_button("Cerrar", child.close, style="primary")
        child.wait()

    dialog_buttons = app.create_button_row(
        summary_card.content_frame,
        buttons=(
            {"text": "Info", "command_key": "info"},
            {"text": "Error", "command_key": "error"},
            {"text": "Confirmar", "command_key": "confirm"},
            {"text": "Entrada", "command_key": "input"},
            {"text": "Ventana", "command_key": "secondary"},
        ),
        commands={
            "info": lambda: app.show_info("Información", "Diálogo informativo reusable de GuiCore."),
            "error": lambda: app.show_error("Error de ejemplo", "La herramienta puede mostrar un error controlado.", details="Detalle técnico opcional para diagnóstico."),
            "confirm": lambda: app.set_status(f"Confirmación: {app.confirm('Confirmar acción', '¿Querés ejecutar esta acción de prueba?')}"),
            "input": lambda: app.set_status(f"Entrada: {app.ask_text('Entrada simple', 'Escribí un valor de prueba:', placeholder='Valor', required=True) or 'cancelada'}"),
            "secondary": open_secondary_demo,
        },
    )
    dialog_buttons.grid(row=1, column=0, pady=(12, 0), sticky="w")

    table_card = app.add_content_card("Resultados", "Tabla reutilizable con scroll vertical/horizontal y estilo consistente.", row_weight=1)
    table_card.frame.grid(sticky="nsew")
    table_card.content_frame.grid_rowconfigure(0, weight=1)
    table_card.content_frame.grid_columnconfigure(0, weight=1)

    def handle_table_select(rows: list[dict]) -> None:
        if rows:
            app.set_status(f"Fila seleccionada: {rows[0].get('tool', '')}")

    def handle_table_double_click(cell: TableCell) -> None:
        app.set_status(f"Doble click en {cell.column_title}: {cell.value}")

    results_table = ResultsTable(
        table_card.content_frame,
        columns=(
            TableColumn("index", "#", width=50, min_width=50, anchor="center", stretch=False, sortable=True, tooltip=False),
            TableColumn("tool", "Herramienta", width=180, min_width=140),
            TableColumn("area", "Área", width=160, min_width=120),
            TableColumn("status", "Estado", width=150, min_width=110),
            TableColumn("detail", "Detalle", width=620, min_width=320, max_width=760),
        ),
        font_config=app.font_config,
        density=app.preferences.table_density,
        appearance_mode_provider=lambda: app.preferences.appearance_mode,
        color_theme_provider=lambda: app.preferences.color_theme,
        surface_theme_provider=lambda: app.preferences.surface_theme,
        selection_mode="browse",
        on_select=handle_table_select,
        on_double_click=handle_table_double_click,
    )
    app.register_results_table(results_table)
    results_table.set_rows(
        [
            {"index": 1, "tool": "SmartFilter", "area": "Búsqueda", "status": "Producto", "detail": "La GUI actual sirve como referencia visual, no como copia directa."},
            {"index": 2, "tool": "EventHealth", "area": "Diagnóstico", "status": "Próximo", "detail": "Puede reutilizar la ventana base y conectar su motor de eventos."},
            {"index": 3, "tool": "ShadowBackup", "area": "Git", "status": "Futuro", "detail": "Puede usar sidebar, progreso y estado sin duplicar diseño."},
            {"index": 4, "tool": "GuiCore", "area": "Tabla", "status": "v0.1", "detail": "Ahora soporta columnas configurables, tooltips cuando el texto no entra, selección, doble click, autosize y orden por encabezado."},
            {"index": 5, "tool": "GuiCore", "area": "Sidebar", "status": "v0.1", "detail": "Ahora incluye controles reutilizables para formularios laterales: entry, combo, picker, checkbox/switch y botones."},
            {"index": 6, "tool": "GuiCore", "area": "Visual", "status": "v0.1", "detail": "Configuración separa color de acento y color base de la app con barras de selección visual."},
        ]
    )
    results_table.auto_size_columns(max_width=760)

    app.set_status("GuiCore demo lista. Tema claro/oscuro reinicia la app; acento/base/fuente/tabla en vivo.")
    app.mainloop()


if __name__ == "__main__":
    main()
