# Roadmap de perfiles RenderCore

RenderCore puede renderizar cualquier JSON válido del contrato estándar, pero los mejores resultados aparecen cuando cada `report_type` o `config_type` tiene un perfil propio.

## Perfil estable actual

### `disk_smart`

Estado: aprobado.

Incluye:

- HTML pro con sidebar sticky.
- TXT ejecutivo/técnico.
- CSV normalizado.
- XLSX presentable.
- Tablas específicas para discos, atributos ATA, métricas NVMe y dispositivos alternativos.

## Próximos perfiles

### `event_health`

Prioridad alta.

Objetivo:

- Timeline o agrupación por severidad.
- Cards de eventos críticos/advertencias.
- Tabla compacta de eventos.
- TXT enfocado en incidencias relevantes.
- XLSX con hojas por severidad/origen.

### `storage_analyzer`

Prioridad alta.

Objetivo:

- Resumen de uso por unidad/carpeta.
- Top carpetas/archivos grandes.
- Barras visuales de ocupación.
- CSV/XLSX con tablas limpias para análisis.

### `category_database`

Prioridad media-alta.

Objetivo:

- HTML ya tiene perfil pro inicial.
- Cerrar TXT ejecutivo.
- CSV por categorías/términos/exclusiones/campos.
- XLSX con hojas por categoría y resumen.

## Regla

Un perfil nuevo no debe debilitar el contrato ni agregar excepciones globales.

Si un tipo de JSON necesita presentación especial, se agrega un normalizador o template propio para ese perfil.
