# GuiCore

GuiCore es la base visual compartida para herramientas con interfaz gráfica del ecosistema.
Para este ecosistema, GUI significa **CustomTkinter**. La idea no es crear una ventana genérica mínima, sino una base visual moderna, consistente y reutilizable para herramientas que necesiten destacar.

## Estado v0.1

**GuiCore v0.1.1 queda como base visual estable inicial con iconos centralizados Windows/Linux.**

Esta versión se considera lista para ser consumida por herramientas reales del ecosistema, por ejemplo EventHealth, ShadowBackup, SmartDisk o futuras apps con CustomTkinter. A partir de este punto, los cambios nuevos deberían responder a necesidades reales detectadas al integrar herramientas concretas.

Documentación de cierre:

```text
CHANGELOG.md
docs/README.md
docs/GUI_CONTRACT.md
docs/QUICKSTART.md
docs/COMPONENT_MAP.md
docs/APP_TEMPLATE.md
```

Regla de oro: GuiCore resuelve la experiencia visual común; la lógica de negocio siempre queda en cada herramienta.

## Rol en SharedCode

```text
GuiCore define patrones visuales reutilizables.
Cada herramienta mantiene su lógica propia.
GuiCore no ejecuta procesos, no escanea y no interpreta datos de negocio.
```

## Decisión de diseño

```text
DESIGN: CustomTkinter es la base visual oficial de GuiCore.
DESIGN: Tkinter puro queda fuera salvo como dependencia interna de CustomTkinter o ttk.Treeview.
DESIGN: los imports de CustomTkinter son diferidos para que tests y validaciones no fallen en entornos sin GUI.
DESIGN: GuiCore toma patrones visuales de SmartFilter, pero no copia su lógica de negocio.
```

## Componentes actuales

```text
gui_core/
├─ app/
│  └─ app_window.py          # shell visual: sidebar + contenido + progreso + estado
├─ app_config.py             # contrato visual declarativo de una app
├─ preferences.py            # preferencias visuales comunes
├─ windows/
│  ├─ secondary_window.py    # ventanas secundarias completas
│  ├─ settings_window.py     # configuración visual reusable
│  └─ window_icon.py         # iconos centralizados Windows/Linux
├─ styles/
│  ├─ colors.py              # paletas separadas: acento + superficie/base
│  ├─ fonts.py               # familias, tamaños y roles de fuente
│  └─ table_style.py         # densidad de tabla
├─ widgets/
│  ├─ sidebar.py             # panel izquierdo estilo producto
│  ├─ content_panel.py       # contenedor principal
│  ├─ section_card.py        # panel/cards reutilizables
│  ├─ form_controls.py       # formularios laterales: inputs, combos, pickers, switches, botones
│  ├─ progress_panel.py      # progreso estándar
│  ├─ results_table.py       # tabla reusable basada en ttk.Treeview
│  └─ status_bar.py          # barra de estado inferior
├─ dialogs/
│  └─ message_dialog.py      # info/error/warning/confirm/input/help/about
├─ theme.py                  # aplicación de tema CustomTkinter
├─ window.py                 # factory mínima original, preservada por compatibilidad
└─ examples/
   ├─ basic_customtkinter_app.py
   └─ smartfilter_style_demo.py
```

## Uso recomendado

```python
from gui_core import GuiAppConfig, GuiAppWindow, ThemeConfig

app = GuiAppWindow(
    GuiAppConfig(
        app_name="Event Health",
        app_subtitle="Diagnóstico de eventos de Windows",
        app_version="v0.1.1",
        icon_path="assets/app_icon.ico",
        icon_png_path="assets/app_icon.png",
        theme_config=ThemeConfig(appearance_mode="Oscuro", color_theme="blue"),
    )
)

app.set_status("Listo")
app.mainloop()
```


## Iconos de ventana Windows/Linux

GuiCore centraliza el icono visual de la app para evitar que cada herramienta aplique lógica propia de sistema operativo.

```python
from gui_core import GuiAppConfig, GuiAppWindow

app = GuiAppWindow(
    GuiAppConfig(
        app_name="SmartFilter",
        app_version="v0.1.1",
        icon_path="assets/app_icon.ico",      # recomendado para Windows
        icon_png_path="assets/app_icon.png", # recomendado para Linux
    )
)
```

Reglas:

```text
Windows prefiere .ico mediante iconbitmap.
Linux prefiere .png mediante iconphoto.
SecondaryWindow hereda el icono del padre por defecto.
Si el icono falla o no existe, la ventana abre igual.
```

## Demo visual estilo SmartFilter

```bash
python examples/smartfilter_style_demo.py
```

La demo muestra una aplicación con:

```text
- ventana base maximizable
- sidebar izquierdo
- menú inferior estándar
- controles propios de herramienta dentro del sidebar
- formulario lateral reusable: entry, combo, picker, switch y botón
- cards de contenido
- barra de progreso arriba de resultados
- tabla de resultados reutilizable
- diálogos comunes reutilizables
- ventana secundaria reusable
- configuración por pestañas: Visual + General
- cambio de acento/base/fuente/densidad en vivo y reinicio automático seguro cuando cambia el tema claro/oscuro
- acento propagado a botones principales, menú, progreso, selección, switches y diálogos
- base propagada a fondo, sidebar, secciones laterales, cards, inputs, combos, ventanas secundarias y diálogos
- barra de estado inferior limpia
```



## Sidebar form controls v0.1

GuiCore incluye controles reutilizables para que cada herramienta arme su panel lateral sin copiar diseño ni estilos. Estos controles no hacen búsqueda, no validan reglas de negocio y no ejecutan motores propios; solo exponen valores y callbacks.

```python
section = app.add_sidebar_section(
    "Análisis",
    "Controles propios de la herramienta."
)

query = section.add_labeled_entry("Texto", placeholder="Ej: soporte técnico")
mode = section.add_labeled_combo("Modo", ["Carpeta", "Archivo"], default_value="Carpeta")
path = section.add_path_picker("Ruta", mode="folder")
remember = section.add_switch("Recordar última ruta", default=True)
section.add_action_button("Ejecutar", command=run_analysis)
```

Componentes disponibles:

```text
- SidebarFormSection
- LabeledEntry
- LabeledComboBox
- PathPicker
- LabeledCheckBox
- LabeledSwitch
- ActionButton
- ButtonRow
- ChoiceOption y ButtonSpec para configuración declarativa
```

Helpers testeables sin abrir GUI:

```text
- normalize_command_key
- normalize_button_style
- normalize_picker_mode
- normalize_control_state
- coerce_choice_options
- get_choice_labels
- get_button_style_options
```

Ejemplos de uso por herramienta:

```text
SmartFilter  -> búsqueda, modo, carpeta, recordar ruta
EventHealth  -> rango, origen, nivel, cantidad máxima, ejecutar análisis
ShadowBackup -> raíz de proyectos, modo push, dry-run, ejecutar backup
SmartDisk    -> selección de disco, modo de informe, ejecutar escaneo
```

## ResultsTable v0.1

`ResultsTable` quedó como componente de tabla reutilizable para herramientas con resultados tabulares. La lógica del dato sigue fuera de GuiCore; la tabla solo maneja presentación e interacción.

```python
from gui_core import ResultsTable, TableColumn

results_table = ResultsTable(
    parent,
    columns=(
        TableColumn("index", "#", width=50, stretch=False, anchor="center"),
        TableColumn("tool", "Herramienta", width=180),
        TableColumn("detail", "Detalle", width=620, max_width=760),
    ),
    selection_mode="browse",
    on_select=lambda rows: print(rows),
    on_double_click=lambda cell: print(cell.column_key, cell.value),
)

results_table.set_rows([
    {"index": 1, "tool": "EventHealth", "detail": "Motor propio conectado a GuiCore."},
])
results_table.auto_size_columns()
```

Capacidades actuales:

```text
- columnas declarativas con key, título, ancho, mínimo, stretch, sortable y tooltip
- scroll vertical y horizontal
- Shift + rueda para scroll horizontal
- selección browse/extended/none
- callbacks on_select, on_row_click y on_double_click
- recuperación de filas seleccionadas como dict por key de columna
- tooltip solo cuando el texto no entra en la celda
- autosize conservador por contenido
- orden por encabezado cuando la columna es sortable
- helpers testeables sin abrir GUI: coerce_row_values, row_values_to_mapping, normalize_selection_mode
```

## Diálogos comunes v0.1

GuiCore incluye diálogos genéricos para que cada herramienta no tenga que recrear ventanas comunes. La lógica y el texto específico siguen perteneciendo a cada proyecto.

```python
app.show_info("Información", "Operación finalizada.")
app.show_error("Error", "No se pudo completar la acción.", details="Detalle técnico opcional.")

if app.confirm("Confirmar", "¿Querés continuar?"):
    app.set_status("Acción confirmada")

value = app.ask_text("Nuevo nombre", "Ingresá un nombre:", required=True)
```

Tipos disponibles:

```text
- show_info / show_success / show_warning / show_error
- confirm para decisiones True/False
- ask_text para entrada simple
- show_help y show_about conectados al menú inferior
- DialogSpec y DialogButton para diálogos declarativos avanzados
```

`GuiAppConfig` puede recibir `help_text` y `about_text` para que cada herramienta personalice Ayuda y Acerca de sin reemplazar la ventana completa.


## Ventanas secundarias v0.1

GuiCore diferencia diálogos simples de ventanas secundarias completas. Los diálogos son para mensajes breves; las ventanas secundarias son para módulos como Categorías, Historial, Detalles o Configuración avanzada.

```python
from gui_core import SecondaryWindow, SecondaryWindowConfig

child = SecondaryWindow(
    app.root,
    SecondaryWindowConfig(
        title="Categorías",
        subtitle="Administración propia de la herramienta.",
        width=720,
        height=520,
        modal=True,
    ),
    app.font_config,
)

# La herramienta agrega sus widgets propios dentro de child.content_frame.
child.add_footer_button("Cerrar", child.close, style="primary")
child.wait()
```

`SecondaryWindow` aporta estilo, centrado, header, cuerpo, footer y comportamiento modal. No sabe qué es una categoría, un evento o un repositorio.

## Configuración común v0.1

El botón `Configuración` del menú inferior abre una ventana real de GuiCore organizada por pestañas. La pestaña `Visual` contiene las preferencias de apariencia ya implementadas; la pestaña `General` queda reservada para configuraciones comunes futuras que no sean visuales.

```text
Visual
├─ Tema: Sistema / Oscuro / Claro
├─ Color de acento: botones primarios, menú inferior, progreso, selección de tabla, switches y diálogos
├─ Barra visual de acento: Azul / Verde / Azul oscuro / Morado / Naranja / Rojo / Turquesa / Negro / Carbón / Grafito / Pizarra / Gris
├─ Color base de app: fondo, sidebar, footer lateral, secciones, cards, inputs, combos, ventanas y superficies principales
├─ Barra visual de base: Predeterminado / Ónix / Carbón / Grafito / Medianoche / Bosque
├─ Fuente: Segoe UI / Arial / Calibri / Verdana / Tahoma / Consolas
├─ Tamaño de fuente: Pequeña / Normal / Grande / Muy grande
└─ Densidad de tabla: Compacta / Normal / Cómoda

General
└─ Reservado para preferencias futuras: recordar tamaño/posición, confirmar salida, comportamiento global, etc.
```

Estrategia anti-congelamiento: GuiCore no cambia el modo claro/oscuro en caliente. Si el usuario cambia el tema, GuiCore guarda la preferencia mediante los callbacks registrados y reinicia la aplicación de forma automática para aplicar el tema desde el arranque. En vivo solo se refrescan piezas seguras: color de acento, color base de app, fuente y densidad de tabla. Esto evita el congelamiento observado en aplicaciones CustomTkinter grandes al usar cambios globales de apariencia sobre una ventana ya renderizada.

La configuración visual separa dos conceptos:

```text
Color de acento
└─ botones primarios, barra de progreso, switches y selección de tabla

Color base de app
└─ fondo general, sidebar, footer lateral, cards, tabla y superficies principales
```

Esto permite combinaciones más profesionales: por ejemplo, base Ónix + acento Morado, base Grafito + acento Azul, o base Bosque + acento Verde. La pestaña Visual muestra barras de preview separadas para elegir ambos colores de forma más clara que con combos únicamente textuales.

Uso declarativo:

```python
from gui_core import GuiAppConfig, GuiAppWindow, GuiPreferences

app = GuiAppWindow(
    GuiAppConfig(
        app_name="Event Health",
        preferences=GuiPreferences(
            appearance_mode="Oscuro",
            color_theme="blue",        # acento
            surface_theme="onyx",      # base/superficie
            font_family="Segoe UI",
            font_size="Normal",
            table_density="Normal",
        ),
    )
)
```

La app concreta decide cómo persistir estos valores. GuiCore solo define la experiencia visual y emite `GuiPreferences` normalizadas mediante callbacks.

```python
def save_preferences(preferences):
    # Guardar con ConfigCore, JSON propio o memoria temporal.
    pass

app.register_preferences_callback(save_preferences)
```

Las tablas registradas con `app.register_results_table(results_table)` reciben automáticamente fuente, densidad, acento y base al aplicar configuración. Los componentes visuales creados con `app.create_button_row(...)` o `app.add_sidebar_section(...)` también se refrescan cuando la app aplica preferencias.

## Dependencia visual

Para ejecutar una aplicación real con GuiCore:

```bash
pip install customtkinter
```

Los tests no requieren CustomTkinter instalado porque los imports visuales se resuelven de forma diferida.

## Validaciones

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

## Doctrina de layout

```text
Panel principal / descripción
Progreso de operación activa
Resultados / tabla de datos
Barra de estado inferior
```

El progreso queda cerca de los datos que se están generando. La barra inferior queda reservada para estado general de la aplicación.

## Línea de diseño

SmartFilter se toma como referencia visual porque ya es producto final. Aun así, GuiCore debe mantenerse neutral:

```text
GuiCore sí contiene:
- shell visual
- sidebar
- cards
- fuentes
- colores
- tabla
- progreso
- estado
- diálogos genéricos
- controles de formulario laterales
- ventanas secundarias completas
- configuración común por pestañas

GuiCore no contiene:
- categorías inteligentes
- búsqueda de archivos
- filtros de contenido
- exportación propia de SmartFilter
- reglas de negocio de una herramienta concreta
```

## Nota sobre tema claro/oscuro

GuiCore no cambia el tema claro/oscuro en vivo dentro de una ventana ya renderizada. En aplicaciones grandes con CustomTkinter, ese cambio puede congelar la imagen en algunos equipos Windows. Por seguridad, cuando el tema cambia, GuiCore persiste la preferencia y reinicia la aplicación automáticamente.

La configuración visual queda separada así:

- Color de acento, color base de app, fuente, tamaño y densidad de tabla: cambios en vivo.
- Tema claro/oscuro/sistema: guarda la preferencia y fuerza reinicio seguro.

La demo usa `examples/demo_gui_preferences.json` para mostrar ese flujo. Una herramienta real puede guardar las preferencias con ConfigCore o con su propio archivo de configuración y pasarlas a `GuiAppConfig(preferences=...)` al iniciar. El reinicio automático está activo por defecto con `restart_on_appearance_change=True`; puede desactivarse si una herramienta necesita controlar ese flujo manualmente.


### Ajustes visuales de paleta

- El color de acento y el color base se propagan a componentes registrados y a controles agregados luego de crear una sección lateral.
- La ventana de Configuración usa barras compactas de paleta, sin dependencia obligatoria de `CTkColorPicker`, para mantener GuiCore portable.

- Barra de progreso indeterminada reutilizable para procesos cuyo total todavía no se conoce.


## Showcase GuiCore 1.1

```powershell
python GuiCore/examples/guicore_1_1_showcase.py --preferences basic
```

Modos disponibles: `none`, `basic`, `advanced`.
