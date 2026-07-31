# Mapa de extracción SmartFilter → GuiCore 1.1.0

Este mapa se basa en la versión pública SmartFilter 1.0.33 y SharedCode 1.0.0.

La regla no es copiar código completo. Cada pieza se clasifica como:

```text
Extraer     → patrón genérico que debe vivir en GuiCore.
Adaptar     → reutilizar la idea y convertirla en API general.
Mantener    → lógica o contenido exclusivo de SmartFilter.
Eliminar    → duplicación que desaparecerá tras migrar.
```

---

## 1. Controles compactos

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `_CompactEntry` | `LabeledEntry` | Adaptar opciones de altura, ancho, etiqueta visible y rol de fuente. |
| `_CompactCombo` | `LabeledComboBox` | Adaptar densidad, ancho y fuente desplegable. |
| `_CompactPathPicker` | `PathPicker` | Adaptar botón auxiliar, tamaños y callback. |
| `_CompactSwitch` | `LabeledSwitch` | Adaptar modo compacto y habilitación estable. |
| `_CompactComboAction` | `LabeledComboAction` | Extraer como componente nuevo. |
| constantes `SIDEBAR_CONTROL_*` | perfiles de layout | Adaptar como tokens, no copiar constantes globales. |

### Resultado esperado en SmartFilter

Eliminar las cinco clases `_Compact*` y construir el formulario usando únicamente
exports públicos de GuiCore.

---

## 2. Sidebar y footer

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `_build_footer_action_bar` | `FixedActionBar` / acciones primarias del sidebar | Extraer estructura; comandos quedan en SmartFilter. |
| `_build_footer_menu` | footer configurable de `Sidebar` | Adaptar una/dos columnas, etiqueta y densidad. |
| `_style_footer_menu` | perfil y tokens de GuiCore | Adaptar estilo; no copiar lógica de color específica. |
| `_apply_smartfilter_chrome` | `layout_profile` + APIs públicas | Reemplazar manipulación interna de widgets. |
| ajuste de `_scrollbar.width` | `SidebarConfig.scrollbar_width` | Extraer como configuración pública. |
| acciones Buscar/Limpiar | SmartFilter | Mantener comandos; GuiCore solo crea la barra. |
| Importar/Categorías/etc. | SmartFilter | Mantener acciones y etiquetas; GuiCore organiza. |

### Resultado esperado

SmartFilter no debe destruir hijos de `sidebar.footer_frame`, usar `pack` interno
ni acceder a `_scrollbar`.

---

## 3. Tooltips

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `SmartTooltip` | `WidgetTooltip` | Extraer y hacer dependiente de tema/fuente de GuiCore. |
| `_add_sidebar_tooltip` | helper `app.add_tooltip` opcional | Adaptar. |
| textos concretos | SmartFilter | Mantener. |

### Resultado esperado

Eliminar `smart_filter/ui/tooltips.py` después de migrar sus usos.

---

## 4. Tarjetas plegables

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `summary_panel_collapsed` y métodos asociados | `CollapsibleSectionCard` | Extraer comportamiento. |
| `detail_panel_collapsed` y métodos asociados | `CollapsibleSectionCard` | Extraer comportamiento. |
| barras compactas de restauración | `CollapsedCardBar` interno | Adaptar. |
| texto de resumen de búsqueda | SmartFilter | Mantener. |
| detalle de archivo seleccionado | SmartFilter | Mantener. |

### Resultado esperado

SmartFilter deja de guardar manualmente `grid_info`, crear tarjetas paralelas y
usar `grid_remove()` para simular el colapso.

---

## 5. Cabeceras con acciones

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| cabecera de resultados con botones | `CardHeaderActions` | Extraer estructura declarativa. |
| Abrir/Carpeta/Destacado/Exportar | SmartFilter | Mantener acciones. |
| mostrar/ocultar barra de acciones | API genérica de estado | Adaptar. |

---

## 6. Métricas

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `_build_metric_chips` | `MetricStrip` + `MetricCard` | Extraer presentación. |
| `_metric_size_tokens` | perfiles/tamaños de métrica | Adaptar. |
| `_metric_colors` | estilos semánticos comunes | Adaptar `neutral/accent/success/warning/danger`. |
| `build_metric_summary_values` | SmartFilter | Mantener interpretación. |
| `build_incident_status_palette` | parcialmente GuiCore | Extraer semántica visual general; mantener reglas de incidencias si son específicas. |

### Resultado esperado

GuiCore recibe valores ya calculados. Nunca debe importar `SearchSummary`.

---

## 7. Estados vacíos y de operación

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| filas falsas de “listo”, “buscando”, “sin resultados” | `EmptyState` / `TableState` | Adaptar. |
| texto del criterio y búsqueda | SmartFilter | Mantener. |
| errores de búsqueda | SmartFilter + diálogos GuiCore | Mantener significado. |

### Resultado esperado

La tabla contiene datos reales; los estados visuales no se mezclan con filas de
negocio.

---

## 8. Operaciones en segundo plano

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `Thread(..., daemon=True)` | `GuiTaskRunner` | Extraer ciclo visual. |
| `_publish_search_progress` | publicador de progreso | Adaptar y generalizar. |
| `_flush_search_progress` | limitador de actualizaciones | Extraer internamente. |
| `_set_search_interaction_locked` | registro de controles bloqueables | Adaptar. |
| `Event` de cancelación | contexto de cancelación cooperativa | Extraer. |
| `run_search` | SmartFilter | Mantener. |
| `SearchCancelledError` | SmartFilter | Mantener o traducir mediante callback. |
| aplicación del `SearchSummary` | SmartFilter | Mantener. |

### Resultado esperado

SmartFilter aporta el worker y callbacks; GuiCore administra hilo, progreso,
cancelación y restauración visual.

---

## 9. Ventanas secundarias

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| `window_icon.py` propio | `gui_core.windows.window_icon` | Eliminar duplicación tras validar. |
| cards visuales de About/Help | posible componente futuro | Mantener en 1.1.0 salvo repetición comprobada. |
| `CategoryWindow` | SmartFilter | Mantener completa. |
| `ProductSettingsWindow` | SmartFilter | Mantener configuración funcional. |
| `FileTypeSelectionWindow` | SmartFilter | Mantener lógica y contenido. |
| `SecondaryWindow` | GuiCore | Ya reutilizado correctamente. |

No todo lo visual debe extraerse de inmediato. Las ventanas de ayuda y acerca de
pueden seguir en SmartFilter hasta comprobar un segundo uso real.

---

## 10. Colores y preferencias

| Origen SmartFilter | Destino GuiCore | Tratamiento |
|---|---|---|
| cálculo de acento/superficie personalizado | estilos de GuiCore | Auditar y consolidar solo lo genérico. |
| selección de colores | preferencias `advanced` | Mantener disponible. |
| necesidad de GUI simple | modos `none/basic` | Agregar. |
| colores de categorías | SmartFilter | Mantener. |

El objetivo no es eliminar colores, sino evitar que dominen la estructura base.

---

## 11. Elementos que permanecen en SmartFilter

- `SearchFormState`;
- `SearchSummary`;
- categorías;
- filtros;
- exclusiones;
- readers;
- escaneo;
- importación/exportación;
- acciones sobre archivos;
- destacado HTML;
- cálculo y significado de métricas;
- mensajes funcionales;
- reglas de configuración del producto.

---

## 12. Orden recomendado de migración

1. Publicar GuiCore 1.1.0 prerelease.
2. Validar todos los componentes con la demo oficial.
3. Migrar ShadowBackup como consumidor pequeño.
4. Corregir APIs detectadas en ShadowBackup.
5. Migrar SmartFilter por bloques:
   - controles;
   - tooltip;
   - footer/sidebar;
   - tarjetas plegables;
   - métricas;
   - operaciones largas;
   - estados vacíos.
6. Eliminar código duplicado solo después de cada prueba visual y funcional.
