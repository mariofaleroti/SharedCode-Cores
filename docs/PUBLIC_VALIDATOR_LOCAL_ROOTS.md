# Public validator local-root policy

`tools/run_public_validation.py` is designed to run directly from a normal Git
clone with a project-local virtual environment.

## Ignored local roots

The validator deliberately excludes these top-level directories from cleanup
and public-tree inspection:

- `.git`
- `.venv`

They are local infrastructure, not release payload.

## Still forbidden

Generated artifacts remain forbidden everywhere else in the project tree,
including:

- `__pycache__`
- `build`
- `dist`
- `output`
- `.pytest_cache`
- `sharedcode_cores.egg-info`
- `.pyc`, `.pyo`, and `.pyd` files

The validator prunes a forbidden generated directory after reporting its root,
preventing thousands of redundant descendant paths in one error.

## Safety guarantee

Cleanup never traverses or mutates `.git` or `.venv`. In particular, compiled
dependency files inside the virtual environment are preserved.
