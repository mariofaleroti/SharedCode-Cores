# Guía rápida de portabilidad

## Regla principal

Las herramientas consumidoras no deberían preguntar directamente por Windows/Linux salvo que sea inevitable. Deben pedir una intención a `PlatformCore`.

```python
from platform_core import open_path, open_folder, get_config_dir, resolve_portable_path

config_dir = get_config_dir("SmartFilter")
project_root = resolve_portable_path("${DOCUMENTS}/Proyectos")
open_path(report_path)
open_folder(results_folder)
```

## Reemplazos recomendados

| Antes | Ahora |
|---|---|
| `os.startfile(path)` | `platform_core.open_path(path)` |
| `subprocess.Popen(["xdg-open", path])` | `platform_core.open_path(path)` |
| rutas manuales `C:\\...` | `resolve_portable_path()` / `get_documents_dir()` / `get_app_data_dir()` / `Path` |
| `sys.platform` disperso | `get_platform_name()` solo en PlatformCore/adapters |
| detectar `.hidden` a mano | `is_hidden(path)` |
| chequear symlink/reparse a mano | `is_symlink_or_reparse(path)` |

## SmartFilter

Primer impacto previsto:

```text
- Abrir archivo original       -> open_path(path)
- Abrir carpeta               -> open_folder(path)
- Abrir vista destacada HTML   -> open_path(html_path)
- Resolver config/logs futuros -> get_config_dir/get_logs_dir cuando aplique
```

El motor de búsqueda, categorías, lectores y contrato JSON no deberían cambiar por este paso.
