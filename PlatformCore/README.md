# PlatformCore

## Resumen

Capa de plataforma para centralizar diferencias entre Windows y Linux: detección del sistema, rutas convencionales, apertura de archivos/carpetas, archivos ocultos, symlinks/reparse points y sufijos de ejecutables/scripts.

## Estado actual

Base inicial portable Windows/Linux.

## Objetivo

Evitar que las herramientas consumidoras llamen directamente a APIs del sistema operativo como `os.startfile`, `xdg-open`, rutas `AppData`, rutas XDG o comparaciones dispersas con `os.name`/`sys.platform`.

```text
Herramienta concreta
  -> PlatformCore.open_path(path)
  -> PlatformCore decide Windows/Linux
```

## Alcance

- Windows y Linux solamente.
- No implementa lógica de negocio de ninguna herramienta.
- No crea servicios, tareas programadas ni instaladores.
- No reemplaza `ToolRuntimeCore`; lo complementa para decisiones nativas del sistema operativo.

## API principal

```python
from platform_core import (
    get_platform_name,
    is_windows,
    is_linux,
    get_documents_dir,
    get_app_data_dir,
    get_config_dir,
    get_logs_dir,
    get_cache_dir,
    resolve_portable_path,
    resolve_portable_paths,
    open_path,
    open_folder,
    reveal_in_folder,
    is_hidden,
    is_symlink_or_reparse,
)
```


## Resolución portable de rutas configurables

`resolve_portable_path()` centraliza rutas de configuración que deben funcionar igual en Windows y Linux, evitando valores duros como `C:\Users\...` dentro de las herramientas.

Tokens soportados principales:

```text
${USER_HOME}   -> carpeta personal del usuario
${HOME}        -> alias de ${USER_HOME}
${DOCUMENTS}   -> Documents del usuario
${BASE_DIR}    -> raíz/base runtime indicada por la herramienta
${PROJECT_ROOT}-> raíz del proyecto, o base_dir si no se indica otra
${CONFIG_DIR}  -> carpeta de configuración indicada o convencional
${OUTPUT_DIR}  -> carpeta output indicada por runtime
${LOGS_DIR}    -> carpeta logs indicada por runtime
${TEMP_DIR}    -> carpeta temporal indicada por runtime
${RUNTIME_DIR} -> carpeta runtime indicada por runtime
${APP_DATA}    -> carpeta app data convencional por sistema
${CACHE_DIR}   -> carpeta cache convencional por sistema
```

Ejemplo:

```python
from platform_core import resolve_portable_path

root = resolve_portable_path(
    "${DOCUMENTS}/Proyectos",
    base_dir=runtime.base_dir,
    output_dir=runtime.output_dir,
    logs_dir=runtime.logs_dir,
    temp_dir=runtime.temp_dir,
    runtime_dir=runtime.runtime_dir,
    tool_name="ShadowBackup",
)
```

## Convenciones

```text
Windows app data : %LOCALAPPDATA%/<ToolName>
Windows config   : %LOCALAPPDATA%/<ToolName>/config
Windows logs     : %LOCALAPPDATA%/<ToolName>/logs
Windows cache    : %LOCALAPPDATA%/<ToolName>/cache

Linux app data   : $XDG_DATA_HOME/<ToolName> o ~/.local/share/<ToolName>
Linux config     : $XDG_CONFIG_HOME/<ToolName> o ~/.config/<ToolName>
Linux logs       : $XDG_STATE_HOME/<ToolName>/logs o ~/.local/state/<ToolName>/logs
Linux cache      : $XDG_CACHE_HOME/<ToolName> o ~/.cache/<ToolName>
```

## Regla de arquitectura

Las herramientas deben pedir una intención, no implementar el detalle del sistema operativo.

```python
# Bien
open_path(report_path)

# En Windows los PDF se delegan a Explorer para resolver de forma
# confiable la aplicación predeterminada; los demás formatos usan
# la apertura nativa normal.

# Evitar dentro de herramientas concretas
os.startfile(report_path)
subprocess.Popen(["xdg-open", report_path])
```
