# SharedCode

Reusable Python infrastructure cores for building desktop and command-line tools without duplicating common plumbing.

[Leer en español](README.es.md)

## What it provides

SharedCode is distributed as one Python package, `sharedcode-cores`, while preserving small, focused import namespaces:

```python
from file_scan_core import walk_files
from platform_core import open_path
from render_core import render_report
```

The project currently includes:

| Package | Responsibility |
|---|---|
| `app_core` | Application lifecycle and normalized execution results. |
| `cli_core` | Common CLI arguments, parsing helpers, and exit codes. |
| `config_core` | JSON configuration loading, merging, validation, and writing. |
| `date_time_core` | Consistent UTC/local timestamps and formatting. |
| `file_scan_core` | Safe directory walking and bounded concurrent processing. |
| `file_system_info_core` | File and directory metadata inspection. |
| `gui_core` | Reusable CustomTkinter windows, dialogs, controls, themes, and preferences. |
| `json_contract_core` | Strict validation for the standard JSON contract. |
| `logging_core` | Structured console and file logging. |
| `platform_core` | Central Windows/Linux filesystem and opening behavior. |
| `process_runner_core` | Controlled external-process execution. |
| `release_core` | Release-folder collection and filtering helpers. |
| `render_core` | HTML, TXT, CSV, and XLSX rendering from validated JSON. |
| `tool_runtime_core` | Portable runtime, output, log, and temporary paths. |

## Installation

Core packages only:

```bash
python -m pip install sharedcode_cores-1.0.0-py3-none-any.whl
```

With GUI support:

```bash
python -m pip install "sharedcode-cores[gui] @ file:///path/to/sharedcode_cores-1.0.0-py3-none-any.whl"
```

With rendering support:

```bash
python -m pip install "sharedcode-cores[render] @ file:///path/to/sharedcode_cores-1.0.0-py3-none-any.whl"
```

For local development from a clone:

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[all,dev]"
python tools/run_public_validation.py
```

## Consuming it from another project

A consuming project should pin a tested SharedCode release. During local development, editable installation is convenient:

```bash
python -m pip install -e ../SharedCode[all]
```

Normal users of compiled applications do not install SharedCode separately. Tools built with PyInstaller bundle the required modules inside their release.

## Command-line entry points

```bash
sharedcode-info
json-contract --help
render-engine --help
```

## Architecture principle

```text
SharedCode provides reusable infrastructure.
Each tool keeps its own business rules.
Each released tool remains self-contained.
```

See [the architecture documentation](docs/CORE_RESPONSIBILITIES.md) and [installation guide](docs/INSTALLATION.md).

## Platform support

- Windows: supported.
- Linux: supported as the current portability target.
- macOS: not currently supported or tested.

## Tests

The public validation script runs the complete test suite, builds a wheel, installs it into an isolated virtual environment, verifies every import, and confirms that RenderCore templates are packaged.

```bash
python tools/run_public_validation.py
```

## License

SharedCode is available under the [MIT License](LICENSE).
