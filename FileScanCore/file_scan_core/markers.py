"""
Marker scanning utilities.

DESIGN:
A marker is only a file or folder name found inside a directory.
FileScanCore must not interpret the marker meaning.

Examples:
- ".git" may be useful to a Git-related tool.
- "tool_manifest.json" may be useful to a release validator.
- "pyproject.toml" may be useful to a Python project analyzer.
"""

from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path

from .errors import build_scan_error, build_validation_error
from .models import DirectoryWalkStats, MarkerMatch, MarkerScanResult, ScanError
from .walker import ProgressCallback, iter_safe_directories


def validate_marker_name(marker_name: str) -> str:
    """
    Validates and normalizes a marker name.

    WARNING:
    Marker names must be simple names, not relative paths.
    """

    if marker_name is None:
        raise ValueError("Marker name cannot be None.")

    clean_marker_name = str(marker_name).strip()

    if not clean_marker_name:
        raise ValueError("Marker name cannot be empty.")

    if clean_marker_name in {".", ".."}:
        raise ValueError("Marker name cannot be '.' or '..'.")

    if "/" in clean_marker_name or "\\" in clean_marker_name:
        raise ValueError("Marker name cannot contain path separators.")

    return clean_marker_name


def directory_contains_marker(directory_path: str | Path, marker_name: str) -> bool:
    """
    Checks whether a directory contains a marker.

    WARNING:
    Do not assume markers are always directories.
    For example, .git can be a directory or a file depending on the Git setup.
    """

    clean_marker_name = validate_marker_name(marker_name)
    marker_path = Path(directory_path) / clean_marker_name

    try:
        # DESIGN: Marker detection is based on name presence, not on traversal.
        # os.path.lexists() also reports broken symlinks as present markers.
        return os.path.lexists(marker_path)
    except OSError:
        return False


def _normalize_root_paths(root_paths: str | Path | Iterable[str | Path]) -> list[Path]:
    """Normalizes one or more root paths into a concrete Path list."""

    if isinstance(root_paths, (str, Path)):
        return [Path(root_paths).expanduser()]

    return [Path(root_path).expanduser() for root_path in root_paths]


def _safe_marker_exists(
    directory_path: Path,
    marker_name: str,
    errors: list[ScanError],
) -> bool:
    """Checks marker existence and records non-fatal filesystem errors."""

    marker_path = directory_path / marker_name

    try:
        return os.path.lexists(marker_path)
    except OSError as error:
        errors.append(build_scan_error(marker_path, error))
        return False


def find_marker_directories(
    root_paths: str | Path | Iterable[str | Path],
    marker_name: str,
    skipped_directory_names: list[str] | set[str] | tuple[str, ...] | None = None,
    skipped_directory_keywords: list[str] | set[str] | tuple[str, ...] | None = None,
    max_depth: int | None = None,
    stop_descending_on_match: bool = True,
    follow_symlinks: bool = False,
    use_default_skipped_directory_names: bool = True,
    progress_callback: ProgressCallback | None = None,
) -> MarkerScanResult:
    """
    Finds directories that contain a specific marker.

    DESIGN:
    This function only detects marker presence.
    The consuming tool decides what the marker means.
    """

    try:
        clean_marker_name = validate_marker_name(marker_name)
    except ValueError as error:
        result = MarkerScanResult(marker_name=str(marker_name).strip())
        result.errors.append(
            build_validation_error(
                path=Path("."),
                error_type="invalid_marker_name",
                message=str(error),
            )
        )
        return result

    result = MarkerScanResult(marker_name=clean_marker_name)

    for root in _normalize_root_paths(root_paths):
        result.root_paths.append(root)

        errors: list[ScanError] = []
        stats = DirectoryWalkStats()
        marker_presence_cache: dict[Path, bool] = {}

        def marker_exists_for(directory_path: Path) -> bool:
            if directory_path not in marker_presence_cache:
                marker_presence_cache[directory_path] = _safe_marker_exists(
                    directory_path=directory_path,
                    marker_name=clean_marker_name,
                    errors=errors,
                )

            return marker_presence_cache[directory_path]

        def should_skip_children(directory_path: Path) -> bool:
            if not stop_descending_on_match:
                return False

            # DESIGN:
            # A matched directory may be reported without scanning its children.
            # This keeps marker discovery useful for boundaries such as repositories
            # or released tool folders.
            return marker_exists_for(directory_path)

        for directory_path, depth in iter_safe_directories(
            root_path=root,
            skipped_directory_names=skipped_directory_names,
            skipped_directory_keywords=skipped_directory_keywords,
            max_depth=max_depth,
            include_root=True,
            follow_symlinks=follow_symlinks,
            use_default_skipped_directory_names=use_default_skipped_directory_names,
            progress_callback=progress_callback,
            errors=errors,
            stats=stats,
            should_skip_children=should_skip_children,
        ):
            if marker_exists_for(directory_path):
                result.matches.append(
                    MarkerMatch(
                        root_path=root,
                        directory_path=directory_path,
                        marker_path=directory_path / clean_marker_name,
                        marker_name=clean_marker_name,
                        depth=depth,
                    )
                )

        result.scanned_count += stats.scanned_count
        result.skipped_count += stats.skipped_count
        result.policy_skipped_count += stats.policy_skipped_count
        result.link_or_reparse_skipped_count += stats.link_or_reparse_skipped_count
        result.name_skipped_count += stats.name_skipped_count
        result.keyword_skipped_count += stats.keyword_skipped_count
        result.revisited_skipped_count += stats.revisited_skipped_count
        result.errors.extend(errors)

    return result
