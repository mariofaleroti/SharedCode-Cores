# Contrato funcional de GuiCore 1.1.0

Estado: **línea base de diseño aprobada para implementación**.

Este documento define el alcance de GuiCore 1.1.0. La versión 1.0.0 permanece
congelada y disponible para los proyectos que todavía la consumen.

---

## 1. Objetivo

GuiCore 1.1.0 debe permitir que una herramienta nueva construya una interfaz
profesional, compacta y adaptable sin reconstruir en cada proyecto:

- la densidad visual;
- el sidebar;
- el footer;
- las acciones principales fijas;
- las proporciones entre paneles;
- las secciones plegables;
- los estados vacíos;
- los tooltips;
- las métricas visuales;
- el ciclo visual de operaciones largas.

La herramienta concreta conserva siempre su motor, configuración, contratos y
reglas de negocio.

```text
Proyecto
├─ motor propio
├─ configuración propia
├─ contratos propios
├─ controladores propios
└─ GUI declarada con GuiCore
```

---

## 2. Compatibilidad obligatoria

GuiCore 1.1.0 será una evolución **aditiva y retrocompatible**.

### Garantías

1. No se elimina ni renombra ninguna API pública de 1.0.0.
2. Los valores predeterminados nuevos deben reproducir el comportamiento visual
   de 1.0.0.
3. Las nuevas capacidades son opcionales.
4. Los tests públicos de 1.0.0 deben continuar pasando sin modificaciones.
5. Los proyectos migran individualmente.
6. El tag, release, wheel y SHA-256 de SharedCode 1.0.0 no se modifican.
7. Durante desarrollo se utilizará `1.1.0.devN`; las pruebas públicas podrán usar
   prereleases `1.1.0aN` o `1.1.0bN`.
8. La primera release estable nueva será `1.1.0`.

### Predeterminados compatibles

```python
layout_profile = "standard"
visual_preferences = "advanced"
sidebar_footer_layout = "single_column"
```

Una aplicación existente que no use las opciones nuevas debe conservar su
estructura actual.

---

## 3. Límites

### GuiCore sí contiene

- shell visual de aplicación;
- perfiles de densidad;
- sidebar y footer configurables;
- controles de formulario reutilizables;
- tarjetas y cabeceras;
- tablas y estados vacíos;
- barras de acciones;
- tooltips;
- métricas visuales genéricas;
- progreso y estado;
- ejecución visual segura de callbacks en segundo plano;
- diálogos y ventanas secundarias;
- preferencias visuales opcionales.

### GuiCore no contiene

- búsqueda de archivos;
- categorías o exclusiones de SmartFilter;
- comandos Git;
- tareas programadas de Windows/Linux;
- análisis de discos;
- lectores de documentos;
- exportaciones específicas;
- reglas de negocio;
- contratos JSON propios de cada herramienta.

---

## 4. Perfiles de layout

GuiCore incorporará perfiles reutilizables:

```text
compact
standard
comfortable
```

Un perfil define únicamente tokens visuales:

- altura de controles;
- altura de botones;
- fuentes por rol;
- padding horizontal y vertical;
- separación entre widgets;
- densidad de footer;
- ancho recomendado del scrollbar;
- radios y márgenes de tarjetas.

No define contenido ni comportamiento del proyecto.

### API prevista

```python
GuiAppConfig(
    ...,
    layout_profile="compact",
)
```

También se expondrá un modelo inmutable para perfiles personalizados:

```python
GuiLayoutProfile(
    name="compact",
    control_height=26,
    action_height=28,
    menu_button_height=22,
    sidebar_padding=12,
    widget_gap=4,
    scrollbar_width=8,
)
```

Los valores concretos se validarán visualmente antes de congelar la API.

---

## 5. Sidebar y footer

El sidebar debe dejar de ser una estructura rígida.

### Capacidades

- encabezado visible u oculto;
- formulario desplazable;
- scrollbar configurable;
- acciones primarias fijas fuera del scroll;
- footer compacto;
- footer de una o dos columnas;
- secciones con padding derivado del perfil;
- acciones declarativas;
- posibilidad de ocultar la etiqueta `MENÚ`;
- acceso estable a controles sin manipular widgets internos.

### API prevista

```python
SidebarConfig(
    header_visible=True,
    scrollable=True,
    fixed_actions=True,
    footer_columns=2,
    footer_label_visible=False,
    compact_footer=True,
)
```

```python
app.add_sidebar_primary_actions(
    (
        GuiActionButton("Ejecutar", "run"),
        GuiActionButton("Limpiar", "clear", style="secondary"),
    )
)
```

El proyecto aporta comandos; GuiCore crea y administra la estructura visual.

---

## 6. Controles de formulario

Los controles actuales seguirán disponibles, pero ganarán opciones aditivas.

### Opciones comunes

- `height`;
- `width`;
- `label_visible`;
- `label_role`;
- `font_role`;
- `padding`;
- `compact`;
- `state`;
- botón auxiliar opcional;
- callback de cambio;
- métodos estables para habilitar/deshabilitar.

### Componentes afectados

- `LabeledEntry`;
- `LabeledComboBox`;
- `PathPicker`;
- `LabeledCheckBox`;
- `LabeledSwitch`;
- `ActionButton`;
- `ButtonRow`.

### Nuevo componente previsto

```python
LabeledComboAction
```

Combina un combo y un botón auxiliar sin que cada proyecto tenga que construir
su propio frame y calcular anchos manualmente.

---

## 7. Tarjetas y contenido

`SectionCard` continúa disponible.

### Mejoras aditivas

- acciones declarativas en la cabecera;
- altura mínima;
- peso de crecimiento;
- `sticky` configurable;
- contenido principal/secundario;
- cabecera configurable;
- posibilidad de ocultar título o subtítulo sin hacks.

### Nuevo componente

```python
CollapsibleSectionCard
```

Responsabilidades:

- expandir y contraer contenido;
- mostrar una barra compacta cuando está contraído;
- texto de resumen opcional;
- callback de cambio;
- persistencia opcional mediante callback externo;
- no conocer el significado del contenido.

### API prevista

```python
card = app.add_collapsible_card(
    title="Resumen",
    subtitle="Estado de la última operación",
    collapsed=False,
    row_weight=1,
    min_height=180,
)
```

---

## 8. Tablas y estados

### ResultsTable

Correcciones obligatorias:

- no pasar `command=None` a `ttk.Treeview.heading`;
- soportar correctamente `enable_sorting=False`;
- pruebas de construcción real del widget;
- estilos aislados por instancia;
- altura visible declarativa;
- mejor control del scrollbar;
- contrato explícito de filas vacías.

### Nuevos componentes

```text
KeyValueTable
EmptyState
TableState
```

`KeyValueTable` mostrará pares campo/valor como estado operativo.

`EmptyState` mostrará:

- título;
- descripción;
- acción opcional;
- estado `empty`, `loading`, `error` o `ready`.

`TableState` permitirá mostrar un estado sin insertar filas falsas dentro de los
datos reales.

---

## 9. Métricas

GuiCore incorporará componentes visuales, no interpretación de métricas.

```text
MetricCard
MetricStrip
```

Cada métrica declara:

- clave;
- título;
- valor;
- estilo semántico opcional;
- tooltip opcional.

El proyecto decide qué significa `errores`, `repositorios`, `archivos` o
`coincidencias`.

```python
MetricItem(
    key="errors",
    title="Incidencias",
    value=3,
    semantic="danger",
)
```

---

## 10. Tooltips

Se añadirá un tooltip genérico para widgets CustomTkinter/Tkinter.

```python
WidgetTooltip(
    widget,
    text,
    delay_ms=800,
    visible_ms=4000,
    wraplength=320,
)
```

Debe:

- enlazar de forma defensiva el árbol de widgets;
- ocultarse con click, salida, scroll o movimiento;
- respetar tema y fuente;
- evitar salirse de la pantalla;
- destruirse sin dejar callbacks pendientes.

El tooltip de celdas de `ResultsTable` seguirá siendo una especialización
interna.

---

## 11. Operaciones largas

GuiCore no ejecutará motores, pero administrará el ciclo visual de una operación.

### Nuevo servicio previsto

```python
GuiTaskRunner
```

Responsabilidades:

- ejecutar un callback en un hilo de trabajo;
- devolver resultado/error al hilo de la GUI;
- publicar progreso determinado o indeterminado;
- cancelación cooperativa;
- evitar actualizaciones visuales desde el worker;
- bloquear y restaurar controles registrados;
- evitar operaciones duplicadas;
- limitar la frecuencia de actualizaciones de progreso;
- exponer callbacks `on_success`, `on_error`, `on_cancel`.

El callback del proyecto recibe un contexto genérico:

```python
def worker(context):
    context.publish_progress(40, "Procesando...")
    context.throw_if_cancelled()
    return result
```

GuiCore no interpreta `result`.

---

## 12. Preferencias visuales

Los colores se mantienen, pero dejan de ser obligatoriamente protagonistas.

```text
none
basic
advanced
```

### none

- sin ventana común de preferencias visuales;
- el proyecto usa los valores declarados.

### basic

- tema;
- fuente;
- densidad.

### advanced

- todas las preferencias de 1.0.0;
- acento;
- superficie;
- fuente;
- tamaño;
- densidad;
- tema.

El valor predeterminado será `advanced` para conservar compatibilidad.

---

## 13. API de aplicación prevista

```python
app = GuiAppWindow(
    GuiAppConfig(
        app_name="ShadowBackup",
        app_version="1.0.0",
        layout_profile="compact",
        visual_preferences="basic",
        sidebar=SidebarConfig(
            fixed_actions=True,
            footer_columns=2,
            compact_footer=True,
        ),
    )
)
```

```python
status_card = app.add_content_card(
    "Estado",
    row_weight=3,
    min_height=360,
    sticky="nsew",
)
```

```python
app.run_task(
    worker=run_backup,
    controls=(save_button, install_button),
    on_success=show_result,
    on_error=show_error,
)
```

Los nombres finales podrán ajustarse durante implementación, pero no se podrá
reducir el alcance funcional aquí definido sin una decisión explícita.

---

## 14. Criterios de aceptación

GuiCore 1.1.0 no se considera listo hasta cumplir:

1. Todos los tests de 1.0.0 continúan pasando.
2. `ResultsTable(enable_sorting=False)` abre realmente.
3. Una demo compacta funciona en Windows y Linux.
4. La GUI de ShadowBackup deja de modificar internamente sidebar/footer.
5. ShadowBackup puede declarar proporciones de paneles sin acceder a `.frame`.
6. SmartFilter puede eliminar sus clases `_Compact*`.
7. SmartFilter puede eliminar su implementación propia de tooltip.
8. SmartFilter puede reemplazar su footer manual por GuiCore.
9. Las operaciones largas no actualizan Tk desde el worker.
10. Ningún componente nuevo contiene lógica de SmartFilter o ShadowBackup.
