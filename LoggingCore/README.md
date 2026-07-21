# LoggingCore

LoggingCore es un core compartido neutral para registrar eventos de ejecución dentro del ecosistema.

Su objetivo no es reemplazar la lógica propia de cada herramienta, sino ofrecer una base común para:

- registrar eventos humanos en archivo de log;
- recolectar advertencias y errores estructurados;
- generar entradas compatibles con `diagnostics` y `errors` del contrato JSON estándar;
- mantener un comportamiento simple, predecible y testeable.

## Rol dentro del ecosistema

```text
La herramienta ejecuta su lógica.
LoggingCore registra lo que pasó.
JsonContractCore valida/guarda el contrato final.
Toolkit consume herramientas estables por manifest.
```

LoggingCore no sabe nada de Toolkit, ShadowBackup, Smart Filter ni otra herramienta concreta.

## Estructura

```text
LoggingCore/
├─ README.md
├─ examples/
│  └─ basic_logging_example.py
├─ tests/
│  └─ test_logging_core_behavior.py
└─ logging_core/
   ├─ __init__.py
   ├─ constants.py
   ├─ models.py
   ├─ logger.py
   ├─ writer.py
   └─ formatters.py
```

## Uso básico

```python
from pathlib import Path
from logging_core import create_logger

logger = create_logger(
    name="ExampleTool",
    log_path=Path("output/logs/example.log"),
)

logger.info("Scan started", code="SCAN_STARTED")
logger.warning(
    "Directory skipped",
    code="DIRECTORY_SKIPPED",
    context={"path": "C:/Temp/node_modules"},
)
logger.error(
    "Permission denied",
    code="PERMISSION_DENIED",
    context={"path": "C:/Protected"},
)

diagnostics = logger.get_diagnostics()
errors = logger.get_errors()
```

## Salida humana

El archivo de log se escribe en UTF-8 y usa líneas simples. Para lectura humana, el timestamp se muestra en hora local con separador visual:

```text
2026-06-30 09:30:10 -03:00 | INFO | ExampleTool | SCAN_STARTED | Scan started
2026-06-30 09:30:11 -03:00 | WARNING | ExampleTool | DIRECTORY_SKIPPED | Directory skipped | context={"path":"C:/Temp/node_modules"}
```

La entrada estructurada conserva `timestamp_utc` en formato estándar:

```text
2026-06-30T12:30:10Z
```

## Salida estructurada

LoggingCore puede producir entradas para el contrato JSON estándar:

```json
{
  "diagnostics": [
    {
      "level": "warning",
      "code": "DIRECTORY_SKIPPED",
      "message": "Directory skipped",
      "context": {
        "path": "C:/Temp/node_modules"
      },
      "source": "ExampleTool"
    }
  ],
  "errors": [
    {
      "code": "PERMISSION_DENIED",
      "message": "Permission denied",
      "context": {
        "path": "C:/Protected"
      },
      "source": "ExampleTool"
    }
  ]
}
```

## Validaciones recomendadas

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

## Decisiones de diseño

- LoggingCore es neutral.
- No ejecuta comandos externos.
- No renderiza reportes.
- No valida contratos JSON completos.
- No depende de Toolkit ni de herramientas concretas.
- Usa solo librería estándar de Python.
- Usa DateTimeCore para evitar formatos de fecha inconsistentes.
- Los logs humanos son para lectura.
- Los registros estructurados son para diagnóstico y contratos JSON.

## Relación con JsonContractCore

LoggingCore puede producir `diagnostics` y `errors`.

JsonContractCore valida que el contrato completo tenga la estructura correcta.

```text
LoggingCore      → produce registros
JsonContractCore → valida/escribe contratos
```
