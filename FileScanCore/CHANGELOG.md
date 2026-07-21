# FileScanCore Changelog

## Cancelación cooperativa del pool acotado

- `iter_bounded_workers()` y `process_with_bounded_workers()` aceptan `cancel_requested`.
- Al solicitar cancelación, el productor deja de consumir candidatos y se cancelan tareas que aún no comenzaron.
- Las llamadas activas terminan naturalmente en segundo plano; el consumidor recupera el control sin esperar el vaciado completo.
- `WorkerPoolStats` agrega `cancelled_count` y `cancellation_requested`.
- Los eventos de progreso incluyen `cancelled` y pueden emitir `event=cancelled`.
- La API sigue siendo retrocompatible porque el callback es opcional.

## Desglose de carpetas omitidas

- `DirectoryWalkStats`, `DirectoryWalkResult` y `MarkerScanResult` separan omisiones por política, enlace/reparse point, nombre exacto, palabra clave y directorio ya visitado.
- Las herramientas consumidoras pueden explicar completamente `skipped_count` sin dejar una diferencia opaca.
- Se mantiene la compatibilidad con `skipped_count` y `policy_skipped_count`.

## Política declarativa de exclusión y poda real

- Nuevo `DirectoryExclusionPolicy` con reglas por nombre, patrón relativo y ruta absoluta.
- El walker descarta una carpeta antes de incorporarla al recorrido.
- Una coincidencia evita recorrer toda la rama y puede reportar grupo, regla, motivo y valor coincidente.
- Las reglas concretas siguen perteneciendo a la herramienta consumidora.
- `DirectoryWalkStats` informa cuántas carpetas fueron podadas por política.
- Se agregaron pruebas para nombres, patrones segmentados, rutas exactas y poda completa.

## Ajuste experimental de cola a 40

- Mantiene 4 trabajadores concurrentes.
- Eleva la cola predeterminada de 20 a 40 tareas pendientes.
- El límite total pasa a ser 44 tareas sin finalizar: 4 activas y hasta 40 en espera.
- No cambia la API pública ni el comportamiento de consumidores que indiquen una capacidad explícita.
- Smart Filter hereda automáticamente este valor porque consume `DEFAULT_QUEUE_CAPACITY`.

## Diagnóstico estructurado de errores

- `ScanError` ahora incluye la etapa (`stage`) donde ocurrió la falla.
- Nuevo `ScanError.to_dict()` para persistir ruta, tipo, excepción y motivo en JSON.
- `build_scan_error()` y `build_validation_error()` pasan a ser API pública.
- Cambio retrocompatible: los campos y constructores anteriores continúan funcionando.


## Progreso vivo del pipeline

- Los eventos de progreso ahora se emiten tanto al enviar como al completar tareas.
- Cada evento informa `event`, `active`, `queued`, `in_flight`, `submitted` y `completed`.
- Esto permite que las herramientas consumidoras muestren actividad real aunque el porcentaje global no cambie.
- Cambio retrocompatible: se conservan las claves anteriores del callback.

## Cola limitada y trabajadores concurrentes

- Nuevo `worker_pool.py` neutral y reutilizable.
- Configuración inicial: 4 trabajadores y cola de 20 tareas pendientes.
- El productor puede seguir descubriendo candidatos mientras los trabajadores procesan los anteriores.
- Producción pausada automáticamente cuando se alcanza el límite total.
- Errores aislados por tarea sin detener el procesamiento restante.
- Orden de entrada opcional mediante `preserve_input_order=True`.
- Métricas de tareas enviadas, completadas, correctas, fallidas y picos de cola.
- Nuevas pruebas unitarias de concurrencia, límites, orden y fallos.

## Límite arquitectónico

FileScanCore coordina el trabajo, pero no decide qué archivo es candidato ni cómo leer XLSX, PDF, DOCX, TXT u otros formatos. Esa lógica permanece en la herramienta consumidora.
