# DateTimeCore

## Resumen

Fechas, horas, timestamps UTC/locales y conversión desde epoch seconds con formato estándar para todo el ecosistema.

## Estado actual

Base inicial funcional para consistencia JSON y logs.

DateTimeCore centraliza el formato de fechas y horas del ecosistema SharedCode.

Su objetivo es evitar que cada core genere timestamps con reglas distintas.

## Regla estándar

Para datos técnicos y JSON:

```text
UTC ISO-8601 compacto, sin microsegundos, con sufijo Z.
```

Ejemplo:

```text
2026-06-30T15:04:05Z
```

Para lectura humana se puede agregar una fecha local separada:

```text
2026-06-30T12:04:05-03:00
```

## Uso básico

```python
from date_time_core import utc_now_iso, datetime_to_utc_iso

print(utc_now_iso())
```

## Helpers principales

- `datetime_to_utc_iso()`
- `datetime_to_local_iso()`
- `utc_now_iso()`
- `local_now_iso()`
- `create_timestamp_pair()`
- `parse_iso_datetime()`
- `timestamp_seconds_to_utc_iso()`
- `format_iso_for_log()`

## Decisiones de diseño

```text
DESIGN: UTC es la fuente técnica estable.
DESIGN: Los timestamps JSON no usan microsegundos.
DESIGN: UTC se serializa como Z, no como +00:00.
DESIGN: La fecha local se guarda en un campo separado cuando aporta valor humano.
DESIGN: Los epoch seconds solo deben exponerse con nombre explícito *_epoch_seconds.
```
