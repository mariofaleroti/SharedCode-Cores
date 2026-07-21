# Contrato de GuiCore v0.1

Este documento define qué promete GuiCore y qué queda fuera. La idea es evitar que GuiCore se convierta en una herramienta concreta disfrazada de librería.

## Rol

GuiCore es el **framework visual interno** para herramientas con GUI del ecosistema ShareCode.

```text
Herramienta concreta
├─ motor propio
├─ configuración propia
├─ reglas de negocio propias
└─ GUI construida con GuiCore
```

## GuiCore sí debe contener

```text
- ventana base de producto
- sidebar reusable
- layout principal
- cards/paneles
- barra de progreso
- barra de estado
- tabla reusable
- diálogos comunes
- ventanas secundarias
- configuración visual común
- tema, fuente, densidad y paletas
- helpers visuales testeables
```

## GuiCore no debe contener

```text
- búsqueda de archivos
- categorías inteligentes de SmartFilter
- reglas de EventHealth
- lógica Git de ShadowBackup
- análisis de discos
- exportación específica de una herramienta
- llamadas a motores externos
- decisiones de negocio
```

## Layout oficial

```text
Panel principal / descripción
Progreso de operación activa
Resultados / tabla de datos
Status inferior
```

Motivo: el progreso debe estar cerca de donde se generan los datos, mientras que el status inferior queda para estado general.

## Ventanas

GuiCore distingue dos niveles:

```text
Diálogos simples
├─ info
├─ error
├─ confirmación
├─ entrada simple
├─ ayuda
└─ acerca de

Ventanas secundarias completas
├─ configuración
├─ categorías
├─ detalles
├─ historial
└─ administración avanzada
```

Las ventanas secundarias se crean con `SecondaryWindow`; el contenido específico lo agrega cada herramienta.

## Configuración visual

GuiCore administra preferencias visuales comunes mediante `GuiPreferences`:

```text
- appearance_mode: system / dark / light
- color_theme: color de acento
- surface_theme: color base de la app
- font_family
- font_size
- table_density
```

### Tema claro/oscuro

El tema claro/oscuro/sistema **no se aplica en vivo**. Se guarda la preferencia y se reinicia la aplicación.

Motivo: en ventanas CustomTkinter grandes, cambiar el appearance global en caliente puede congelar la imagen en Windows.

### Cambios seguros en vivo

```text
- color de acento
- color base/superficie
- fuente
- tamaño de fuente
- densidad de tabla
```

## Persistencia

GuiCore no impone ConfigCore ni un archivo obligatorio. La app puede usar:

```text
- ConfigCore
- JSON propio
- memoria temporal
- perfil de usuario
```

GuiCore solo emite preferencias normalizadas mediante callback:

```python
def save_preferences(preferences):
    pass

app.register_preferences_callback(save_preferences)
```

## Compatibilidad

Se mantienen disponibles las piezas iniciales:

```text
- create_main_window
- WindowConfig
- ThemeConfig
- apply_theme
```

Esto evita romper herramientas o pruebas creadas antes del shell visual completo.


## Iconos de ventana

`GuiAppConfig.icon_path` y `GuiAppConfig.icon_png_path` definen el icono principal de la aplicación. `SecondaryWindowConfig` puede heredar el icono del padre o definir uno propio. Windows/Linux están contemplados; macOS queda fuera del alcance.
