from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

from date_time_core import timestamp_seconds_to_utc_iso

from .models import DirectorySummary, PathInfo


def _error_dict(code: str, error: BaseException) -> Dict[str, Any]:
    return {
        "code": code,
        "message": str(error),
        "context": {"exception_type": type(error).__name__},
    }


def get_path_info(path: Path | str, *, follow_symlinks: bool = False) -> PathInfo:
    """Return metadata for one path without walking recursively."""
    target = Path(path).expanduser()

    try:
        exists = target.exists() if follow_symlinks else os.path.lexists(target)
        if not exists:
            return PathInfo(path=target, exists=False, name=target.name, suffix=target.suffix, parent=target.parent)

        stat_result = target.stat() if follow_symlinks else target.lstat()
        return PathInfo(
            path=target,
            exists=True,
            is_file=target.is_file(),
            is_dir=target.is_dir(),
            is_symlink=target.is_symlink(),
            name=target.name,
            suffix=target.suffix,
            parent=target.parent,
            size_bytes=stat_result.st_size if target.is_file() else None,
            created_at_utc=timestamp_seconds_to_utc_iso(stat_result.st_ctime),
            modified_at_utc=timestamp_seconds_to_utc_iso(stat_result.st_mtime),
            accessed_at_utc=timestamp_seconds_to_utc_iso(stat_result.st_atime),
            created_at_epoch_seconds=stat_result.st_ctime,
            modified_at_epoch_seconds=stat_result.st_mtime,
            accessed_at_epoch_seconds=stat_result.st_atime,
        )
    except OSError as error:
        return PathInfo(
            path=target,
            exists=False,
            name=target.name,
            suffix=target.suffix,
            parent=target.parent,
            error=_error_dict("PATH_INFO_ERROR", error),
        )


def get_directory_summary(path: Path | str) -> DirectorySummary:
    """Return a non-recursive summary for one directory."""
    target = Path(path).expanduser()

    if not target.exists():
        return DirectorySummary(path=target, exists=False)

    if not target.is_dir():
        return DirectorySummary(
            path=target,
            exists=True,
            error={
                "code": "PATH_NOT_DIRECTORY",
                "message": "Path is not a directory.",
                "context": {"path": str(target)},
            },
        )

    files_count = 0
    directories_count = 0
    symlinks_count = 0
    total_size = 0

    try:
        with os.scandir(target) as entries:
            for entry in entries:
                try:
                    if entry.is_symlink():
                        symlinks_count += 1
                    if entry.is_file(follow_symlinks=False):
                        files_count += 1
                        total_size += entry.stat(follow_symlinks=False).st_size
                    elif entry.is_dir(follow_symlinks=False):
                        directories_count += 1
                except OSError:
                    continue
    except OSError as error:
        return DirectorySummary(path=target, exists=True, error=_error_dict("DIRECTORY_SUMMARY_ERROR", error))

    return DirectorySummary(
        path=target,
        exists=True,
        files_count=files_count,
        directories_count=directories_count,
        symlinks_count=symlinks_count,
        total_file_size_bytes=total_size,
    )
