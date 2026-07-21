# Contributing

Contributions are welcome when they preserve the separation between reusable infrastructure and tool-specific business logic.

## Development setup

```bash
python -m venv .venv
python -m pip install --upgrade pip
python -m pip install -e ".[all,dev]"
python tools/run_public_validation.py
```

## Rules

- Keep public imports backward compatible whenever practical.
- Put operating-system differences in `platform_core` instead of scattering them through consumers.
- Do not add SmartFilter, ShadowBackup, Toolkit, or other product-specific rules to a core.
- Add or update tests for behavior changes.
- Do not commit generated output, personal paths, secrets, real customer documents, or runtime state.
- Update documentation when a public API or installation step changes.

Open an issue before a large architectural change so the scope can be agreed first.
