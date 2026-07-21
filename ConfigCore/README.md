# ConfigCore

ConfigCore es un core compartido del ecosistema **SharedCode** para cargar, combinar y validar configuraciones de herramientas externas.

Su objetivo no es interpretar reglas de negocio de una herramienta concreta. Su responsabilidad es resolver problemas comunes de configuración:

- cargar archivos JSON de configuración
- trabajar con contratos JSON estándar
- extraer la configuración desde `data`
- aplicar valores por defecto
- validar rutas requeridas
- validar tipos básicos
- validar valores permitidos
- devolver errores y diagnósticos estructurados
- escribir configuraciones estándar cuando sea necesario

## Rol dentro del ecosistema

```text
JsonContractCore  -> valida el envase JSON estándar
ConfigCore        -> valida y normaliza la configuración dentro de data
Herramienta       -> interpreta la configuración según su negocio
```

Ejemplo:

```text
config.json
├─ meta
├─ summary
├─ report_brief
├─ data          <- ConfigCore trabaja principalmente acá
├─ diagnostics
└─ errors
```

## Qué no hace ConfigCore

```text
- no sabe qué es Toolkit
- no sabe qué es ShadowBackup
- no sabe qué es Smart Filter
- no ejecuta comandos externos
- no decide reglas de negocio finales
- no reemplaza JsonContractCore
```

## Estructura

```text
ConfigCore/
├─ README.md
├─ examples/
│  └─ basic_config_example.py
├─ tests/
│  └─ test_config_core_behavior.py
└─ config_core/
   ├─ __init__.py
   ├─ access.py
   ├─ constants.py
   ├─ loader.py
   ├─ merger.py
   ├─ models.py
   ├─ validator.py
   └─ writer.py
```

## Uso básico

```python
from config_core import load_config

result = load_config(
    "config/shadow_backup.json",
    defaults={
        "scan": {
            "max_depth": 5,
            "scan_interval_minutes": 20,
        },
        "git": {
            "auto_commit": False,
            "commit_message": "Automatic backup",
        },
    },
    required_paths=[
        "scan.root_paths",
    ],
    type_rules={
        "scan.root_paths": list,
        "scan.max_depth": int,
        "git.auto_commit": bool,
    },
)

if not result.is_valid:
    for error in result.errors:
        print(error.code, error.message)
else:
    config = result.config
```

## Integración con JsonContractCore

Por defecto, `load_config()` espera un contrato JSON estándar y trabaja sobre la clave `data`.

```json
{
  "meta": {
    "schema_version": "1.0.0",
    "file_type": "config",
    "config_type": "shadow_backup",
    "tool_name": "ShadowBackup",
    "module_name": "Config"
  },
  "summary": {
    "status": "active",
    "errors_count": 0,
    "diagnostics_count": 0
  },
  "report_brief": {},
  "data": {
    "scan": {
      "root_paths": ["C:/Projects"],
      "max_depth": 5
    }
  },
  "diagnostics": [],
  "errors": []
}
```

ConfigCore puede llamar a `JsonContractCore` si el paquete `json_contract_core` está disponible en el `PYTHONPATH`.

```python
result = load_config(
    "config.json",
    validate_standard_contract=True,
)
```

Si querés exigir que JsonContractCore esté disponible:

```python
result = load_config(
    "config.json",
    require_contract_validator=True,
)
```

## Defaults

ConfigCore aplica defaults con merge profundo:

```python
defaults = {
    "scan": {
        "max_depth": 5,
        "scan_interval_minutes": 20,
    }
}
```

Si el archivo define solo:

```json
{
  "scan": {
    "max_depth": 3
  }
}
```

el resultado final conserva `scan_interval_minutes` y reemplaza `max_depth`.

## Listas

Las listas no se mezclan automáticamente.

```text
DESIGN: una lista representa una decisión de la herramienta.
ConfigCore no intenta adivinar si debe concatenar, reemplazar o deduplicar.
```

Si una herramienta define una lista en el archivo de configuración, esa lista reemplaza la lista por defecto.

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
