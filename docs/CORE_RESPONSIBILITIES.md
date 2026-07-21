# Responsabilidades de cores

Este documento define para qué sirve cada parte de SharedCode. La intención es que cualquier persona pueda entrar al proyecto y entender qué módulo usar sin mezclar responsabilidades.

## Regla global

```text
Un core compartido resuelve infraestructura común.
Una herramienta concreta resuelve negocio concreto.
```

Si un módulo empieza a saber demasiado sobre SmartFilter, ShadowBackup, EventHealth, SmartDisk o Toolkit, probablemente está en el lugar incorrecto.

## Mapa por core

| Core | Sirve para | No debe hacer | Consumidores típicos |
|---|---|---|---|
| `AppCore` | Ordenar el ciclo de vida común de una herramienta, crear/transportar contexto y normalizar resultado de ejecución. | Parsear CLI, cargar config por sí mismo, escanear archivos, ejecutar lógica propia de una herramienta. | Herramientas CLI o GUI que quieran un arranque común. |
| `CliCore` | Crear argumentos comunes, flags estándar y códigos de salida. | Ejecutar la herramienta, escribir reportes, decidir negocio. | CLIs de SmartFilter, ShadowBackup, RenderEngine, etc. |
| `ConfigCore` | Leer JSON, validar estructura de configuración, aplicar defaults y devolver errores/diagnósticos. | Interpretar reglas finales de una herramienta o reemplazar JsonContractCore. | Cualquier herramienta con `settings.json` o config estándar. |
| `DateTimeCore` | Generar timestamps UTC/locales consistentes. | Decidir zonas horarias de negocio o formatos especiales de UI. | Logs, contratos JSON, runtime, reportes. |
| `FileScanCore` | Recorrer carpetas de forma segura y coordinar procesamiento concurrente limitado de candidatos mediante trabajadores genéricos. | Elegir candidatos, leer formatos concretos por sí mismo, interpretar resultados finales, ejecutar Git o renderizar reportes. | SmartFilter, ShadowBackup, analizadores de archivos. |
| `FileSystemInfoCore` | Obtener metadata puntual de una ruta: tamaño, fechas, tipo, errores, resumen liviano. | Recorrer árboles completos o decidir reglas de negocio. | Reportes, diagnósticos, validaciones de rutas. |
| `GuiCore` | Proveer base visual CustomTkinter: ventana principal, sidebar, cards, tablas, diálogos, ventanas secundarias, preferencias visuales e iconos. | Buscar archivos, manejar categorías, ejecutar procesos o guardar negocio propio de una herramienta. | SmartFilter, EventHealth GUI, futuras herramientas visuales. |
| `JsonContractCore` | Validar y analizar el contrato estándar `meta/summary/report_brief/data/diagnostics/errors`. | Aceptar contratos legacy/permisivos o corregir silenciosamente datos inválidos. | Todas las herramientas que generan JSON estándar. |
| `LoggingCore` | Crear logs estándar en consola/archivo con códigos y contexto. | Decidir alertas de negocio o interpretar significado final del evento. | Todas las herramientas. |
| `PlatformCore` | Centralizar diferencias Windows/Linux: plataforma, rutas nativas, abrir archivo/carpeta, ocultos, symlink/reparse y sufijos. | Convertirse en lógica de negocio, crear servicios, instalar dependencias o reemplazar ToolRuntimeCore. | Todas las herramientas que necesiten tocar el sistema operativo. |
| `ProcessRunnerCore` | Ejecutar procesos externos de forma controlada con stdout/stderr/exit_code/timeout. | Decidir si un `git status`, `smartctl` o comando externo es bueno/malo a nivel negocio. | ShadowBackup, SmartDisk, wrappers CLI. |
| `ReleaseCore` | Preparar carpetas de release: copiar, limpiar, excluir desarrollo y validar estructura base. | Compilar ejecutables, reemplazar PyInstaller o decidir manifest de una herramienta concreta. | Scripts de build/release. |
| `RenderCore` | Tomar JSON estándar válido y producir HTML/TXT/CSV/XLSX. | Recolectar datos, diagnosticar equipos o aceptar contratos viejos. | Toolkit, SmartDisk, EventHealth, reportes externos. |
| `ToolRuntimeCore` | Crear contexto de ejecución portable: base_dir, output, logs, temp, runtime, run_id y metadatos. | Resolver rutas nativas de usuario tipo AppData/XDG o abrir archivos; eso va en PlatformCore. | Todas las herramientas. |

## Límites importantes

### PlatformCore vs ToolRuntimeCore

```text
ToolRuntimeCore = carpetas internas de ejecución de una herramienta/release.
PlatformCore    = convenciones del sistema operativo: AppData, XDG, abrir archivo/carpeta, sufijos.
```

Ejemplo:

```python
# Runtime portable dentro del release o proyecto
runtime.output_dir

# Config nativa del usuario según OS
get_config_dir("SmartFilter")
```

### FileScanCore vs FileSystemInfoCore

```text
FileScanCore        = caminar árboles y coordinar trabajadores genéricos con cola limitada.
FileSystemInfoCore  = describir una ruta individual o resumen liviano.
```

### GuiCore vs herramienta concreta

```text
GuiCore da controles visuales.
SmartFilter decide qué significa buscar.
EventHealth decide qué eventos mostrar.
ShadowBackup decide qué repositorio respaldar.
```

## Señales de alerta

Algo probablemente está mal ubicado si aparece esto dentro de un core neutral:

```text
- nombres de herramientas concretas usados para decidir lógica
- rutas absolutas de usuario
- `os.startfile` fuera de PlatformCore
- `xdg-open` fuera de PlatformCore
- `sys.platform` disperso fuera de PlatformCore/adapters muy justificados
- comandos PowerShell dentro de lógica común portable
- reglas de negocio mezcladas con helpers genéricos
```
