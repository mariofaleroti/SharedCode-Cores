# JSON Standard v1.0.0

## Estructura raíz

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

## Regla general

Las claves raíz estándar deben existir siempre.

Los objetos vacíos se representan con `{}`.

Las listas vacías se representan con `[]`.

No usar `null` para bloques estructurales.


## Fechas y horas

Regla estándar para todo JSON técnico del ecosistema:

```text
UTC ISO-8601 compacto, sin microsegundos, con sufijo Z.
```

Ejemplo:

```json
"started_at_utc": "2026-06-30T15:04:05Z"
```

Cuando una fecha local aporte valor humano, debe ir en un campo separado y explícito:

```json
"started_at_local": "2026-06-30T12:04:05-03:00"
```

No mezclar `Z` y `+00:00` para UTC en salidas estándar. UTC se serializa como `Z`.

Los timestamps numéricos tipo epoch solo deben exponerse cuando sean necesarios y con nombre explícito:

```json
"modified_at_epoch_seconds": 1782824645.0
```

## Tipos generales

`meta.file_type` define el tipo general del JSON:

- `manifest`
- `config`
- `report`
- `result`
- `state`
- `profile`

## Subtipos recomendados

Según el tipo:

- `manifest` usa `manifest_type`
- `config` usa `config_type`
- `report` usa `report_type`
- `result` usa `result_type`
- `state` usa `state_type`

Ejemplos:

```json
"file_type": "config",
"config_type": "settings"
```

```json
"file_type": "manifest",
"manifest_type": "tool_manifest"
```

```json
"file_type": "report",
"report_type": "hardware"
```
