# FileScanCore

## Resumen

`FileScanCore` es una base común para recorrer carpetas de forma segura, detectar marcadores y coordinar procesamiento paralelo limitado de candidatos.

Su objetivo es evitar que cada herramienta externa vuelva a implementar la misma lógica de escaneo, exclusiones, profundidad, manejo de errores y prevención de recorridos peligrosos.

```text
SharedCode alimenta herramientas externas en desarrollo.
Cada herramienta mantiene su lógica propia.
Cada herramienta genera un release autosuficiente.
Toolkit no depende de SharedCode.
Toolkit solo consume herramientas estables por manifest.
```

---

## Responsabilidad principal

`FileScanCore` es responsable de:

```text
- recorrer carpetas de forma segura
- aplicar reglas de directorios salteados
- podar ramas completas mediante políticas declarativas de exclusión
- controlar max_depth
- evitar symlinks/reparse points por defecto
- detectar marcadores dentro de carpetas
- coordinar una cola limitada de candidatos
- procesar candidatos con un grupo fijo de trabajadores
- aislar fallas individuales de cada trabajador
- recolectar errores no fatales
- desglosar por qué cada carpeta fue omitida
- conservar ruta, etapa, tipo de excepción y motivo de cada error
- devolver resultados estructurados
```

---

## Lo que no debe hacer

`FileScanCore` debe mantenerse neutral.

No debe:

```text
- conocer ShadowBackup, Smart Filter, Toolkit u otra herramienta concreta
- ejecutar comandos externos
- interpretar el significado final de un marcador
- validar repositorios Git
- decidir qué archivo es candidato
- leer por sí mismo contenido de PDF, Excel, Word u otros documentos
- generar reportes finales de una herramienta
- renderizar HTML
- decidir reglas de negocio
```

Regla base:

```text
FileScanCore escanea y coordina trabajadores.
La herramienta consumidora selecciona candidatos e interpreta resultados.
```

---

## Marcador detectado vs directorio recorrido

Detectar un marcador no es lo mismo que recorrerlo internamente.

Ejemplo:

```text
Project\
├─ .git\
├─ main.py
└─ README.md
```

`FileScanCore` puede detectar que `Project` contiene `.git`, pero no debe recorrer por dentro:

```text
Project\.git\objects\
Project\.git\refs\
Project\.git\logs\
```

Motivo:

```text
.git puede servir como marcador.
.git no es un objetivo de escaneo recursivo.
```

En el código esto queda representado por la constante:

```python
DEFAULT_SKIPPED_DIRECTORY_NAMES
```

Esa constante expresa directorios que se saltean durante el recorrido, no marcadores que se ignoran.

---

## Estructura

```text
FileScanCore\
├─ CHANGELOG.md
├─ README.md
├─ examples\
│  ├─ find_git_repositories_example.py
│  └─ bounded_workers_example.py
├─ tests\
│  ├─ test_exclusion_policy.py
│  ├─ test_file_scan_core_behavior.py
│  └─ test_worker_pool.py
└─ file_scan_core\
   ├─ __init__.py
   ├─ models.py
   ├─ errors.py
   ├─ exclusion_policy.py
   ├─ filters.py
   ├─ walker.py
   ├─ markers.py
   └─ worker_pool.py
```

---

## Módulos

### `models.py`

Define modelos estructurados y neutrales:

```text
ScanError
DirectoryWalkStats
DirectoryWalkResult
MarkerMatch
MarkerScanResult
WorkerPoolStats
WorkerTaskResult
WorkerPoolResult
```

Estos modelos describen resultados. No ejecutan acciones ni contienen lógica de una herramienta concreta.

---

### `errors.py`

Convierte errores del filesystem en errores estructurados.

Tipos esperados:

```text
permission_denied
path_not_found
not_a_directory
os_error
unknown_error
invalid_marker_name
invalid_max_depth
skipped_link_or_reparse_point
```

La regla es recolectar errores no fatales y devolverlos en el resultado.

---

### `filters.py`

Centraliza reglas de exclusión de recorrido.

La constante principal es:

```python
DEFAULT_SKIPPED_DIRECTORY_NAMES
```

Incluye carpetas que normalmente no conviene recorrer recursivamente, por ejemplo:

```text
.git
.venv
__pycache__
node_modules
```

Nota importante: `release`, `build` y `dist` no están en los defaults porque pueden tener significado para herramientas del ecosistema, por ejemplo al buscar `tool_manifest.json`.

---

### `walker.py`

Contiene el motor de recorrido seguro.

Funciones públicas:

```python
iter_safe_directories(...)
walk_directories(...)
```

`iter_safe_directories()` es útil para procesamiento por streaming.

`walk_directories()` es útil cuando se necesita un resultado completo ya recolectado.

Por defecto no sigue symlinks ni reparse points. Si `follow_symlinks=True` se activa explícitamente, el walker mantiene un registro interno de directorios reales ya visitados para evitar loops recursivos.

---

### `worker_pool.py`

Coordina el patrón productor-consumidor usado por búsquedas amplias:

```text
1 productor/escáner
+ grupo fijo de trabajadores
+ cola de espera limitada
```

Funciones públicas:

```python
iter_bounded_workers(...)
process_with_bounded_workers(...)
```

Valores iniciales:

```text
max_workers = 4
queue_capacity = 40
```

El iterable de entrada puede continuar descubriendo candidatos mientras los trabajadores procesan los anteriores. Cuando existen 4 tareas activas y 40 esperando, el productor pausa hasta que quede espacio.

El core no sabe si un candidato es XLSX, PDF, DOCX o TXT. La herramienta consumidora entrega la función trabajadora y agrega los resultados en su propio hilo para evitar condiciones de carrera.

El callback de progreso recibe eventos al enviar y completar tareas:

```python
{
    "event": "submitted",  # o "completed"
    "submitted": 24,
    "completed": 7,
    "active": 4,
    "queued": 13,
    "in_flight": 17,
}
```

Esto permite mostrar contadores reales sin depender de un porcentaje estimado.

La cancelación es cooperativa y opcional:

```python
resultados = list(
    iter_bounded_workers(
        items=candidate_paths,
        worker=read_candidate,
        max_workers=4,
        queue_capacity=40,
        cancel_requested=cancel_event.is_set,
        stats=stats,
    )
)
```

Cuando el callback devuelve `True`, FileScanCore deja de consumir el iterable,
cancela las tareas aún no iniciadas y devuelve el control sin esperar el vaciado
completo. Las tareas ya activas terminan naturalmente y sus resultados se ignoran.

`WorkerPoolStats` expone:

```text
cancelled_count
cancellation_requested
```

---

### `markers.py`

Contiene helpers para detectar marcadores.

Función principal:

```python
find_marker_directories(...)
```

`root_paths` puede recibir una ruta individual o una colección de rutas:

```python
find_marker_directories(Path(r"C:\Projects"), ".git")
find_marker_directories([Path(r"C:\Projects"), Path(r"D:\Tools")], ".git")
```

Ejemplos de marcadores posibles:

```text
.git
tool_manifest.json
pyproject.toml
package.json
```

El core no interpreta esos marcadores. Solo informa que existen.

---

## Ejemplo básico

```python
from pathlib import Path

from file_scan_core import find_marker_directories

result = find_marker_directories(
    root_paths=Path(r"C:\Projects"),
    marker_name=".git",
    max_depth=5,
)

for match in result.matches:
    print(match.directory_path)

for error in result.errors:
    print(error.error_type, error.path, error.message)
```

---

## Ejemplo de procesamiento paralelo limitado

```python
from file_scan_core import process_with_bounded_workers

result = process_with_bounded_workers(
    items=candidate_paths,
    worker=read_candidate,
    max_workers=4,
    queue_capacity=40,
    preserve_input_order=True,
)

for task in result.succeeded_results:
    consume(task.value)
```

Regla de seguridad para consumidores:

```text
El trabajador devuelve un resultado.
El hilo productor actualiza contadores, listas, progreso y GUI.
```

---

## Convención de comentarios

Los comentarios técnicos deben usar estas marcas cuando aporten valor real:

```text
DESIGN   -> decisión de arquitectura
NOTE     -> aclaración importante
WARNING  -> riesgo técnico
TODO     -> tarea pendiente concreta
FUTURE   -> mejora posible para más adelante
```

No se deben agregar comentarios obvios que repitan el código.

---

## Estado

Base estable de recorrido seguro y procesamiento concurrente limitado.

El siguiente paso natural es conectar Smart Filter al nuevo flujo productor-consumidor, manteniendo sus readers y reglas de negocio fuera de `FileScanCore`.

---

## Pruebas

FileScanCore incluye pruebas automáticas con `unittest`, sin dependencias externas.

Desde la carpeta `FileScanCore`, ejecutar:

```powershell
python -m unittest discover -s tests -v
```

Resultado esperado:

```text
OK
```

Las pruebas validan escenarios base del core:

```text
- recorrido seguro de carpetas
- exclusión de directorios internos como .git y node_modules
- detección de marcadores sin recorrer internamente el marcador
- detección de tool_manifest.json dentro de release
- control de max_depth
- reglas personalizadas de exclusión por nombre exacto y keyword
- errores no fatales estructurados
- bloqueo de symlinks por defecto
- protección contra loops si follow_symlinks=True
- aceptación de ruta individual o múltiples rutas
- exportación pública de símbolos principales del paquete
- callback de progreso
- procesamiento concurrente con límite de trabajadores
- cola pendiente limitada
- aislamiento de errores por tarea
- conservación opcional del orden de entrada
```

---

## Política declarativa de exclusión

`DirectoryExclusionPolicy` permite que cada herramienta entregue reglas neutrales:

```text
- nombres exactos de carpeta
- patrones relativos desde la raíz
- rutas absolutas elegidas por el usuario
```

El walker evalúa las reglas antes de agregar una carpeta a la pila. Si coincide, la rama completa queda podada y el consumidor puede registrar grupo, regla y motivo mediante callback.


## Desglose de omisiones

Los resultados de recorrido conservan `skipped_count` y además separan:

```text
policy_skipped_count
link_or_reparse_skipped_count
name_skipped_count
keyword_skipped_count
revisited_skipped_count
```

La política concreta sigue perteneciendo a la herramienta consumidora. FileScanCore solo informa el motivo técnico de la poda.
