# Integración de RenderCore en SharedCode

## Ubicación

Copiar la carpeta completa `RenderCore` dentro de la raíz del proyecto compartido:

```text
SharedCode/
├─ AppCore/
├─ CliCore/
├─ ConfigCore/
├─ FileScanCore/
├─ FileSystemInfoCore/
├─ GuiCore/
├─ JsonContractCore/
├─ LoggingCore/
├─ ProcessRunnerCore/
├─ ReleaseCore/
├─ ToolRuntimeCore/
└─ RenderCore/
```

## Regla de diseño

RenderCore debe mantenerse neutral y estricto:

```text
Herramienta genera JSON estándar
  ↓
JsonContractCore valida
  ↓
RenderCore renderiza
  ↓
Toolkit u otra app consume resultado
```

Toolkit no debe ser dependencia de RenderCore.

## Relación con JsonContractCore

`JsonContractCore` es dependencia obligatoria de RenderCore. No hay fallback local ni modo compatible.

La dirección correcta es:

```text
RenderCore ──importa/usa──> JsonContractCore
JsonContractCore ──X──> RenderCore
```

`JsonContractCore` debe seguir siendo más bajo nivel. No debe conocer HTML, TXT, CSV, XLSX ni templates.

## Uso desde otra herramienta Python

Ejemplo desde Event Health, Smart Disk o Smart Filter:

```python
from render_core import render_many

render_many(
    input_path="output/event_health.json",
    formats=["html", "txt", "xlsx"],
    output_dir="output/reportes/EventHealth",
)
```

La herramienta puede validar con `JsonContractCore` antes de guardar el JSON. RenderCore vuelve a validar antes de renderizar como segundo candado.

## Uso como ejecutable futuro

El wrapper `apps/render_engine/render_engine.py` existe para compilar un `RenderEngine.exe`.

Ese exe debe ser fino: solo llama a `render_core.cli`. La lógica vive en `render_core`.

## GitHub

Subir:

```text
RenderCore/render_core/
RenderCore/apps/
RenderCore/examples/
RenderCore/scripts/
RenderCore/tests/
RenderCore/docs/
RenderCore/README.md
RenderCore/CHANGELOG.md
```

No subir:

```text
RenderCore/output/
RenderCore/release/
RenderCore/build/
RenderCore/dist/
RenderCore/.venv/
RenderCore/__pycache__/
RenderCore/*.egg-info/
```

## Documentos relacionados

- `docs/STABLE_BASELINE.md` define la base estable aprobada.
- `docs/TESTING.md` contiene las pruebas oficiales.
- `docs/PROFILE_ROADMAP.md` lista los próximos perfiles sugeridos.

## Empaquetado público

RenderCore forma parte de la distribución raíz `sharedcode-cores`. Sus dependencias se instalan con el extra `render`.
