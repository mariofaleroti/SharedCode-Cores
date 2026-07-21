"""Filesystem helpers that hide OS-specific metadata details."""

from __future__ import annotations

import os
from pathlib import Path

from .constants import WINDOWS_HIDDEN_ATTRIBUTE, WINDOWS_REPARSE_POINT_ATTRIBUTE
from .paths import normalize_path


def _file_attributes(path: Path) -> int:
    try:
        stat_result = path.stat(follow_symlinks=False)
    except OSError:
        return 0
    return int(getattr(stat_result, "st_file_attributes", 0) or 0)


def is_hidden(path: str | os.PathLike[str]) -> bool:
    """Return True when a path is hidden on Windows or Linux conventions."""

    target = normalize_path(path, resolve=False)
    if target.name.startswith(".") and target.name not in {".", ".."}:
        return True
    return bool(_file_attributes(target) & WINDOWS_HIDDEN_ATTRIBUTE)


def is_symlink_or_reparse(path: str | os.PathLike[str]) -> bool:
    """Return True for POSIX symlinks or Windows reparse points/junctions."""

    target = normalize_path(path, resolve=False)
    try:
        if target.is_symlink():
            return True
    except OSError:
        return False
    return bool(_file_attributes(target) & WINDOWS_REPARSE_POINT_ATTRIBUTE)
