# Portabilidad Windows/Linux

Este documento define cómo escribir código en SharedCode y herramientas consumidoras para que no queden atadas a un sistema operativo.

## Alcance

```text
Windows: soportado.
Linux: soportado como objetivo de portabilidad inicial.
macOS: fuera de alcance por decisión actual del proyecto.
```

## Regla principal

Las herramientas concretas no deberían preguntar directamente por Windows/Linux si existe una función de SharedCode para pedir la intención.

```python
# Bien
from platform_core import open_path, get_config_dir

open_path(report_path)
config_dir = get_config_dir("SmartFilter")
```

```python
# Evitar en herramientas concretas
os.startfile(report_path)
subprocess.Popen(["xdg-open", str(report_path)])
if sys.platform.startswith("linux"):
    ...
```

## Reemplazos oficiales

| Necesidad | Usar | Evitar |
|---|---|---|
| Abrir archivo con app predeterminada | `PlatformCore.open_path(path)` | `os.startfile`, `xdg-open` directo |
| Abrir carpeta | `PlatformCore.open_folder(path)` | comandos de shell dispersos |
| Mostrar archivo en su carpeta | `PlatformCore.reveal_in_folder(path)` | explorador hardcodeado |
| Directorio de config de usuario | `PlatformCore.get_config_dir(tool_name)` | `C:\Users\...`, `~/.config` a mano |
| Directorio de logs nativo | `PlatformCore.get_logs_dir(tool_name)` | AppData/XDG escritos a mano |
| Ruta de documentos | `PlatformCore.get_documents_dir()` | `C:\Users\...\Documents` |
| Detectar plataforma | `PlatformCore.get_platform_name()` | `sys.platform` repartido |
| Archivo oculto | `PlatformCore.is_hidden(path)` | reglas duplicadas |
| Symlink/reparse | `PlatformCore.is_symlink_or_reparse(path)` | checks duplicados |
| Sufijo ejecutable | `PlatformCore.get_executable_suffix()` | asumir `.exe` |
| Sufijo script | `PlatformCore.get_script_suffix()` | asumir `.cmd` o `.sh` |

## Rutas

Usar siempre `pathlib.Path` para construir rutas.

```python
from pathlib import Path

project_dir = Path.home() / "Documents" / "Proyectos"
```

Evitar concatenar separadores:

```python
# Evitar
path = base + "\\output\\report.json"
```

## Archivos ocultos

Windows y Linux no ocultan archivos de la misma manera.

```text
Windows: atributo hidden.
Linux: nombre que empieza con punto.
```

La herramienta no debería resolver esto sola; debe usar `PlatformCore.is_hidden(path)`.

## Symlinks y reparse points

Regla del ecosistema:

```text
No seguir symlinks/reparse points por defecto.
Permitirlo solo si una configuración explícita lo habilita.
Registrar diagnóstico si una ruta se omite por seguridad.
```

Esto evita loops, rutas inesperadas y recorridos peligrosos.

## Mayúsculas/minúsculas

Windows suele ser case-insensitive. Linux suele ser case-sensitive.

Regla recomendada:

```text
Búsqueda de usuario: normalmente no sensible a mayúsculas.
Comparación técnica de rutas/archivos: respetar el sistema o definir política explícita.
```

## Permisos

En Linux es normal encontrar `Permission denied` en algunas rutas. En Windows también pueden aparecer carpetas bloqueadas.

Regla:

```text
Un error de lectura no debe romper todo el escaneo.
Debe registrarse como diagnóstico/error no fatal cuando corresponda.
```

## GUI e iconos

GuiCore soporta iconos centralizados:

```python
GuiAppConfig(
    icon_path="assets/app_icon.ico",      # recomendado Windows
    icon_png_path="assets/app_icon.png",  # recomendado Linux
)
```

Las ventanas secundarias pueden heredar el icono de la principal mediante `SecondaryWindowConfig.inherit_parent_icon`.

## Release

El código fuente puede ser común, pero el binario final no es universal.

```text
Windows -> build en Windows -> .exe
Linux   -> build en Linux   -> binario Linux o ejecución Python empaquetada
```

Modelo recomendado futuro:

```text
release/
  SmartFilter-windows-x64/
  SmartFilter-linux-x64/
```

## Validación mínima de portabilidad

Antes de declarar que una herramienta está preparada para Windows/Linux:

```text
1. compileall OK.
2. tests OK.
3. CLI abre --help.
4. lectura/escritura de JSON OK.
5. rutas con Path OK.
6. GUI abre si aplica.
7. open_path/open_folder funcionan si aplica.
8. release se genera en el sistema correspondiente si aplica.
```
