# Perfil `document_highlight` — RenderCore 0.9.0

Este perfil genera un visor HTML temporal para documentos convertidos a una estructura neutral.
RenderCore no interpreta PDF, DOCX o XLSX: recibe secciones y bloques ya preparados por la herramienta consumidora.

## Responsabilidades

- Validar el contrato estándar mediante JsonContractCore.
- Renderizar páginas, párrafos, líneas y tablas.
- Resaltar términos sin distinguir mayúsculas ni tildes comunes.
- Calcular coincidencias visibles en el documento renderizado.
- Navegar con Anterior, Siguiente, flechas o F3.
- Filtrar la navegación por término desde el sidebar.
- Mantener el archivo original sin modificaciones.

## Datos principales

```text
data.document
  title
  source_path
  source_uri
  format
  reader
  truncated
  sections[]

data.highlight
  category_name
  terms[]
  occurrence_count
  locations[]
```

Los bloques admitidos en la primera versión son `line`, `paragraph` y `table`.
La representación es semántica: conserva el contenido y su estructura recuperable, pero no intenta reproducir píxel a píxel el diseño original.
