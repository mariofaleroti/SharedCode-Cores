# Controles compactos reutilizables — GuiCore 1.1

GuiCore 1.1.0.dev3 incorpora opciones visuales reutilizables para construir
formularios densos sin crear clases privadas en cada proyecto.

## Capacidades comunes

Los controles aceptan, según corresponda:

- `height`
- `width`
- `label_visible`
- `font_role`
- `label_font_role`
- `label_weight`
- `label_gap`
- `button_width`
- `gap`
- `button_style`
- `on_change`

El perfil `compact` continúa siendo la fuente principal de dimensiones. Las
opciones directas permiten excepciones puntuales sin reconstruir widgets.

## Entry sin etiqueta

```python
entry = section.add_labeled_entry(
    "Buscar",
    label_visible=False,
    height=25,
    width=280,
    font_role="small",
)
```

## PathPicker compacto

```python
picker = section.add_path_picker(
    "Ruta",
    width=300,
    height=26,
    button_width=34,
    gap=6,
    font_role="small",
)
```

## Combo con acción auxiliar

```python
category = section.add_labeled_combo_action(
    "Categoría",
    ("Todas", "Documentos", "Código"),
    button_text="...",
    button_command=open_categories,
)
```

`LabeledComboAction` mantiene valores estables mediante `ChoiceOption`, permite
habilitar solamente el botón auxiliar y comparte temas/fuentes con GuiCore.

La lógica, validaciones y callbacks permanecen siempre en el proyecto consumidor.
