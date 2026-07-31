# Tarjetas y componentes de estado — GuiCore 1.1

## Tarjetas con proporción declarativa

```python
status_card = app.add_content_card(
    "Estado",
    row_weight=3,
    min_height=360,
    sticky="nsew",
)

paths_card = app.add_content_card(
    "Rutas",
    row_weight=1,
    min_height=150,
    sticky="nsew",
)
```

El proyecto ya no necesita usar:

```python
card.frame.grid_configure(...)
content_frame.grid_rowconfigure(...)
```

## Acciones de cabecera

```python
CardHeaderAction(
    "Actualizar",
    command=refresh,
    command_key="refresh",
)
```

## Tarjeta plegable

```python
card = app.add_collapsible_card(
    "Detalle",
    collapsed=True,
    collapsed_summary="3 elementos",
)
```

`CollapsibleSectionCard` administra `grid_remove`, el botón de restauración y el
callback de cambio.

## Tabla clave/valor

```python
KeyValueTable(
    parent,
    (
        KeyValueItem("Estado", "Operativo", "success"),
        KeyValueItem("Tarea", "Instalada"),
    ),
)
```

GuiCore presenta los valores. El proyecto decide qué significan.

## Estado vacío

```python
EmptyState(
    parent,
    "Sin resultados",
    "Ejecutar una operación para comenzar.",
    action_text="Ejecutar",
    action_command=run,
)
```

Estados admitidos:

```text
empty
loading
error
ready
info
warning
```
