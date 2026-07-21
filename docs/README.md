# Documentación de SharedCode

`SharedCode` es la base común reutilizable para herramientas externas del ecosistema.

Su objetivo no es tomar código viejo y convertirlo a la fuerza en compartido. Su objetivo es diseñar módulos comunes claros para evitar repetir infraestructura entre herramientas.

## Documentos principales

| Documento | Para qué sirve |
|---|---|
| `CORE_RESPONSIBILITIES.md` | Explica qué hace cada core, qué no hace y quién debería consumirlo. |
| `PORTABILITY_WINDOWS_LINUX.md` | Define las reglas para que el código no quede atado a Windows. |
| `OS_SPECIFIC_BOUNDARIES.md` | Inventario de cosas específicas por sistema operativo y dónde deben vivir. |
| `shared_code_map.md` | Mapa resumido generado desde los README de los cores. |
| `../README.md` | Entrada rápida del proyecto. |

## Principio principal

```text
SharedCode alimenta herramientas externas en desarrollo.
Cada herramienta mantiene su lógica propia.
Cada herramienta genera un release autosuficiente.
Toolkit consume solo releases estables por manifest.
```

## Separación obligatoria

```text
Desarrollo ≠ Release ≠ Toolkit
```

En desarrollo, una herramienta puede importar módulos desde `SharedCode`.

En release, cada herramienta debe quedar autosuficiente. En Windows puede ser un `.exe`; en Linux puede ser un binario generado desde Linux o una carpeta ejecutable equivalente. En ambos casos, el release debe incluir internamente lo que necesita.

Toolkit no debe depender del código fuente de `SharedCode`. Toolkit solo debe ejecutar herramientas externas por `tool_manifest.json` y consumir sus salidas.

## Cores actuales

| Core | Responsabilidad corta | Portabilidad |
|---|---|---|
| `AppCore` | Ciclo común de app y contexto de ejecución. | Portable. |
| `CliCore` | Argumentos, flags y códigos de salida CLI. | Portable. |
| `ConfigCore` | Carga y validación de configuración JSON. | Portable. |
| `DateTimeCore` | Fechas, horas y timestamps estándar. | Portable. |
| `FileScanCore` | Escaneo seguro de carpetas/archivos. | Windows/Linux con cuidado de symlinks/reparse. |
| `FileSystemInfoCore` | Metadata puntual de archivos/carpetas. | Windows/Linux con diferencias documentadas. |
| `GuiCore` | Base visual CustomTkinter. | Windows/Linux; usa `.ico`/`.png` según entorno. |
| `JsonContractCore` | Contrato JSON estándar. | Portable. |
| `LoggingCore` | Logs estándar. | Portable. |
| `PlatformCore` | Diferencias Windows/Linux. | Es el punto oficial de adaptación por sistema. |
| `ProcessRunnerCore` | Ejecución controlada de procesos. | Portable; el comando concreto puede ser específico del sistema. |
| `ReleaseCore` | Preparar carpetas de release. | Portable; el build final depende del sistema. |
| `RenderCore` | Renderizado HTML/TXT/CSV/XLSX desde JSON estándar. | Portable; algunos scripts auxiliares actuales son Windows/PowerShell. |
| `ToolRuntimeCore` | Rutas runtime/output/logs/temp de herramienta. | Portable para releases; se complementa con PlatformCore para rutas nativas. |

## Regla de decisión

Antes de crear una función, clase o archivo nuevo, preguntar:

```text
¿Esto podría servir a más de una herramienta externa?
```

Si la respuesta es sí, se evalúa para `SharedCode`.

Si la respuesta es no, queda dentro de la herramienta.

Si hay duda, queda primero dentro de la herramienta hasta que aparezca un segundo caso real.
