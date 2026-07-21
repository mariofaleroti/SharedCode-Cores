# RenderCore v0.10.0 - Document Highlight Pro

Motor compartido y neutral para renderizar contratos JSON del ecosistema **SharedCode**.

## Novedad 0.10.0

- Agrega el perfil profesional `document_highlight_pro`.
- Conserva `document_highlight` como base funcional estable.
- Reutiliza el lenguaje visual aprobado del perfil SmartDisk sin copiar su estructura de datos.
- Incorpora hero, métricas, sidebar sticky, términos, ubicaciones, secciones plegables y navegación con progreso.
- Mantiene resaltado tolerante a mayúsculas y tildes comunes.
- Mantiene JsonContractCore obligatorio y no interpreta formatos propietarios dentro de RenderCore.


RenderCore no recolecta datos, no diagnostica equipos y no corrige contratos. Su responsabilidad es recibir un JSON válido del contrato estándar, validarlo mediante `JsonContractCore` y generar salidas consumibles.

## Estado de esta versión

`v0.10.0` eleva el visor documental con un perfil profesional y mantiene `document_highlight` como base funcional compatible. La base congelada 0.8.1 continúa documentada.

Esta versión toma como base funcional `v0.8.0 - Export Polish` y agrega documentación, scripts oficiales y notas de congelamiento. No introduce cambios de contrato ni vuelve a habilitar compatibilidad legacy.

Base aprobada:

- `JsonContractCore` obligatorio.
- Contrato JSON estándar estricto.
- Sin modo legacy, local, none ni fallback permisivo.
- HTML / TXT / CSV / XLSX.
- Perfil completo de producción para `disk_smart`.
- HTML SmartDisk profesional con sidebar sticky real.
- TXT ejecutivo/técnico legible.
- CSV con tablas normalizadas y `report_summary.csv`.
- XLSX presentable con hojas, filtros, encabezados congelados y columnas ajustadas.

## Lugar dentro de SharedCode

```text
SharedCode/
└─ RenderCore/
   ├─ render_core/
   ├─ apps/
   │  └─ render_engine/
   ├─ examples/
   ├─ scripts/
   ├─ tests/
   ├─ docs/
   ├─ README.md
   ├─ CHANGELOG.md
   ├─ VERSION
   ├─ pyproject.toml
   └─ requirements.txt
```

## Flujo interno

```text
JSON del ecosistema
  ↓
JsonContractCore obligatorio
  ↓
ReportDocument neutral
  ↓
normalización de presentación por perfil
  ↓
HTML / TXT / CSV / XLSX
```

## Regla de contrato

Contrato base obligatorio:

```json
{
  "meta": {},
  "summary": {},
  "report_brief": {},
  "data": {},
  "diagnostics": [],
  "errors": []
}
```

Valores mínimos defensivos para RenderCore dentro de `meta`:

```json
{
  "schema_version": "1.0.0",
  "tool_name": "Nombre de herramienta",
  "report_type": "disk_smart"
}
```

Para documentos de configuración también puede usarse `config_type` o `file_type`, siempre que `JsonContractCore` lo valide.

No existe modo legacy, modo local, modo none ni normalización permisiva. Si el contrato no cumple, RenderCore no renderiza.

## Integración con JsonContractCore

`JsonContractCore` es obligatorio. RenderCore busca un validador compatible en estas rutas:

```text
json_contract_core
JsonContractCore.json_contract_core
SharedCode.JsonContractCore.json_contract_core
```

Y en submódulos comunes:

```text
api
contracts
validators
validation
```

Funciones compatibles:

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

## Uso desde CLI

Desde `SharedCode/RenderCore`:

```powershell
python -m render_core render --input examples/event_health_sample.json --output-dir output/demo --formats html,txt,csv,xlsx
```

Salida JSON para integración:

```powershell
python -m render_core render --input examples/event_health_sample.json --output-dir output/demo --formats html,txt,xlsx --json
```

Prueba real con un JSON propio:

```powershell
python -m render_core render `
  --input "C:\ruta\al\smart_disk.json" `
  --output-dir ".\output\smartdisk_test" `
  --formats html,txt,csv,xlsx `
  --json
```

También puede usarse el helper:

```powershell
.\scripts\render_json.ps1 -InputJson "C:\ruta\al\smart_disk.json" -OutputDir ".\output\smartdisk_test" -Formats "html,txt,csv,xlsx" -Json
```

## Salidas esperadas para `disk_smart`

```text
smart_disk.html
smart_disk.txt
smart_disk.xlsx
report_summary.csv
data_disks.csv
data_ata_attributes.csv
data_nvme_health_metrics.csv
data_alternate_smart_devices.csv
```

## TXT

El TXT no intenta reemplazar al HTML ni al XLSX. Es una lectura rápida para consola, tickets o revisión técnica rápida:

- Contexto del reporte.
- Resumen ejecutivo.
- Discos y estado principal.
- Referencia a tablas técnicas exportadas.
- Diagnósticos y errores si existen.

## CSV

CSV genera un archivo por tabla normalizada y un `report_summary.csv`. Los archivos se guardan con UTF-8 BOM para abrir mejor en Excel.

## XLSX

XLSX genera un libro legible para revisión técnica:

- `Resumen`
- `Vista discos`, para `disk_smart`
- `Diagnosticos`, si existen
- `Errores`, si existen
- una hoja por tabla normalizada

Incluye filtros, encabezados congelados, anchos de columna acotados y estilos básicos por estado.

## Build del wrapper RenderEngine

Desde `SharedCode/RenderCore`:

```powershell
.\scripts\build_render_engine.ps1
```

Resultado esperado:

```text
release\RenderEngine\RenderEngine.exe
release\RenderEngine\tool_manifest.json
```

La carpeta `release/` no debería subirse a GitHub. Se genera localmente para distribuir.

## Pruebas oficiales

Smoke test aislado:

```powershell
.\scripts\quick_test.ps1
```

Prueba de un JSON real:

```powershell
.\scripts\render_json.ps1 -InputJson "C:\ruta\al\archivo.json" -OutputDir ".\output\manual_test" -Formats "html,txt,csv,xlsx" -Json
```

Limpieza de outputs locales:

```powershell
.\scripts\clean_outputs.ps1
```

El smoke test instala un `JsonContractCore` falso temporal solo para comprobar la integración estricta. En producción debe usarse el `JsonContractCore` real de SharedCode.

## Base congelada

Ver `docs/STABLE_BASELINE.md` antes de hacer cambios grandes sobre esta base.
