# ProcessRunnerCore

**ProcessRunnerCore** es un core compartido de SharedCode para ejecutar comandos externos de forma controlada y devolver resultados estructurados.

Su objetivo es servir como base común para herramientas que necesiten llamar procesos externos, por ejemplo `git`, `smartctl`, utilidades del sistema o ejecutables auxiliares.

## Objetivo

ProcessRunnerCore permite:

- ejecutar comandos externos sin usar `shell=True` por defecto;
- capturar `stdout`, `stderr` y `exit_code`;
- aplicar timeout;
- medir duración;
- registrar `started_at` y `ended_at` en UTC estándar con sufijo `Z`;
- devolver un resultado estructurado y serializable a JSON;
- convertir fallos en entradas compatibles con `diagnostics` y `errors`;
- evitar que cada herramienta repita lógica de ejecución de procesos.

## Reglas de diseño

```text
ProcessRunnerCore ejecuta procesos externos.
ProcessRunnerCore no interpreta el significado de negocio del comando.
ProcessRunnerCore no sabe nada de ShadowBackup, Smart Filter o Toolkit.
ProcessRunnerCore no escribe contratos JSON por sí mismo.
ProcessRunnerCore devuelve resultados estructurados para que otra capa decida qué hacer.
ProcessRunnerCore usa DateTimeCore para serializar fechas UTC de forma consistente.
```

## Estructura

```text
ProcessRunnerCore/
├─ README.md
├─ examples/
│  └─ basic_process_runner_example.py
├─ tests/
│  └─ test_process_runner_core_behavior.py
└─ process_runner_core/
   ├─ __init__.py
   ├─ constants.py
   ├─ models.py
   └─ runner.py
```

## Uso básico

```python
from process_runner_core import run_process

result = run_process(
    ["python", "--version"],
    timeout_seconds=10,
)

print(result.exit_code)
print(result.stdout)
print(result.stderr)
```

## Uso recomendado con argumentos explícitos

```python
from process_runner_core import run_process

result = run_process(
    ["git", "status", "--porcelain"],
    cwd="C:/Projects/MyRepo",
    timeout_seconds=30,
)

if result.succeeded:
    print("Command completed successfully")
else:
    print(result.to_error())
```

## Seguridad

Por defecto, ProcessRunnerCore usa:

```python
shell=False
```

Esto evita que el sistema interprete el comando como una línea de shell completa.

### Recomendado

```python
run_process(["git", "status", "--porcelain"])
```

### Evitar salvo necesidad real

```python
run_process("git status --porcelain", shell=True)
```

`DESIGN`: `shell=True` queda disponible, pero debe ser una decisión explícita del consumidor.

## Resultado estructurado

`run_process()` devuelve un `ProcessRunResult` con campos como:

```text
command
status
exit_code
stdout
stderr
duration_ms
started_at
ended_at
timed_out
timeout_seconds
exception_type
exception_message
```

También puede convertirse a diccionario:

```python
result.to_dict()
```

## Integración con JsonContractCore

ProcessRunnerCore no depende de JsonContractCore, pero sus resultados pueden alimentar `diagnostics` y `errors`:

```python
diagnostic = result.to_diagnostic()
error = result.to_error()
```

`to_error()` devuelve `None` cuando el proceso fue exitoso.

## Validaciones

Comandos recomendados:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

Estas validaciones comprueban que el código Python sea sintácticamente válido y que el core respete los comportamientos esperados.

## Estado

```text
ProcessRunnerCore v1 - base inicial
```
