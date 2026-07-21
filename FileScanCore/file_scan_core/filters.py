"""
Filtering helpers for FileScanCore.

DESIGN:
Filtering must stay generic.
Tool-specific include or exclude decisions must be passed by the consuming tool.
"""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

# DESIGN:
# These names are skipped during recursive traversal, but they may still be
# detected as markers from their parent directory.
DEFAULT_SKIPPED_DIRECTORY_NAMES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".mypy_cache",
        ".pytest_cache",
        ".ruff_cache",
        "node_modules",
        ".idea",
        ".vscode",
    }
)


def normalize_name_set(names: Iterable[str] | None) -> set[str]:
    """Returns normalized names for exact folder or file comparisons."""

    if not names:
        return set()

    return {str(name).strip().casefold() for name in names if str(name).strip()}


def normalize_keyword_list(keywords: Iterable[str] | None) -> list[str]:
    """Returns normalized keywords for contains-style comparisons."""

    if not keywords:
        return []

    return [
        str(keyword).strip().casefold()
        for keyword in keywords
        if str(keyword).strip()
    ]


def build_skipped_directory_names(
    additional_names: Iterable[str] | None = None,
    use_defaults: bool = True,
) -> set[str]:
    """Builds the effective exact-name skip set for directory traversal."""

    skipped_names: set[str] = set()

    if use_defaults:
        skipped_names.update(normalize_name_set(DEFAULT_SKIPPED_DIRECTORY_NAMES))

    skipped_names.update(normalize_name_set(additional_names))
    return skipped_names


def should_skip_name(
    name: str,
    skipped_names: set[str] | None = None,
    skipped_keywords: list[str] | None = None,
) -> bool:
    """Checks whether a name should be skipped by exact name or keyword."""

    clean_name = str(name).strip().casefold()

    if not clean_name:
        return True

    if skipped_names and clean_name in skipped_names:
        return True

    if skipped_keywords:
        return any(keyword in clean_name for keyword in skipped_keywords)

    return False


def should_skip_directory(
    directory_path: Path,
    skipped_directory_names: set[str] | None = None,
    skipped_directory_keywords: list[str] | None = None,
) -> bool:
    """Checks whether a directory should be skipped during traversal."""

    return should_skip_name(
        name=directory_path.name,
        skipped_names=skipped_directory_names,
        skipped_keywords=skipped_directory_keywords,
    )
