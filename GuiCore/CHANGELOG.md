# Changelog

Todas las notas relevantes de GuiCore quedan registradas aquí. El objetivo es
que cada herramienta del ecosistema pueda saber qué contrato visual está
consumiendo.

## Unreleased — objetivo v1.1.0

Estado: **implementación iniciada en la línea 1.1.0.dev0**.

### Decisiones

- SharedCode 1.0.0 permanece congelado y disponible.
- GuiCore 1.1.0 tendrá un contrato propio; los proyectos anteriores permanecen fijados a 1.0.0.
- SmartFilter se utilizará como fuente de patrones visuales maduros, no de lógica
  de negocio.
- ShadowBackup será el primer consumidor de validación.
- La migración de proyectos será individual y con dependencias fijadas.

### Alcance planificado

- corrección completa de `ResultsTable`;
- perfiles de layout;
- sidebar/footer compactos y configurables;
- acciones primarias fijas;
- controles compactos;
- tarjetas plegables;
- tabla de estado;
- estados vacíos;
- tooltips;
- métricas visuales;
- ciclo visual genérico de operaciones largas.

### Implementado

- `ResultsTable` ya no pasa `command=None` a `ttk.Treeview.heading`.
- El parámetro `enable_sorting=False` vuelve a ser seguro.
- Las columnas individuales con `sortable=False` omiten completamente el
  callback de encabezado.
- Se agregó un helper puro para probar las opciones de encabezado.
- Se agregaron pruebas unitarias y smoke tests con widgets `ttk` reales.
- La fuente del repositorio inicia la línea de desarrollo `1.1.0.dev0`.
- Los metadatos heredables de iconos ahora usan separadores `/` estables en Windows y Linux.
- Se agregaron perfiles de layout `compact`, `standard` y `comfortable`.
- `standard` define la densidad equilibrada predeterminada de GuiCore 1.1.
- GuiAppWindow propaga densidad, alturas y espaciados a sidebar, controles y tarjetas.
- Se documentaron perfiles personalizados inmutables y serializables.
- La línea de desarrollo avanza a `1.1.0.dev1`.
- Se agregó `SidebarConfig` para declarar header, scroll, footer y acciones fijas.
- El footer admite de una a cuatro columnas y etiqueta opcional.
- Las acciones primarias permanecen fuera del formulario desplazable.
- El scrollbar puede configurarse sin acceder a `_scrollbar` desde el proyecto consumidor.
- Se agregaron APIs públicas para habilitar acciones y obtener sus botones.
- La línea de desarrollo avanza a `1.1.0.dev2`.
- Los controles de formulario aceptan dimensiones, roles de fuente y etiquetas opcionales.
- `PathPicker` permite declarar ancho total, ancho del botón auxiliar y separación.
- Se agregó `LabeledComboAction` como componente público.
- Switches, checkboxes y botones aceptan geometría y tipografía configurables.
- `SidebarFormSection` puede crear combos con acción sin frames manuales.
- La línea de desarrollo avanza a `1.1.0.dev3`.
- `SectionCard` admite acciones declarativas en la cabecera.
- `GuiAppWindow` permite declarar peso, altura mínima y sticky de cada tarjeta.
- Se agregó `CollapsibleSectionCard` y `add_collapsible_card`.
- Se agregaron `KeyValueTable`, `KeyValueItem` y `EmptyState`.
- Los estados visuales ya no necesitan filas falsas dentro de tablas de negocio.
- La línea de desarrollo avanza a `1.1.0.dev4`.
- Corrección dev4: la prueba de geometría valida el padding del contenedor de cabecera.
- Corrección dev4: los smoke tests cancelan callbacks `after` antes de destruir raíces Tk.
- Corrección dev4: demos y documentación genérica usan ejemplos neutrales.
- Corrección dev4: el contrato 1.1 protege su propia suite; 1.0.0 permanece como release independiente.
- Se agregaron `MetricItem`, `MetricCard` y `MetricStrip`.
- Se agregó `WidgetTooltip` con cierre defensivo, límite de pantalla y cancelación de callbacks.
- `GuiAppWindow` expone `create_metric_strip` y `add_tooltip`.
- La Fase 5 queda completa con métricas y ayudas contextuales genéricas.
- La línea de desarrollo avanza a `1.1.0.dev5`.
- Se agregó `GuiTaskRunner` para workers cooperativos sin acceso a Tk.
- Se agregaron `TaskContext`, `TaskProgress`, `TaskError`, `TaskResult` y `CancellationToken`.
- El progreso aplica throttling y coalescencia por ciclo de polling.
- `ProgressPanel` admite cancelación opcional.
- `GuiAppWindow.start_task` integra progreso, cancelación, controles y claves de tarea.
- El cierre de ventana cancela y desconecta runners activos.
- La línea de desarrollo avanza a `1.1.0.dev6`.
- Se implementaron los modos de preferencias visuales `none`, `basic` y `advanced`.
- El modo `none` elimina la acción común de configuración del footer.
- El modo `basic` limita la ventana a tema, fuente, tamaño y densidad.
- Se agregó `examples/guicore_1_1_showcase.py` como integración neutral oficial.
- Se agregaron quickstart actualizado y guía de migración explícita 1.0 → 1.1.
- La línea de desarrollo avanza a `1.1.0.dev7`.
- Corrección dev7: el cierre de ventanas secundarias cancela callbacks `after` mediante su widget propietario.
- Corrección dev7: se evita la doble eliminación de comandos Tcl en Python 3.13.
- Corrección dev7: `SecondaryWindow.close()` es idempotente y administra su callback de elevación.

### Documentación

- `docs/GUI_CORE_1_1_CONTRACT.md`
- `docs/SMARTFILTER_EXTRACTION_MAP.md`
- `docs/GUI_CORE_1_1_IMPLEMENTATION_PLAN.md`

## v0.1.2 - Progreso indeterminado reutilizable

Estado: **cambio aditivo y compatible**.

### Agregado

- `ProgressPanel.show_indeterminate()` para procesos cuyo total todavía no se conoce.
- `GuiAppWindow.show_indeterminate_progress()` como API pública.
- Transición segura entre progreso animado y progreso determinado.
- Detención defensiva de la animación al completar, ocultar o volver a modo determinado.

## v0.1.1 - Iconos centralizados Windows/Linux

Estado: **corte aditivo para preparar herramientas GUI sin acople directo al sistema operativo**.

### Agregado

- `window_icon.py` con helpers defensivos para aplicar iconos en ventanas Tk/CustomTkinter.
- `GuiAppConfig.icon_path` para icono principal, normalmente `.ico` en Windows.
- `GuiAppConfig.icon_png_path` para fallback visual, recomendado en Linux.
- `SecondaryWindowConfig.icon_path`, `icon_png_path` e `inherit_parent_icon`.
- Herencia automática del icono desde la ventana principal hacia ventanas secundarias.
- Tests de resolución/aplicación de iconos sin requerir entorno gráfico real.

### Decisiones de diseño

- Windows y Linux quedan contemplados; macOS queda fuera del alcance por decisión del ecosistema.
- Si el icono no existe o falla, la ventana debe abrir igual.
- Las herramientas no deberían llamar `iconbitmap`/`iconphoto` directamente salvo casos excepcionales.

## v0.1.0 - Base visual estable ShareCode

Estado: **aprobada como base inicial de GuiCore para ShareCode**.

### Agregado

- `GuiAppWindow` como shell visual reutilizable:
  - sidebar izquierdo
  - área principal por cards
  - progreso arriba de resultados
  - tabla como protagonista
  - status inferior limpio
- `GuiAppConfig` como contrato declarativo de aplicación.
- `GuiPreferences` para preferencias visuales comunes.
- Separación de paleta en dos conceptos:
  - color de acento: botones, progreso, switches, selección de tabla y acciones principales
  - color base/superficie: fondo, sidebar, cards, tabla, inputs, combos y ventanas
- Configuración visual común con pestañas:
  - Visual
  - General reservado para futuras preferencias comunes
- Reinicio seguro al cambiar tema claro/oscuro/sistema.
- Cambios en vivo para:
  - color de acento
  - color base de app
  - fuente
  - tamaño de fuente
  - densidad de tabla
- `SidebarFormSection` y controles laterales reutilizables:
  - `LabeledEntry`
  - `LabeledComboBox`
  - `PathPicker`
  - `LabeledCheckBox`
  - `LabeledSwitch`
  - `ActionButton`
  - `ButtonRow`
- `ResultsTable` reusable basada en `ttk.Treeview`:
  - columnas declarativas
  - scroll vertical/horizontal
  - tooltip de celda cuando el texto no entra
  - selección simple/múltiple
  - callbacks de selección, click y doble click
  - orden por encabezado
  - autosize conservador
- Diálogos comunes:
  - info
  - éxito
  - advertencia
  - error
  - confirmación
  - entrada de texto
  - ayuda
  - acerca de
- `SecondaryWindow` para ventanas secundarias completas:
  - configuración
  - categorías
  - detalles
  - historial
  - módulos avanzados
- Persistencia JSON simple de preferencias mediante `preferences_store.py`.
- Demo visual estilo SmartFilter:
  - `examples/smartfilter_style_demo.py`
- Bootstrap de ejemplos para ejecutar desde PowerShell sin instalar el paquete:
  - `examples/_bootstrap.py`

### Decisiones de diseño

- CustomTkinter queda como estándar visual oficial de GuiCore.
- GuiCore toma inspiración visual de SmartFilter, pero no copia lógica de SmartFilter.
- El tema claro/oscuro no se aplica en caliente; se guarda y se reinicia la app para evitar congelamientos.
- GuiCore no ejecuta motores, no escanea archivos, no interpreta eventos y no conoce reglas de negocio.
- Cada herramienta decide cómo persistir configuración real; GuiCore solo ofrece preferencias visuales comunes y callbacks.

### Validación

Validación esperada para esta versión:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

Resultado de cierre:

```text
Ran 31 tests
OK
```
