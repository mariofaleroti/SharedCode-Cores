# Integración estricta con JsonContractCore

RenderCore v0.4.1 exige `JsonContractCore`. No hay validador local alternativo, modo legacy ni bypass de contrato.

## Idea

```text
Herramienta externa
  ↓ genera JSON estándar
JsonContractCore
  ↓ valida contrato
RenderCore
  ↓ construye ReportDocument
HTML / TXT / CSV / XLSX
```

## Responsabilidades

```text
JsonContractCore  valida el contrato JSON estándar.
RenderCore        presenta el contrato validado.
Herramientas      generan datos correctos.
Toolkit           consume resultados o ejecuta herramientas.
```

RenderCore puede hacer una comprobación defensiva de forma después de recibir el resultado de `JsonContractCore`, pero no completa campos faltantes ni transforma contratos viejos.

## CLI

```powershell
python -m render_core render `
  --input examples/event_health_sample.json `
  --output-dir output/demo `
  --formats html,txt,csv,xlsx `
  --json
```

No existen estos parámetros:

```text
--validator auto
--validator local
--validator none
--strict
```

El contrato es estricto siempre.

## Python

```python
from render_core import render_many

results = render_many(
    input_path="event_health.json",
    formats=["html", "txt", "xlsx"],
    output_dir="output/reportes",
    contract_profile="tool_report",
)
```

## API esperada de JsonContractCore

RenderCore busca paquetes en estas rutas:

```text
json_contract_core
JsonContractCore.json_contract_core
SharedCode.JsonContractCore.json_contract_core
```

Y busca funciones compatibles en el paquete raíz o submódulos `api`, `contracts`, `validators` o `validation`:

```text
validate_tool_report_contract
validate_report_contract
validate_json_contract
validate_contract
validate
```

Forma recomendada:

```python
def validate_contract(data: dict, *, strict: bool = True, contract_profile: str = "tool_report") -> dict:
    return {
        "ok": True,
        "normalized_data": data,
        "warnings": [],
        "errors": [],
        "diagnostics": [],
    }
```

También puede devolver un objeto con atributos equivalentes:

```text
ok / valid
normalized_data / normalized / data / report_data
warnings
errors
diagnostics
```

Si `ok` o `valid` es falso, RenderCore corta y no renderiza.

## Error esperado si falta JsonContractCore

Si RenderCore se ejecuta sin `JsonContractCore`, debe fallar con un error claro:

```text
JsonContractCore is required by RenderCore v0.4.1 and no compatible validator was found.
```

Ese comportamiento es intencional.

## Diagnósticos

Cuando el render es exitoso, RenderCore agrega un diagnóstico indicando qué validador procesó el contrato:

```json
{
  "level": "info",
  "message": "Contract validator: json_contract_core.api.validate_contract"
}
```
