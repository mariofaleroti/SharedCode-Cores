# ToolRuntimeCore

ToolRuntimeCore es un core compartido del ecosistema **SharedCode** para crear un contexto de ejecución neutral para herramientas externas.

Su objetivo es evitar que cada herramienta reinvente la misma lógica para resolver rutas, crear carpetas de salida, generar identificadores de ejecución y exponer metadatos básicos.

## Objetivo

ToolRuntimeCore permite resolver de forma consistente:

- nombre técnico de la herramienta
- versión de la herramienta
- carpeta base
- carpeta `output`
- carpeta `logs`
- carpeta `temp`
- carpeta `runtime`
- `run_id`
- fecha/hora de inicio en UTC
- metadatos base para contratos JSON

## Regla de arquitectura

```text
ToolRuntimeCore no sabe nada de Toolkit.
ToolRuntimeCore no sabe nada de ShadowBackup.
ToolRuntimeCore no sabe nada de Smart Filter.
ToolRuntimeCore solo crea contexto de ejecución neutral.
```

## Estructura

```text
ToolRuntimeCore/
├─ README.md
├─ examples/
│  └─ basic_runtime_context_example.py
├─ tests/
│  └─ test_tool_runtime_core_behavior.py
└─ tool_runtime_core/
   ├─ __init__.py
   ├─ constants.py
   ├─ models.py
   └─ runtime.py
```

## Uso básico

```python
from tool_runtime_core import create_runtime_context

runtime = create_runtime_context(
    tool_name="ShadowBackup",
    tool_version="0.1.0",
    base_dir=".",
)

print(runtime.run_id)
print(runtime.output_dir)
print(runtime.logs_dir)
print(runtime.get_log_path())
```

Por defecto se crean estas carpetas:

```text
output/
├─ logs/
├─ temp/
└─ runtime/
```

## Metadatos para JSON

El contexto puede generar metadatos reutilizables:

```python
meta = runtime.to_meta(
    module_name="Scanner",
    file_type="result",
)
```

Ejemplo de salida:

```json
{
  "tool_name": "ShadowBackup",
  "tool_version": "0.1.0",
  "run_id": "20260630_150405_ab12cd34",
  "started_at_utc": "2026-06-30T15:04:05Z",
  "started_at_local": "2026-06-30T12:04:05-03:00",
  "local_timezone": "-03",
  "local_utc_offset": "-03:00",
  "module_name": "Scanner",
  "file_type": "result"
}
```

## Decisiones de diseño

```text
DESIGN: ToolRuntimeCore resuelve contexto, no ejecuta procesos externos.
DESIGN: Las rutas se resuelven a Path absolutos para evitar ambigüedades.
DESIGN: El run_id combina timestamp UTC y sufijo aleatorio corto.
DESIGN: La fecha de inicio se normaliza a UTC y se serializa como ISO-8601 con sufijo Z.
NOTE: DateTimeCore centraliza el formato para evitar mezclar Z, +00:00 y epoch sin nombre explícito.
NOTE: El nombre de herramienta se normaliza para uso seguro en nombres de archivo.
NOTE: Las herramientas pueden desactivar la creación automática de carpetas.
```

## Validaciones

Comandos recomendados:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

Estado actual:

```text
compileall: OK
unittest: OK
```
