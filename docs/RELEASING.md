# Releasing SharedCode

1. Update `SharedCodeMeta/sharedcode_meta/__init__.py`.
2. Update `CHANGELOG.md`.
3. Run:

```bash
python tools/run_public_validation.py
```

4. Confirm that `dist/` contains the expected wheel and source archive.
5. Create a Git tag matching the version, for example `v1.0.0`.
6. Publish the generated artifacts in the corresponding GitHub Release.

Do not commit `dist/`, `build/`, or `*.egg-info` directories.
