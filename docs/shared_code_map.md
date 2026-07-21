# SharedCode Map

Mapa generado automáticamente desde los `README.md` de cada Core.

```text
SharedCode
├─ AppCore
│  └─ Identidad, metadatos y datos generales de cada herramienta externa.
├─ CliCore
│  └─ Argumentos, flags, códigos de salida y comportamiento común de consola.
├─ ConfigCore
│  └─ Carga, creación y validación de configuraciones JSON.
├─ FileScanCore
│  └─ `FileScanCore` recorre carpetas de forma segura, detecta marcadores y coordina trabajadores concurrentes con cola limitada.
├─ DateTimeCore
│  └─ Fechas, horas, timestamps UTC/locales y conversión desde epoch seconds con formato estándar para todo el ecosistema.
├─ FileSystemInfoCore
│  └─ Metadata, tamaños, fechas y errores de filesystem.
├─ GuiCore
│  └─ Componentes visuales reutilizables para herramientas con GUI e iconos centralizados Windows/Linux.
├─ JsonContractCore
│  └─ Creación, validación y análisis de contratos JSON estándar.
├─ LoggingCore
│  └─ Logs estándar en consola y archivo.
├─ ProcessRunnerCore
│  └─ Ejecución controlada de comandos externos.
├─ PlatformCore
│  └─ Capa de plataforma para centralizar diferencias entre Windows y Linux: detección del sistema, rutas convencionales, apertura de archivos/carpetas, archivos ocultos, symlinks/reparse points y sufijos de ejecutables/scripts.
├─ ReleaseCore
│  └─ Ayudas para estructura de release, manifest y validaciones de empaquetado.
├─ ToolRuntimeCore
│  └─ Rutas runtime/output/logs/temp de herramienta; se complementa con PlatformCore para rutas nativas por sistema.
```

## Inventario

| Core | Estado | Resumen |
|---|---|---|
| `AppCore` | Base inicial funcional | Identidad, metadatos y datos generales de cada herramienta externa. |
| `CliCore` | Base inicial funcional | Argumentos, flags, códigos de salida y comportamiento común de consola. |
| `ConfigCore` | Base inicial funcional | Carga, creación y validación de configuraciones JSON. |
| `FileScanCore` | Base concurrente funcional | `FileScanCore` recorre carpetas de forma segura, detecta marcadores y coordina trabajadores concurrentes con cola limitada. |
| `DateTimeCore` | Base inicial funcional para consistencia JSON y logs. | Fechas, horas, timestamps UTC/locales y conversión desde epoch seconds con formato estándar para todo el ecosistema. |
| `FileSystemInfoCore` | Base inicial funcional | Metadata, tamaños, fechas y errores de filesystem. |
| `GuiCore` | Base visual estable con iconos heredables | Componentes visuales reutilizables para herramientas con GUI e iconos centralizados Windows/Linux. |
| `JsonContractCore` | Base inicial funcional | Creación, validación y análisis de contratos JSON estándar. |
| `LoggingCore` | Base inicial funcional | Logs estándar en consola y archivo. |
| `ProcessRunnerCore` | Base inicial funcional | Ejecución controlada de comandos externos. |
| `PlatformCore` | Base inicial portable Windows/Linux. | Capa de plataforma para centralizar diferencias entre Windows y Linux: detección del sistema, rutas convencionales, apertura de archivos/carpetas, archivos ocultos, symlinks/reparse points y sufijos de ejecutables/scripts. |
| `ReleaseCore` | Base inicial funcional | Ayudas para estructura de release, manifest y validaciones de empaquetado. |
| `ToolRuntimeCore` | Base inicial funcional | Rutas runtime/output/logs/temp de herramienta; se complementa con PlatformCore para rutas nativas por sistema. |

## Regla de arquitectura

```text
SharedCode se usa en desarrollo.
Cada herramienta empaqueta lo que necesita.
Toolkit no depende de SharedCode.
Toolkit consume releases estables por manifest.
```
