# Plan de implementación GuiCore 1.1.0

Este plan evita una reescritura grande y permite validar una capacidad por vez.

---

## Fase 0 — Protección de versiones

### Acciones

- mantener intacta la release y tag `v1.0.0`;
- crear rama `feature/guicore-1.1`;
- establecer versión de desarrollo `1.1.0.dev0`;
- no publicar `latest` durante desarrollo;
- producir wheels con versión de desarrollo o prerelease;
- mantener URLs y hashes fijados en proyectos actuales.

### Cierre

```text
SharedCode 1.0.0 continúa instalable y verificable.
Ningún proyecto actual cambia de dependencia.
```

---

## Fase 1 — ResultsTable robusta

Estado: **completada y validada en Windows (43/43 pruebas en el cierre de fase).**

### Trabajo

- corregir `command=None`;
- añadir helper testeable para opciones de heading;
- construir `ResultsTable(enable_sorting=False)` en prueba visual;
- aislar nombres de estilo por instancia;
- añadir altura visible declarativa;
- añadir estado vacío sin filas falsas.

### Pruebas

- sorting activado;
- sorting desactivado;
- columnas no ordenables;
- dos tablas simultáneas;
- tooltip activado/desactivado;
- tabla sin filas;
- smoke test Windows en VM.

### Consumidor de validación

ShadowBackup.

---

## Fase 2 — Perfiles de layout

Estado: **implementada en `1.1.0.dev1`; pendiente validación visual final en Windows.**

### Trabajo

- crear `GuiLayoutProfile`;
- perfiles `compact`, `standard`, `comfortable`;
- conectar perfil con fuentes, controles y padding;
- documentar perfiles personalizados.

### Pruebas

- normalización;
- serialización;
- valores mínimos;
- demo visual en 1280×720 y escalado de Windows.

---

## Fase 3 — Sidebar y footer

Estado: **implementada en `1.1.0.dev2`; pendiente validación visual final en Windows.**

### Trabajo

- crear `SidebarConfig`;
- header opcional;
- footer una/dos columnas;
- footer compacto;
- etiqueta de menú opcional;
- acciones primarias fijas;
- scrollbar público/configurable;
- eliminar necesidad de manipular hijos internos.

### Pruebas

- footer vacío;
- una columna;
- dos columnas;
- acciones deshabilitadas;
- sidebar corto con scroll;
- sidebar en resolución baja.

### Consumidores

ShadowBackup primero; SmartFilter después.

---

## Fase 4 — Controles compactos

Estado: **implementada en `1.1.0.dev3`; pendiente validación visual final en Windows.**

### Trabajo

- extender controles existentes con parámetros aditivos;
- crear `LabeledComboAction`;
- API común de `set_enabled`;
- callbacks de cambio;
- tamaños derivados del perfil.

### Pruebas

- lectura/escritura;
- habilitar/deshabilitar;
- etiqueta oculta;
- botón auxiliar;
- modo archivo/carpeta;
- compact/standard.

### Cierre

SmartFilter puede eliminar las clases `_Compact*`.

---

## Fase 5 — Tarjetas y componentes de estado

Estado: **Fase 5 completa en `1.1.0.dev5`: tarjetas flexibles, colapso, estados, métricas semánticas y tooltips genéricos.**

### Trabajo

- ampliar `SectionCard`;
- crear `CollapsibleSectionCard`;
- crear cabecera con acciones;
- crear `KeyValueTable`;
- crear `EmptyState`;
- crear `MetricCard` y `MetricStrip`;
- crear `WidgetTooltip`.

### Pruebas

- expandir/contraer;
- restaurar;
- pesos de grid;
- estado vacío/carga/error;
- métricas semánticas;
- tooltip destruido correctamente.

---

## Fase 6 — Operaciones largas

### Trabajo

- crear `GuiTaskRunner`;
- contexto de progreso y cancelación;
- callbacks al hilo principal;
- bloqueo temporal de controles;
- throttling de progreso;
- protección contra operación duplicada.

### Pruebas

- éxito;
- error;
- cancelación;
- progreso determinado;
- progreso indeterminado;
- operación duplicada;
- cierre de ventana durante ejecución;
- ningún acceso a Tk desde worker.

---

## Fase 7 — Demo y documentación

### Demo oficial

```text
examples/guicore_1_1_showcase.py
```

Debe demostrar:

- perfil compacto;
- sidebar con acciones fijas;
- footer de dos columnas;
- controles compactos;
- tarjeta plegable;
- métricas;
- tabla con estados;
- tarea simulada cancelable;
- preferencias basic/advanced.

### Documentación

- quickstart 1.1;
- mapa de componentes;
- guía de migración 1.0 → 1.1;
- contrato público de GuiCore 1.1;
- ejemplos completos.

---

## Fase 8 — Validación con ShadowBackup

ShadowBackup será el primer consumidor porque su GUI es pequeña y expone
rápidamente defectos estructurales.

### Criterios

- no acceder a `sidebar.footer_buttons`;
- no acceder a `.frame` para cambiar pesos;
- no modificar `_scrollbar`;
- no definir alturas manuales repetidas;
- no implementar su propio ciclo de worker;
- dejar operativo ShadowBackup desde la GUI;
- seguir funcionando sin GUI.

---

## Fase 9 — Prerelease

Publicar:

```text
v1.1.0a1
```

Incluye:

- wheel;
- SHA-256;
- changelog;
- matriz de pruebas;
- demo;
- advertencia de prerelease.

ShadowBackup podrá fijar temporalmente esa versión en una rama de prueba.

---

## Fase 10 — Migración gradual de SmartFilter

Migrar un bloque por commit y prueba:

```text
1. controles compactos
2. tooltips
3. sidebar/footer
4. cards plegables
5. métricas
6. estados vacíos
7. operación larga
```

No eliminar código anterior hasta validar el reemplazo.

---

## Fase 11 — Release estable

Publicar `v1.1.0` únicamente cuando:

- todos los tests de SharedCode pasan;
- demo validada Windows/Linux;
- ShadowBackup validado;
- SmartFilter validado en los bloques migrados;
- wheel reproducible;
- SHA-256 registrado;
- API pública documentada;
- la suite acumulativa del contrato 1.1 pasa sin fallos.

---

## Matriz de riesgo

| Riesgo | Mitigación |
|---|---|
| Romper proyectos actuales | Dependencia exacta 1.0.0 y release congelada. |
| Extraer lógica de negocio | Revisar límites en cada PR/commit. |
| Reescritura demasiado grande | Fases pequeñas y consumidor real por fase. |
| Tests sin entorno gráfico | Helpers puros + smoke tests en VM. |
| API demasiado específica de SmartFilter | Validar primero con ShadowBackup y demo neutral. |
| Duplicar APIs | Extender componentes existentes antes de crear nuevos. |
| Personalización visual excesiva | Perfiles simples y preferencias none/basic/advanced. |

---

## Primer commit de código recomendado

```text
fix(gui): make ResultsTable safe when sorting is disabled
```

Ese commit debe contener solamente:

- corrección de `_apply_columns`;
- helper/test unitario;
- smoke test visual;
- changelog de desarrollo.

No debe incluir todavía perfiles, sidebar ni nuevos widgets.
