# Límites específicos por sistema operativo

Este documento deja claro qué partes de SharedCode son neutrales y qué partes contienen diferencias Windows/Linux de forma intencional.

## Regla principal

```text
Lo específico del sistema operativo debe estar concentrado.
No debe aparecer repartido por todas las herramientas.
```

El lugar oficial para diferencias Windows/Linux es `PlatformCore`, salvo casos muy justificados.

## Inventario actual

| Zona | Tipo | Estado | Comentario |
|---|---|---|---|
| `PlatformCore/platform_core/detection.py` | Windows/Linux | Correcto | Detecta plataforma soportada. macOS queda fuera de alcance. |
| `PlatformCore/platform_core/opener.py` | Windows/Linux | Correcto | Centraliza `os.startfile`/`xdg-open` mediante intención `open_path/open_folder`. |
| `PlatformCore/platform_core/paths.py` | Windows/Linux | Correcto | Centraliza AppData/XDG/config/logs/cache. |
| `PlatformCore/platform_core/filesystem.py` | Windows/Linux | Correcto | Centraliza ocultos, symlinks y reparse points. |
| `PlatformCore/platform_core/process.py` | Windows/Linux | Correcto | Sufijos `.exe`, `.cmd`, `.sh`. |
| `GuiCore/gui_core/windows/window_icon.py` | Windows/Linux visual | Aceptado | Aunque la carpeta se llame `windows`, el helper aplica iconos con fallback `.ico`/`.png`. Futuro: renombrar carpeta a `platform` si se quiere mayor claridad. |
| `RenderCore/scripts/*.ps1` | Windows-only | Aceptado temporal | Scripts oficiales actuales son PowerShell. Futuro: agregar equivalentes `.sh`. |
| `RenderCore/apps/render_engine/tool_manifest.json` | Windows release | Aceptado temporal | Actualmente apunta a `RenderEngine.exe`. Futuro: `entry_by_platform`. |
| Documentación con `powershell` o `C:\...` | Ejemplo Windows | Aceptado si está rotulado | Debe quedar claro cuando un ejemplo es Windows-only. |

## Qué NO debería aparecer fuera de PlatformCore

```text
os.startfile(...)
subprocess.Popen(["xdg-open", ...])
sys.platform para abrir archivos o decidir rutas comunes
rutas C:\Users\... como valor real de configuración compartida
asumir siempre .exe
asumir siempre .cmd
asumir siempre separador \\
```

Excepciones permitidas:

```text
- tests que validan comportamiento por plataforma
- documentación que muestra ejemplos rotulados
- scripts auxiliares claramente Windows-only o Linux-only
- adapters específicos de una herramienta cuando el negocio realmente depende del sistema
```

## Casos especiales por herramienta

Algunas herramientas pueden tener backend específico por sistema, aunque usen SharedCode.

Ejemplos:

```text
EventHealth Windows -> Windows Event Log / PowerShell / Get-WinEvent.
EventHealth Linux   -> futuro backend separado con journalctl/systemd logs.
SmartDisk Windows   -> smartctl.exe u otros binarios Windows.
SmartDisk Linux     -> smartctl Linux si se empaqueta/instala.
```

La regla es que el contrato de salida puede mantenerse igual aunque el backend cambie.

```text
Backend específico por OS -> JSON estándar común -> RenderCore común
```

## Checklist para código nuevo

Antes de aprobar código nuevo en SharedCode o una herramienta consumidora:

```text
[ ] Usa pathlib.Path.
[ ] No introduce rutas absolutas personales.
[ ] No llama os.startfile fuera de PlatformCore.
[ ] No llama xdg-open fuera de PlatformCore.
[ ] No asume .exe salvo release Windows.
[ ] No asume PowerShell salvo script Windows-only.
[ ] Maneja permisos/errores de ruta como no fatales cuando aplica.
[ ] No sigue symlinks/reparse por defecto salvo config explícita.
[ ] Documenta si algo es Windows-only o Linux-only.
```
