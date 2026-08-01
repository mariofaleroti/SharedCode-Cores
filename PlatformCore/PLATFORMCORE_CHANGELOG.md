# PlatformCore Changelog

## vNext - Portable path resolution semantics

- `resolve=False` now applies to context variables as well as the final path.
- Rooted paths without a Windows drive are no longer incorrectly rebased under
  `base_dir`.
- Added deterministic Windows/Linux simulation coverage without host filesystem
  resolution.

## vNext - Apertura nativa de PDF en Windows

- `open_path()` delega archivos PDF a Explorer en Windows para que la asociación predeterminada se resuelva de forma confiable.
- Conserva `os.startfile(..., "open")` para los demás formatos y como fallback cuando Explorer no puede iniciarse.
- Agrega pruebas unitarias específicas para PDF y archivos no PDF.

## vNext - Portable path resolver

- Added `resolve_portable_path()` and `resolve_portable_paths()` to centralize OS-neutral config path resolution.
- Added shared tokens such as `${USER_HOME}`, `${DOCUMENTS}`, `${BASE_DIR}`, `${PROJECT_ROOT}`, `${CONFIG_DIR}`, `${OUTPUT_DIR}`, `${LOGS_DIR}`, `${TEMP_DIR}`, `${RUNTIME_DIR}`, `${APP_DATA}` and `${CACHE_DIR}`.
- Documented the resolver as the preferred replacement for hardcoded tool paths in consuming projects.


## v0.1.0-dev

- Nuevo core `PlatformCore` para preparar ShareCode para Windows/Linux sin tocar herramientas consumidoras.
- Detección explícita de plataforma: `windows`, `linux`, `unsupported`.
- Rutas convencionales por sistema:
  - Windows: `LOCALAPPDATA` / `APPDATA`.
  - Linux: XDG (`XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_STATE_HOME`, `XDG_CACHE_HOME`) con fallbacks estándar.
- Helpers de apertura:
  - `open_path(path)`
  - `open_folder(path)`
  - `reveal_in_folder(path)`
- Builders testeables de comandos de apertura para evitar disparar ventanas durante tests.
- Helpers de filesystem:
  - `is_hidden(path)`
  - `is_symlink_or_reparse(path)`
- Helpers de sufijos:
  - `get_executable_suffix()`
  - `get_script_suffix()`
- Tests unitarios de comportamiento Windows/Linux.
