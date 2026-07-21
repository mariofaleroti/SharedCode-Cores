# CliCore

CliCore es un core compartido de **SharedCode** para estandarizar la entrada por línea de comandos de herramientas externas del ecosistema.

Su objetivo es pequeño y claro: ofrecer argumentos comunes, opciones normalizadas y códigos de salida consistentes.

CliCore no ejecuta la herramienta, no carga configuración, no crea contexto de ejecución, no escribe reportes y no conoce Toolkit, ShadowBackup, Smart Filter ni ninguna herramienta concreta.

## Rol dentro del ecosistema

```text
CliCore recibe argumentos comunes.
ToolRuntimeCore arma contexto y rutas.
ConfigCore carga configuración.
LoggingCore registra eventos.
La herramienta concreta ejecuta su lógica.
JsonContractCore estructura/valida salidas JSON.
```

## Argumentos comunes

CliCore define argumentos reutilizables para herramientas externas:

```text
--config
--output-dir
--logs-dir
--json-output
--quiet
--verbose / -v
--debug
--no-pause
--validate-config
--version
```

La herramienta puede agregar sus propios argumentos encima de esta base.

## Uso básico

```python
from cli_core import create_base_parser, parse_cli_options

parser = create_base_parser(
    tool_name="ShadowBackup",
    description="Automatic Git repository backup tool.",
    version="0.1.0",
)

parser.add_argument(
    "--scan-root",
    help="Tool-specific scan root.",
)

options = parse_cli_options(parser)

print(options.config_path)
print(options.output_dir)
print(options.log_level)
```

## Filosofía

CliCore debe mantenerse neutral.

```text
CliCore no ejecuta aplicaciones.
CliCore no interpreta configuración.
CliCore no valida reglas de negocio.
CliCore no depende de Toolkit.
CliCore solo estandariza entrada CLI común.
```

## Códigos de salida

```text
0 -> OK
1 -> Error general / validación fallida
2 -> Error de uso CLI / argumentos inválidos
```

Estos códigos están disponibles como constantes:

```python
from cli_core import EXIT_OK, EXIT_ERROR, EXIT_USAGE_ERROR
```

## Validaciones incluidas

CliCore rechaza combinaciones contradictorias como:

```text
--quiet + --verbose
--quiet + --debug
```

## Estructura

```text
CliCore/
├─ README.md
├─ examples/
│  └─ basic_cli_example.py
├─ tests/
│  └─ test_cli_core_behavior.py
└─ cli_core/
   ├─ __init__.py
   ├─ constants.py
   ├─ exit_codes.py
   ├─ models.py
   └─ parser.py
```

## Pruebas

Desde la carpeta `CliCore`:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

## Estado

```text
CliCore v1 - base inicial
```
