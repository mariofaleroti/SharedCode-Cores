from __future__ import annotations

from pathlib import Path
from typing import Iterable

DEFAULT_SKIPPED_DIRECTORY_NAMES = frozenset({
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "venv",
})

DEFAULT_SKIPPED_FILE_SUFFIXES = frozenset({
    ".pyc",
    ".pyo",
    ".tmp",
    ".bak",
})


def should_skip_path(
    relative_path: Path,
    *,
    skipped_directory_names: Iterable[str] = DEFAULT_SKIPPED_DIRECTORY_NAMES,
    skipped_file_suffixes: Iterable[str] = DEFAULT_SKIPPED_FILE_SUFFIXES,
) -> bool:
    """Return True when a relative path should not be copied to a release package."""
    directory_names = {name.lower() for name in skipped_directory_names}
    file_suffixes = {suffix.lower() for suffix in skipped_file_suffixes}

    for part in relative_path.parts[:-1]:
        if part.lower() in directory_names:
            return True

    if relative_path.parts and relative_path.parts[-1].lower() in directory_names:
        return True

    return relative_path.suffix.lower() in file_suffixes
