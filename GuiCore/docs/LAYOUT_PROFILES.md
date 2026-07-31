# Perfiles de layout de GuiCore 1.1

Los perfiles de layout centralizan la densidad y el espaciado visual. No cambian
la lógica de un proyecto.

## Perfiles incorporados

```text
compact      → herramientas con muchas opciones o pantallas pequeñas
standard     → comportamiento compatible con GuiCore 1.0.0
comfortable → interfaces con mayor separación y accesibilidad visual
```

El identificador correcto del tercer perfil es `comfortable`.

## Uso

```python
from gui_core import GuiAppConfig, GuiAppWindow

app = GuiAppWindow(
    GuiAppConfig(
        app_name="ShadowBackup",
        layout_profile="compact",
    )
)
```

GuiAppWindow propaga automáticamente el perfil al sidebar, las secciones, los
controles, las barras de botones y las tarjetas creadas mediante sus APIs.

## Perfil personalizado

```python
from gui_core import GuiAppConfig, GuiLayoutProfile

project_profile = GuiLayoutProfile(
    name="project_custom",
    control_height=30,
    action_height=36,
    widget_gap=8,
    content_pad_x=18,
)

config = GuiAppConfig(
    app_name="Tool",
    layout_profile=project_profile,
)
```

Todos los valores son inmutables y serializables mediante `to_dict()`.

## Compatibilidad

`standard` es el perfil predeterminado y conserva los valores históricos más
importantes de GuiCore 1.0.0:

```text
control_height     28
toggle_height      24
action_height      34
menu_button_height 34
sidebar_padding    14
content_pad_x      20
card_inner_pad_x   16
card_corner_radius 14
```

Los proyectos que no declaren `layout_profile` mantienen el comportamiento
anterior.

## Límite

Los perfiles no deciden:

- qué controles muestra una herramienta;
- qué acción ejecuta un botón;
- qué datos aparecen en una tabla;
- cómo se valida la configuración;
- cómo funciona el motor del proyecto.

## Demostración visual

```powershell
.\.venv\Scripts\python.exe .\GuiCore\examples\layout_profiles_demo.py --profile compact
.\.venv\Scripts\python.exe .\GuiCore\examples\layout_profiles_demo.py --profile standard
.\.venv\Scripts\python.exe .\GuiCore\examples\layout_profiles_demo.py --profile comfortable
```
