# FileSystemInfoCore

FileSystemInfoCore obtiene información puntual de archivos y carpetas.

No recorre árboles completos. Para recorridos profundos existe FileScanCore. Este core se enfoca en metadatos de rutas individuales y resúmenes livianos de directorios.

## Rol dentro de SharedCode

```text
FileScanCore recorre.
FileSystemInfoCore describe rutas.
```

## Validaciones

```bash
python -m compileall .
python -m unittest discover -s tests -v
```

## Formato de fechas

FileSystemInfoCore serializa fechas técnicas como UTC ISO-8601 con sufijo `Z`:

```json
"modified_at_utc": "2026-06-30T15:04:05Z"
```

Cuando necesita conservar el valor numérico del sistema de archivos, usa campos explícitos `*_epoch_seconds`:

```json
"modified_at_epoch_seconds": 1782824645.0
```
