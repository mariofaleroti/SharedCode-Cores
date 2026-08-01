# Changelog

All notable changes to the public SharedCode distribution are documented here.

## 1.1.0 - 2026-08-01

### Added

- GuiCore layout profiles: `compact`, `standard`, and `comfortable`.
- Declarative sidebar, footer, and fixed primary-action contracts.
- Compact reusable form controls and card-header actions.
- Collapsible cards, key/value status views, and empty states.
- Metric cards, metric strips, and reusable tooltips.
- `GuiTaskRunner` with progress, cancellation, callback safety, and duplicate-task protection.
- Visual preference modes: `none`, `basic`, and `advanced`.
- Official neutral GuiCore 1.1 showcase and migration documentation.

### Fixed

- Safe `ResultsTable` headings when sorting callbacks are absent.
- Stable icon metadata paths across Windows and Linux.
- Owner-aware Tk callback cleanup and idempotent secondary-window closing.
- Python 3.13 Tcl command cleanup during settings-window shutdown.

### Changed

- GuiCore now exposes the stable 1.1 visual contract.
- SharedCode 1.0.0 remains available as an independent frozen release.
- Projects migrate explicitly and consume one exact SharedCode artifact.

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
