# AppCore

**AppCore** es el core compartido encargado de estandarizar el arranque y ciclo de vida de herramientas externas del ecosistema.

## Rol dentro de SharedCode

```text
CliCore             -> recibe argumentos
ToolRuntimeCore     -> prepara contexto/rutas/runtime
ConfigCore          -> carga configuración
LoggingCore         -> registra eventos
AppCore             -> ordena el ciclo de vida común
Herramienta concreta -> ejecuta su lógica propia
```


## Reglas diseño

```text
AppCore no escanea archivos.
AppCore no ejecuta comandos externos.
AppCore no carga configuración por sí mismo.
AppCore no parsea argumentos por sí mismo.
AppCore no sabe nada de Toolkit, ShadowBackup o Smart Filter.
```

AppCore solo coordina objetos ya creados o creados mediante fábricas inyectadas.

## Estructura

```text
AppCore/
├─ README.md
├─ examples/
│  └─ basic_app_bootstrap_example.py
├─ tests/
│  └─ test_app_core_behavior.py
└─ app_core/
   ├─ __init__.py
   ├─ app.py
   ├─ constants.py
   ├─ context.py
   ├─ lifecycle.py
   └─ models.py
```

## Uso básico

```python
from app_core import run_tool_app


def run_tool(context):
    context.logger.info("Tool logic started")
    return 0

exit_code = run_tool_app(
    tool_name="ExampleTool",
    tool_version="0.1.0",
    run_handler=run_tool,
    logger=my_logger,
)

raise SystemExit(exit_code)
```

## Uso con resultado estructurado

```python
result = run_tool_app(
    tool_name="ExampleTool",
    tool_version="0.1.0",
    run_handler=run_tool,
    return_result=True,
)

print(result.status)
print(result.exit_code)
print(result.duration_ms)
```

## Uso con fábricas

```python
from app_core import run_tool_app_with_factories

exit_code = run_tool_app_with_factories(
    tool_name="ExampleTool",
    tool_version="0.1.0",
    cli_options_factory=create_cli_options,
    runtime_factory=create_runtime,
    logger_factory=create_logger,
    config_factory=load_config,
    run_handler=run_tool,
)
```

## Exit codes

```text
0   -> ejecución correcta
1   -> error general durante la ejecución
2   -> error durante el arranque/fábricas
130 -> ejecución interrumpida por el usuario
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

## Filosofía

AppCore funciona como un punto de orden: recibe piezas preparadas por otros cores, ejecuta la función principal de la herramienta y devuelve un resultado consistente.

Cada herramienta mantiene su lógica propia. AppCore solo estandariza el ciclo común.
