# Quickstart GuiCore

Guía rápida para crear una herramienta GUI nueva usando GuiCore.

## 1. Instalar dependencia visual

```bash
pip install customtkinter
```

Los tests de GuiCore no requieren CustomTkinter porque los imports visuales son diferidos. Una app real sí lo necesita.

## 2. Crear una app base

```python
from gui_core import GuiAppConfig, GuiAppWindow, GuiPreferences

app = GuiAppWindow(
    GuiAppConfig(
        app_name="Event Health",
        app_subtitle="Diagnóstico de eventos de Windows",
        app_version="v0.1.1",
        icon_path="assets/app_icon.ico",
        icon_png_path="assets/app_icon.png",
        preferences=GuiPreferences(
            appearance_mode="dark",
            color_theme="blue",
            surface_theme="default",
            font_family="Segoe UI",
            font_size="Normal",
            table_density="Normal",
        ),
    )
)

app.set_status("Listo")
app.mainloop()
```

## 3. Agregar controles al sidebar

```python
section = app.add_sidebar_section(
    "Análisis",
    "Controles propios de la herramienta."
)

query = section.add_labeled_entry("Texto", placeholder="Ej: soporte técnico")
mode = section.add_labeled_combo("Modo", ["Carpeta", "Archivo"], default_value="Carpeta")
path = section.add_path_picker("Ruta", mode="folder")
remember = section.add_switch("Recordar última ruta", default=True)
section.add_action_button("Ejecutar", command=lambda: app.set_status("Ejecutando..."))
```

GuiCore no decide qué significa ejecutar. Solo ofrece controles visuales y callbacks.

## 4. Crear una card principal

```python
main_card = app.add_card(
    "Panel principal",
    "Cada herramienta conecta aquí su lógica propia."
)
```

## 5. Mostrar progreso

```python
app.progress.show("Preparando análisis...")
app.progress.update(current=25, total=100, unit="archivos")
app.progress.complete("Análisis finalizado correctamente")
```

## 6. Usar tabla de resultados

```python
from gui_core import ResultsTable, TableColumn

results_table = ResultsTable(
    app.content_frame,
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
results_table.set_rows([
    {"index": 1, "name": "Tool Alpha", "status": "Ready", "detail": "Generic visual example."},
])
```

## 7. Usar diálogos comunes

```python
app.show_info("Información", "Operación finalizada.")
app.show_error("Error", "No se pudo completar.", details="Detalle técnico opcional.")

if app.confirm("Confirmar", "¿Querés continuar?"):
    app.set_status("Acción confirmada")

value = app.ask_text("Nuevo nombre", "Ingresá un nombre:", required=True)
```

## 8. Usar una ventana secundaria

```python
from gui_core import SecondaryWindow, SecondaryWindowConfig

child = SecondaryWindow(
    app.root,
    SecondaryWindowConfig(
        title="Detalle",
        subtitle="Información propia de la herramienta.",
        width=720,
        height=520,
        modal=True,
    ),
    app.font_config,
)

# La herramienta agrega sus propios widgets dentro de child.content_frame.
child.add_footer_button("Cerrar", child.close, style="primary")
child.wait()
```

## 9. Persistir preferencias visuales

```python
from gui_core import load_preferences_from_json, save_preferences_to_json

PREFERENCES_PATH = "settings/gui_preferences.json"
preferences = load_preferences_from_json(PREFERENCES_PATH)

app = GuiAppWindow(
    GuiAppConfig(
        app_name="Mi herramienta",
        preferences=preferences,
    )
)

app.register_preferences_callback(
    lambda updated_preferences: save_preferences_to_json(PREFERENCES_PATH, updated_preferences)
)
```

Si el usuario cambia `Tema`, GuiCore guarda la preferencia y reinicia la app automáticamente. Acento, base, fuente y densidad se aplican en vivo.

## 10. Ejecutar demo oficial

```bash
python examples/smartfilter_style_demo.py
```
