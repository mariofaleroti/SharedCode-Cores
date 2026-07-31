# Métricas y tooltips — GuiCore 1.1

## Métricas

GuiCore presenta métricas, pero no interpreta su significado.

```python
MetricItem(
    key="processed",
    title="Procesados",
    value=120,
    semantic="info",
    detail="Elementos",
    tooltip="Cantidad total procesada.",
)
```

Componentes públicos:

```text
MetricItem
MetricCard
MetricStrip
```

### MetricStrip

```python
strip = app.create_metric_strip(
    parent,
    metrics,
    columns=4,
)
strip.grid(row=0, column=0, sticky="ew")
```

Actualizar una métrica:

```python
strip.update_metric(
    "processed",
    value=148,
    detail="Actualizado",
    semantic="success",
)
```

Semánticas habituales:

```text
neutral
accent / info
success / ready / ok
warning / attention
danger / error / failed
```

## Tooltips

```python
tooltip = WidgetTooltip(
    widget,
    "Descripción contextual.",
    title="Ayuda",
    delay_ms=800,
    visible_ms=4000,
    wraplength=320,
)
```

También puede registrarse desde la aplicación:

```python
app.add_tooltip(
    widget,
    "Descripción contextual.",
    title="Ayuda",
)
```

El componente:

- enlaza defensivamente el widget y sus descendientes;
- se oculta al salir, mover el puntero, hacer clic o desplazar;
- limita su posición al área visible de la pantalla;
- respeta fuente, superficie y apariencia;
- cancela callbacks pendientes al destruirse.

El tooltip interno de celdas de `ResultsTable` permanece como una especialización
propia de la tabla.
