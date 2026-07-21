# Pruebas de RenderCore

## Preparación

Desde la raíz de `SharedCode`:

```powershell
python -m pip install -e ".[render,dev]"
python tools/run_public_validation.py
```

## Smoke test aislado

```powershell
.\scripts\quick_test.ps1
```

Este test usa un `JsonContractCore` falso temporal para verificar que RenderCore llama a un validador obligatorio. No reemplaza las pruebas con el `JsonContractCore` real.

## Prueba real de SmartDisk

```powershell
.\scripts\render_json.ps1 `
  -InputJson "C:\ruta\al\smart_disk.json" `
  -OutputDir ".\output\smartdisk_real_test" `
  -Formats "html,txt,csv,xlsx" `
  -Json
```

Salidas esperadas para `disk_smart`:

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

## Ver salidas

```powershell
Invoke-Item ".\output\smartdisk_real_test\smart_disk.html"
Invoke-Item ".\output\smartdisk_real_test\smart_disk.txt"
Invoke-Item ".\output\smartdisk_real_test\smart_disk.xlsx"
```

## Limpieza

```powershell
.\scripts\clean_outputs.ps1
```

## Resultado correcto

Una prueba correcta debe cumplir:

- El CLI devuelve `ok: true` en JSON si se usa `-Json`.
- El diagnóstico menciona un validador de contrato compatible.
- No aparecen diccionarios crudos dentro de CSV/XLSX para `disk_smart`.
- El HTML usa el perfil `disk_smart.html.j2`.
- El TXT se lee como informe técnico, no como volcado JSON.

## Resultado incorrecto esperado

Si `JsonContractCore` no existe o no se encuentra, RenderCore debe fallar. Eso es correcto.

No se debe resolver agregando fallback local ni modo permisivo. Se debe corregir la ruta/importación de `JsonContractCore`.
