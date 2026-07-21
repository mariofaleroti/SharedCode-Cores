# Perfil `document_highlight_pro` — RenderCore 0.10.0

## Objetivo

Presentar un documento neutral ya interpretado por la herramienta consumidora como una vista HTML profesional, navegable y segura.

## Responsabilidades

RenderCore recibe:

- metadatos del archivo;
- secciones neutrales;
- bloques de línea, párrafo o tabla;
- términos que deben destacarse.

RenderCore entrega:

- cabecera visual tipo ecosistema;
- métricas de coincidencias, términos, secciones y formato;
- sidebar sticky con filtro, términos, ubicaciones, índice y acciones;
- navegación Anterior/Siguiente con progreso y atajos;
- secciones plegables y resaltado tolerante a tildes y mayúsculas.

## Límites

- No lee directamente PDF, DOCX, XLSX ni otros formatos propietarios.
- No clasifica archivos ni decide qué términos buscar.
- No modifica el archivo original.
- No relaja el contrato JSON ni ofrece compatibilidad legacy.

## Perfiles

- `document_highlight`: base funcional estable.
- `document_highlight_pro`: presentación profesional recomendada para Smart Filter.
