# Plantilla de app usando GuiCore

Este ejemplo muestra una estructura mínima para una herramienta real. La lógica se mantiene fuera de GuiCore.

```python
from pathlib import Path

from gui_core import (
    GuiAppConfig,
    GuiAppWindow,
    GuiPreferences,
    ResultsTable,
    TableColumn,
    load_preferences_from_json,
    save_preferences_to_json,
)

PREFERENCES_PATH = Path("config/gui_preferences.json")


def run_tool(app: GuiAppWindow, results_table: ResultsTable) -> None:
    """Connect the real tool engine here."""
    app.progress.show("Preparando...")
    app.progress.update(current=1, total=1, unit="tareas")

    # La herramienta concreta reemplaza estos datos por resultados reales.
    rows = [
        {"index": 1, "name": "Demo", "status": "OK", "detail": "Motor conectado correctamente."},
    ]
    results_table.set_rows(rows)

    app.progress.complete("Finalizado correctamente")
    app.set_status(f"{len(rows)} resultado(s).")


def main() -> None:
    preferences: GuiPreferences = load_preferences_from_json(PREFERENCES_PATH)

    app = GuiAppWindow(
        GuiAppConfig(
            app_name="Mi herramienta",
            app_subtitle="Base visual ShareCode",
            app_version="v0.1.0",
            preferences=preferences,
            help_text="Ayuda propia de la herramienta.",
            about_text="Herramienta construida sobre GuiCore.",
        )
    )

    app.register_preferences_callback(
        lambda updated_preferences: save_preferences_to_json(PREFERENCES_PATH, updated_preferences)
    )

    section = app.add_sidebar_section("Análisis", "Opciones propias de la herramienta.")
    text_input = section.add_labeled_entry("Texto", placeholder="Ej: soporte técnico")
    mode_input = section.add_labeled_combo("Modo", ["Rápido", "Completo"], default_value="Rápido")
    section.add_switch("Recordar opciones", default=True)

    app.add_card(
        "Panel principal",
        "Esta zona explica qué hará la herramienta y muestra acciones principales."
    )

    results_card = app.add_card("Resultados", "Tabla reusable para datos generados por el motor.")
    results_table = ResultsTable(
        results_card.body_frame,
        columns=(
            TableColumn("index", "#", width=50, stretch=False, anchor="center"),
            TableColumn("name", "Nombre", width=180),
            TableColumn("status", "Estado", width=120),
            TableColumn("detail", "Detalle", width=620, max_width=760),
        ),
        selection_mode="browse",
        on_select=lambda rows: app.set_status(f"Seleccionado: {rows[0]['name']}" if rows else "Listo"),
    )
    app.register_results_table(results_table)
    results_table.pack(fill="both", expand=True)

    section.add_action_button("Ejecutar", command=lambda: run_tool(app, results_table))

    app.set_status("Listo")
    app.mainloop()


if __name__ == "__main__":
    main()
```

Notas:

```text
- Los nombres internos están en inglés.
- El texto visible puede estar en español.
- GuiCore no ejecuta el motor: solo ofrece la estructura visual.
- El cambio de tema claro/oscuro reinicia la app de forma segura.
```
