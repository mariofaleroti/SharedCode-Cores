# SharedCode

Base reutilizable de infraestructura Python para crear herramientas de escritorio y CLI sin repetir código común.

[Read in English](README.md)

## Qué incluye

SharedCode se distribuye como un único paquete, `sharedcode-cores`, pero mantiene imports pequeños y claros:

```python
from file_scan_core import walk_files
from platform_core import open_path
from render_core import render_report
```

Incluye núcleos para ciclo de vida de aplicaciones, CLI, configuración JSON, fechas, escaneo de archivos, metadata del sistema de archivos, GUI CustomTkinter, contrato JSON, logging, portabilidad Windows/Linux, procesos externos, releases, renderizado HTML/TXT/CSV/XLSX y rutas de ejecución portables.

## Instalación

Solo los núcleos que usan biblioteca estándar:

```bash
python -m pip install sharedcode_cores-1.0.0-py3-none-any.whl
```

Con GUI y RenderCore:

```bash
python -m pip install "sharedcode-cores[all] @ file:///ruta/sharedcode_cores-1.0.0-py3-none-any.whl"
```

Para desarrollar desde el repositorio:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[all,dev]"
python tools/run_public_validation.py
```

## Uso desde SmartFilter u otra herramienta

Durante desarrollo local puede instalarse en modo editable:

```bash
python -m pip install -e ../SharedCode[all]
```

Una aplicación compilada con PyInstaller incluye internamente los módulos que utiliza. El usuario del portable no instala SharedCode por separado.

## Principio de arquitectura

```text
SharedCode aporta infraestructura reutilizable.
Cada herramienta conserva sus reglas de negocio.
Cada release final es autosuficiente.
```

## Compatibilidad

- Windows: soportado.
- Linux: objetivo actual de portabilidad y soportado por los núcleos documentados.
- macOS: fuera del alcance actual.

## Licencia

SharedCode se publica bajo la [licencia MIT](LICENSE).
