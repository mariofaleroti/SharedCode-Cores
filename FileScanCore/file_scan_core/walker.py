"""
Safe directory walking utilities.

DESIGN:
FileScanCore walks paths and returns structured data.
It does not interpret files, execute commands or apply business rules.

WARNING:
Symlinks and Windows reparse points are not followed by default to reduce
recursive-loop risks and avoid escaping the expected scan tree.
"""

from __future__ import annotations

import os
from collections.abc import Callable, Iterator, Mapping
from pathlib import Path

from .errors import build_scan_error, build_validation_error
from .filters import (
    build_skipped_directory_names,
    normalize_keyword_list,
)
from .exclusion_policy import DirectoryExclusionMatch, DirectoryExclusionPolicy
from .models import DirectoryWalkResult, DirectoryWalkStats, ScanError

ProgressCallback = Callable[[Mapping[str, object]], None]
SkipChildrenCallback = Callable[[Path], bool]
DirectoryExcludedCallback = Callable[[DirectoryExclusionMatch], None]

_FILE_ATTRIBUTE_REPARSE_POINT = 0x0400


def _safe_path(path: str | Path) -> Path:
    """Returns an expanded Path without resolving symlinks."""

    return Path(path).expanduser()


def _is_reparse_point(path: Path) -> bool:
    """Returns True for Windows reparse points when that metadata is available."""

    try:
        attributes = path.stat(follow_symlinks=False).st_file_attributes
    except AttributeError:
        return False
    except OSError:
        return False

    return bool(attributes & _FILE_ATTRIBUTE_REPARSE_POINT)


def _is_entry_reparse_point(entry: os.DirEntry[str]) -> bool:
    """Returns True for Windows reparse-point entries when metadata is available."""

    try:
        attributes = entry.stat(follow_symlinks=False).st_file_attributes
    except AttributeError:
        return False
    except OSError:
        return False

    return bool(attributes & _FILE_ATTRIBUTE_REPARSE_POINT)


def _should_skip_link_or_reparse(path: Path, follow_symlinks: bool) -> bool:
    """Checks whether a path must be skipped because it redirects elsewhere."""

    if follow_symlinks:
        return False

    return path.is_symlink() or _is_reparse_point(path)


def _directory_identity(path: Path) -> str:
    """Returns a stable identity string used to avoid recursive directory loops."""

    # DESIGN:
    # When symlink following is explicitly enabled, different path strings may
    # still point to the same physical directory. Tracking the real path keeps
    # the walker from revisiting the same directory forever.
    return os.path.normcase(os.path.realpath(os.fspath(path)))


def _collect_child_directories(
    current_path: Path,
    follow_symlinks: bool,
    skipped_directory_names: set[str],
    skipped_directory_keywords: list[str],
    errors: list[ScanError],
    stats: DirectoryWalkStats,
    root_path: Path,
    exclusion_policy: DirectoryExclusionPolicy | None,
    directory_excluded_callback: DirectoryExcludedCallback | None,
) -> list[Path]:
    """Collects safe child directories from one directory level."""

    child_directories: list[Path] = []

    try:
        with os.scandir(current_path) as entries:
            for entry in entries:
                child_path = Path(entry.path)

                try:
                    if not follow_symlinks and (
                        entry.is_symlink() or _is_entry_reparse_point(entry)
                    ):
                        stats.skipped_count += 1
                        stats.link_or_reparse_skipped_count += 1
                        continue

                    if not entry.is_dir(follow_symlinks=follow_symlinks):
                        continue
                except OSError as error:
                    errors.append(build_scan_error(child_path, error, stage="directory_entry_check"))
                    continue

                if exclusion_policy is not None:
                    exclusion_match = exclusion_policy.match(child_path, root_path=root_path)
                    if exclusion_match is not None:
                        stats.skipped_count += 1
                        stats.policy_skipped_count += 1
                        if directory_excluded_callback is not None:
                            directory_excluded_callback(exclusion_match)
                        continue

                child_name = child_path.name.strip().casefold()
                if child_name in skipped_directory_names:
                    stats.skipped_count += 1
                    stats.name_skipped_count += 1
                    continue

                if skipped_directory_keywords and any(
                    keyword in child_name for keyword in skipped_directory_keywords
                ):
                    stats.skipped_count += 1
                    stats.keyword_skipped_count += 1
                    continue

                child_directories.append(child_path)
    except OSError as error:
        errors.append(build_scan_error(current_path, error, stage="directory_enumeration"))
        return child_directories

    # NOTE:
    # Reverse sorting compensates for LIFO stack traversal, preserving natural
    # alphabetical processing order for callers.
    return sorted(child_directories, key=lambda path: path.name.casefold(), reverse=True)


def iter_safe_directories(
    root_path: str | Path,
    skipped_directory_names: list[str] | set[str] | tuple[str, ...] | None = None,
    skipped_directory_keywords: list[str] | set[str] | tuple[str, ...] | None = None,
    max_depth: int | None = None,
    include_root: bool = True,
    follow_symlinks: bool = False,
    use_default_skipped_directory_names: bool = True,
    progress_callback: ProgressCallback | None = None,
    errors: list[ScanError] | None = None,
    stats: DirectoryWalkStats | None = None,
    should_skip_children: SkipChildrenCallback | None = None,
    exclusion_policy: DirectoryExclusionPolicy | None = None,
    directory_excluded_callback: DirectoryExcludedCallback | None = None,
) -> Iterator[tuple[Path, int]]:
    """
    Iterates directories safely from a root path.

    NOTE:
    This function is a generator. It yields directories as they are discovered.
    Use walk_directories() if a collected result object is needed.
    """

    root = _safe_path(root_path)

    if errors is None:
        errors = []

    if stats is None:
        stats = DirectoryWalkStats()

    effective_skipped_names = build_skipped_directory_names(
        additional_names=skipped_directory_names,
        use_defaults=use_default_skipped_directory_names,
    )
    effective_skipped_keywords = normalize_keyword_list(skipped_directory_keywords)

    if max_depth is not None and max_depth < 0:
        errors.append(
            build_validation_error(
                path=root,
                error_type="invalid_max_depth",
                message="max_depth cannot be negative.",
            )
        )
        return

    try:
        if not root.exists():
            errors.append(
                build_validation_error(
                    path=root,
                    error_type="path_not_found",
                    message="Root path does not exist.",
                )
            )
            return

        if not root.is_dir():
            errors.append(
                build_validation_error(
                    path=root,
                    error_type="not_a_directory",
                    message="Root path is not a directory.",
                )
            )
            return
    except OSError as error:
        errors.append(build_scan_error(root, error, stage="root_validation"))
        return

    if _should_skip_link_or_reparse(root, follow_symlinks=follow_symlinks):
        stats.skipped_count += 1
        stats.link_or_reparse_skipped_count += 1
        errors.append(
            build_validation_error(
                path=root,
                error_type="skipped_link_or_reparse_point",
                message="Root path is a symlink or reparse point and follow_symlinks is disabled.",
            )
        )
        return

    stack: list[tuple[Path, int]] = [(root, 0)]
    visited_directory_identities: set[str] = set()

    while stack:
        current_path, current_depth = stack.pop()

        if follow_symlinks:
            directory_identity = _directory_identity(current_path)

            if directory_identity in visited_directory_identities:
                stats.skipped_count += 1
                stats.revisited_skipped_count += 1
                continue

            visited_directory_identities.add(directory_identity)

        stats.scanned_count += 1

        if include_root or current_path != root:
            yield current_path, current_depth

        if progress_callback is not None:
            progress_callback(
                {
                    "stage": "scanning",
                    "current": stats.scanned_count,
                    "total": 0,
                    "percent": 0,
                    "path": str(current_path),
                    "depth": current_depth,
                }
            )

        if max_depth is not None and current_depth >= max_depth:
            continue

        if should_skip_children is not None and should_skip_children(current_path):
            continue

        child_directories = _collect_child_directories(
            current_path=current_path,
            follow_symlinks=follow_symlinks,
            skipped_directory_names=effective_skipped_names,
            skipped_directory_keywords=effective_skipped_keywords,
            errors=errors,
            stats=stats,
            root_path=root,
            exclusion_policy=exclusion_policy,
            directory_excluded_callback=directory_excluded_callback,
        )

        for child_path in child_directories:
            stack.append((child_path, current_depth + 1))


def walk_directories(
    root_path: str | Path,
    skipped_directory_names: list[str] | set[str] | tuple[str, ...] | None = None,
    skipped_directory_keywords: list[str] | set[str] | tuple[str, ...] | None = None,
    max_depth: int | None = None,
    include_root: bool = True,
    follow_symlinks: bool = False,
    use_default_skipped_directory_names: bool = True,
    progress_callback: ProgressCallback | None = None,
    exclusion_policy: DirectoryExclusionPolicy | None = None,
    directory_excluded_callback: DirectoryExcludedCallback | None = None,
) -> DirectoryWalkResult:
    """Collects directories from iter_safe_directories() into a result object."""

    root = _safe_path(root_path)
    errors: list[ScanError] = []
    stats = DirectoryWalkStats()

    directories = [
        directory_path
        for directory_path, _depth in iter_safe_directories(
            root_path=root,
            skipped_directory_names=skipped_directory_names,
            skipped_directory_keywords=skipped_directory_keywords,
            max_depth=max_depth,
            include_root=include_root,
            follow_symlinks=follow_symlinks,
            use_default_skipped_directory_names=use_default_skipped_directory_names,
            progress_callback=progress_callback,
            errors=errors,
            stats=stats,
            exclusion_policy=exclusion_policy,
            directory_excluded_callback=directory_excluded_callback,
        )
    ]

    return DirectoryWalkResult(
        root_path=root,
        directories=directories,
        errors=errors,
        scanned_count=stats.scanned_count,
        skipped_count=stats.skipped_count,
        policy_skipped_count=stats.policy_skipped_count,
        link_or_reparse_skipped_count=stats.link_or_reparse_skipped_count,
        name_skipped_count=stats.name_skipped_count,
        keyword_skipped_count=stats.keyword_skipped_count,
        revisited_skipped_count=stats.revisited_skipped_count,
    )
