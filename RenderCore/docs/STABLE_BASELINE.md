# RenderCore Stable Baseline v0.8.1

Esta versión queda marcada como la primera base estable aprobada de RenderCore dentro de SharedCode.

## Qué queda aprobado

- RenderCore vive como core compartido en `SharedCode/RenderCore`.
- `JsonContractCore` es obligatorio y sigue siendo la autoridad del contrato.
- RenderCore no corrige contratos rotos.
- RenderCore no acepta modo legacy/permisivo.
- RenderCore genera `html`, `txt`, `csv` y `xlsx`.
- `disk_smart` queda como primer perfil completo de producción.

## Criterio de estabilidad

La base se considera estable porque cubre el flujo completo:

```text
JSON estándar válido
  ↓
validación estricta
  ↓
normalización de presentación
  ↓
render multi-formato
```

## Reglas para cambios futuros

No modificar la base estable por ajustes de una herramienta específica si el cambio puede romper otros perfiles.

Cambios permitidos:

- Nuevo perfil visual para un `report_type` o `config_type`.
- Nuevo normalizador específico por perfil.
- Mejora de exportación que mantenga compatibilidad.
- Corrección de bug comprobado.
- Documentación o pruebas.

Cambios que requieren versión mayor o revisión especial:

- Cambiar el contrato esperado.
- Hacer opcional `JsonContractCore`.
- Agregar modo legacy/permisivo.
- Completar automáticamente claves obligatorias faltantes.
- Cambiar nombres de salidas ya estabilizadas.

## Perfiles aprobados

| Perfil | HTML | TXT | CSV | XLSX | Estado |
| --- | --- | --- | --- | --- | --- |
| `disk_smart` | Sí | Sí | Sí | Sí | Aprobado |

## Próximos perfiles sugeridos

| Perfil | Motivo |
| --- | --- |
| `event_health` | Segundo reporte real del ecosistema Toolkit. |
| `storage_analyzer` | Alto valor visual y tabular. |
| `category_database` | Ya tiene HTML pro parcial y conviene cerrar TXT/CSV/XLSX. |

## Nota de arquitectura

RenderCore presenta. JsonContractCore valida. Las herramientas generan. Toolkit consume.
