# Migración explícita de GuiCore 1.0 a 1.1

SharedCode 1.0.0 permanece congelado. Un proyecto continúa usando esa release
hasta decidir migrar de forma explícita a GuiCore 1.1.

## Estrategia

1. crear una rama de migración del proyecto consumidor;
2. instalar una prerelease o wheel de GuiCore 1.1;
3. seleccionar un `layout_profile`;
4. reemplazar ajustes privados por APIs públicas;
5. validar GUI, CLI y automatización del proyecto;
6. fijar la nueva versión solamente después de la validación.

## Cambios principales

| Necesidad anterior | Contrato 1.1 |
|---|---|
| tamaños repetidos | `GuiLayoutProfile` |
| footer reconstruido | `SidebarConfig` |
| acciones fuera del scroll | `primary_actions` |
| controles privados compactos | controles públicos parametrizables |
| pesos manipulando `.frame` | `row_weight`, `min_height`, `sticky` |
| colapso manual | `CollapsibleSectionCard` |
| métricas artesanales | `MetricStrip` |
| tooltip propio | `WidgetTooltip` |
| hilo y cola propios | `GuiTaskRunner` |
| preferencias siempre completas | `visual_preferences` |

## Preferencias visuales

```python
GuiAppConfig(
    app_name="ApplicationDemo",
    visual_preferences="basic",
)
```

- `none`: no muestra la acción común de configuración;
- `basic`: tema, fuente, tamaño y densidad;
- `advanced`: selectores de acento y superficie, tema, fuente, tamaño y densidad.

## Límite arquitectónico

GuiCore administra presentación, ciclo visual y seguridad del hilo de interfaz.
El proyecto conserva validaciones, configuración operativa, lectura de datos y
lógica de negocio.
