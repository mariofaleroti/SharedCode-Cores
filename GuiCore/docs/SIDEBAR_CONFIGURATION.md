# Sidebar configurable — GuiCore 1.1

GuiCore 1.1 permite declarar toda la estructura lateral sin destruir widgets
internos ni acceder a atributos privados.

## Ejemplo

```python
GuiAppConfig(
    app_name="ApplicationDemo",
    layout_profile="compact",
    sidebar_config=SidebarConfig(
        footer_label_visible=False,
        footer_columns=2,
        primary_action_columns=2,
        scrollbar_width=8,
    ),
    primary_actions=(
        GuiActionButton("Guardar", "save"),
        GuiActionButton("Ejecutar", "run"),
    ),
)
```

## Estructura

```text
Sidebar
├─ Header opcional
├─ Formulario con scroll opcional
├─ Acciones primarias fijas
└─ Footer declarativo
```

Las acciones primarias permanecen visibles aunque el formulario tenga muchos
controles.

## Configuración

- `header_visible`
- `scrollable`
- `footer_label_visible`
- `footer_label`
- `footer_columns`
- `footer_button_style`
- `primary_actions_visible`
- `primary_actions_label_visible`
- `primary_actions_label`
- `primary_action_columns`
- `scrollbar_width`

## Acciones

```python
app.set_sidebar_action("run", callback)
app.set_sidebar_action_enabled("run", False)
button = app.get_sidebar_action_button("run")
```

El proyecto aporta únicamente los comandos. GuiCore construye y mantiene la
estructura visual.
