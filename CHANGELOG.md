# Changelog

All notable changes to the public SharedCode distribution are documented here.

## 1.0.0 - 2026-07-21

### Added

- A single installable distribution named `sharedcode-cores`.
- Optional dependency groups for GUI and report rendering.
- Central package version exposed through `sharedcode_meta`.
- Console commands: `sharedcode-info`, `json-contract`, and `render-engine`.
- Public installation, contribution, security, and release documentation.
- Validation for source imports, wheel contents, isolated installation, and RenderCore templates.

### Changed

- SharedCode no longer depends on a sibling-folder `PYTHONPATH` layout.
- GuiCore and RenderCore expose the central distribution version.
- Packaging metadata and dependencies are managed by the root `pyproject.toml`.

### Removed

- Generated outputs, Python caches, private Git history, obsolete GitQuickMenu helpers, and patch-only root documents.
