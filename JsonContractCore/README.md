# JsonContractCore

`JsonContractCore` es el core compartido encargado de crear, leer, escribir y validar contratos JSON estándar del ecosistema.

Su objetivo es que las herramientas externas produzcan salidas JSON consistentes, sin que cada proyecto vuelva a inventar su propia estructura base.

## Regla principal

```text
JsonContractCore define y valida el sobre JSON estándar.
Cada herramienta mantiene su lógica propia dentro de data, summary, diagnostics y errors.
Toolkit no depende de JsonContractCore.
Toolkit consume releases estables por manifest.
```

## Estructura esperada del contrato

Todo contrato JSON estándar debe tener estas claves raíz:

```text
meta
summary
report_brief
data
diagnostics
errors
```

Tipos esperados:

```text
meta         -> object
summary      -> object
report_brief -> object
data         -> object
diagnostics  -> list
errors       -> list
```

## Qué hace este core

```text
- crea contratos JSON estándar
- valida contratos JSON en memoria
- carga archivos JSON en UTF-8
- escribe archivos JSON en UTF-8
- devuelve errores y advertencias estructuradas
- permite validar un archivo JSON desde consola
```

## Qué no hace este core

```text
- no interpreta lógica de negocio
- no renderiza HTML
- no ejecuta herramientas externas
- no depende de Toolkit
- no decide si un resultado es bueno o malo para una herramienta concreta
```

## Estructura del proyecto

```text
JsonContractCore/
├─ README.md
├─ examples/
│  └─ basic_contract_validation_example.py
├─ tests/
│  └─ test_json_contract_core_behavior.py
└─ json_contract_core/
   ├─ __init__.py
   ├─ constants.py
   ├─ models.py
   ├─ validator.py
   ├─ builder.py
   ├─ writer.py
   ├─ loader.py
   ├─ cli.py
   └─ __main__.py
```

## Uso básico

```python
from json_contract_core import create_result_contract, validate_contract

contract = create_result_contract(
    result_type="example_result",
    tool_name="ExampleTool",
    module_name="ExampleModule",
    summary={
        "status": "ok",
        "errors_count": 0,
        "diagnostics_count": 0,
    },
    data={
        "items": [],
    },
)

result = validate_contract(contract)

if result.is_valid:
    print("Contrato válido")
else:
    print(result.errors)
```


## Uso desde consola

La CLI valida un archivo JSON concreto contra el contrato estándar. Esto permite que una herramienta PowerShell genere su JSON y luego lo valide antes de entregarlo como salida estable.

```bash
python -m json_contract_core output/tool_result.json
```

Modo silencioso, útil para scripts:

```bash
python -m json_contract_core output/tool_result.json --quiet
```

Guardar el resultado de validación como JSON:

```bash
python -m json_contract_core output/tool_result.json --json-output output/validation_result.json
```

Exit codes:

```text
0 -> contrato válido, o válido con advertencias si no se usa --fail-on-warnings
1 -> contrato inválido, o advertencias tratadas como error con --fail-on-warnings
2 -> error de ejecución: ruta inexistente, entrada no es archivo, JSON inválido o error de lectura
```

Opciones relevantes:

```text
--strict-schema-version  convierte diferencia de schema_version en error
--allow-extra-root-keys  permite claves extra en la raíz sin advertencia
--fail-on-warnings       devuelve exit code 1 si hay advertencias
--quiet                  no imprime reporte humano
```

## Validaciones

Comandos recomendados desde la carpeta `JsonContractCore`:

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

Estas validaciones comprueban que el código Python sea sintácticamente válido y que el core respete los comportamientos esperados.

## Decisiones de diseño

```text
DESIGN: El validador revisa el contrato raíz compartido, no el contenido específico de cada herramienta.
NOTE: report_brief puede estar vacío si no aplica.
WARNING: Las claves extra en la raíz generan advertencia por defecto; se recomienda moverlas dentro de data.
DESIGN: La CLI valida un archivo JSON específico; no hace análisis masivo recursivo para no volver al enfoque del analyzer histórico.
NOTE: El loader acepta UTF-8 con BOM para mejorar compatibilidad con JSON generado desde PowerShell.
```
