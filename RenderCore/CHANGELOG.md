# Changelog

## 0.10.0 - Document highlight pro

- Agrega el perfil HTML `document_highlight_pro` sin retirar `document_highlight`.
- Eleva el visor documental al lenguaje visual aprobado de SmartDisk: hero profesional, métricas, tarjetas y fondo con profundidad.
- Agrega sidebar sticky con filtro local, términos, contadores, ubicaciones navegables, índice de secciones y acciones.
- Agrega navegador sticky con progreso, ubicación actual, atajos de teclado y salto exacto entre coincidencias.
- Agrega secciones plegables para páginas, hojas, párrafos y tablas sin modificar el documento original.
- Mantiene el resaltado tolerante a mayúsculas y tildes y la validación estricta mediante JsonContractCore.
- Mantiene `document_highlight` como perfil funcional estable para comparación y rollback visual.

## 0.9.0 - Document highlight

- Agrega el perfil HTML interactivo `document_highlight`.
- Agrega renderizado desde contratos en memoria mediante `render_report_data()`.
- Agrega navegación por coincidencias, contador, filtros por término y apertura del original.
- Admite bloques neutrales de línea, párrafo y tabla.
- Mantiene validación estricta obligatoria por JsonContractCore.
- No interpreta formatos propietarios dentro de RenderCore; las herramientas entregan el modelo neutral.

## 0.8.1 - Stable base freeze

- Congela RenderCore como primera base estable aprobada.
- Mantiene el comportamiento de `0.8.0 - Export polish` sin cambios de contrato.
- Agrega documentación de baseline estable, pruebas oficiales y roadmap de perfiles.
- Agrega scripts auxiliares para renderizar JSON reales y limpiar outputs locales.
- Actualiza `tool_manifest.json` con capacidades estables y perfil completo `disk_smart`.
- Mantiene `JsonContractCore` como requisito obligatorio.
- Mantiene bloqueado cualquier modo legacy, local, none o fallback permisivo.

## 0.8.0 - Export polish

- Mejora el TXT para que sea una salida ejecutiva/técnica legible, especialmente para `disk_smart`.
- Agrega resumen de contexto, estado general, métricas principales, discos y referencia a tablas técnicas en TXT.
- Mejora CSV agregando `report_summary.csv` junto a las tablas normalizadas.
- Mejora XLSX con hoja `Resumen` más presentable, hoja `Vista discos` para Smart Disk, filtros automáticos, encabezados congelados, anchos acotados y estilos por estado.
- Mantiene `JsonContractCore` como requisito obligatorio.
- No agrega modo legacy ni normalización permisiva.

## 0.7.3 - SmartDisk sidebar structural sticky fix

- Reworked the Smart Disk HTML profile so the left panel uses a sticky inner wrapper inside a full-height sidebar column.
- Removed the previous sticky behavior from the grid item itself, which could stop early depending on viewport size and layout height.
- Adjusted overflow handling to avoid breaking sticky positioning while preserving table scroll containers.
- Kept responsive behavior for narrow screens.

## 0.7.2 - Sticky sidebar refinement

- Added sticky left sidebar behavior for the Smart Disk professional HTML profile.
- Sidebar now stays available while scrolling long technical sections.
- Sidebar uses its own vertical scroll when viewport height is limited.
- Reset sticky behavior automatically on narrow/mobile layouts.

## 0.7.1 - Layout responsive fix

- Ajusta el perfil HTML `disk_smart` para evitar desbordes horizontales.
- Reduce el ancho de la barra lateral en escritorio.
- Mejora grids adaptativos para métricas, tarjetas de disco y detalles.
- Encapsula tablas anchas dentro de scroll horizontal propio.
- Mantiene `JsonContractCore` como requisito estricto.

## 0.7.0 - Pro HTML profile for Smart Disk

- Added dedicated `disk_smart.html.j2` standalone professional HTML profile.
- Updated `disk_smart` registry mapping to use the new pro template instead of the legacy Toolkit-style profile.
- Kept normalized table extraction from v0.6 for CSV/XLSX.
- HTML now includes hero dashboard, metric cards, disk cards, life bars, local search, and collapsible normalized tables.

## 0.6.0 - Normalized tables

- Added profile-aware render normalization for `disk_smart`.
- CSV/XLSX exports now split Smart Disk data into clean tables: disks, ATA attributes, NVMe metrics and alternate SMART devices.
- Kept strict contract behavior: JsonContractCore remains required and RenderCore does not repair invalid contracts.

## 0.5.0 - HTML professional profiles

- Added a dedicated `category_database` HTML profile for Smart Filter category databases.
- Reworked the generic HTML template with a stronger visual hierarchy, metrics, brief cards and improved tables.
- Kept strict JsonContractCore validation: visual improvements do not downgrade the JSON contract.
- Updated smoke validator to match the strict shared contract shape used by configuration documents.

## 0.4.1 - Strict contract for reports and configs

- `JsonContractCore` pasa a ser obligatorio para renderizar.
- RenderCore trabaja en modo estricto siempre.
- Se eliminan modos permisivos y legacy.
- RenderCore acepta documentos válidos con `report_type`, `config_type` o `file_type` según contrato.

## 0.4.0 - Strict contract foundation

- Se elimina fallback local/permisivo.
- `JsonContractCore` pasa a ser autoridad del contrato.

## 0.3.0 - JsonContractCore bridge

- Puente opcional con `JsonContractCore`.
- Esta versión fue superada porque permitía fallback local.

## 0.2.0 - SharedCode integration

- Estructura lista para integrarse como `SharedCode/RenderCore`.

## 0.1.0 - Initial RenderCore base

- Primera base desacoplada de Toolkit con HTML, TXT, CSV y XLSX.
