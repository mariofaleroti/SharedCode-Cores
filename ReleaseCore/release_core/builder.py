from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List, Tuple

from .filters import DEFAULT_SKIPPED_DIRECTORY_NAMES, DEFAULT_SKIPPED_FILE_SUFFIXES, should_skip_path
from .models import ReleaseItem, ReleaseResult


def _resolve(path: Path | str) -> Path:
    return Path(path).expanduser().resolve()


def collect_release_files(
    source_dir: Path | str,
    *,
    skipped_directory_names: Iterable[str] = DEFAULT_SKIPPED_DIRECTORY_NAMES,
    skipped_file_suffixes: Iterable[str] = DEFAULT_SKIPPED_FILE_SUFFIXES,
) -> Tuple[List[Path], List[str]]:
    """Collect files that should be copied to a release package."""
    source = _resolve(source_dir)
    if not source.exists():
        raise FileNotFoundError(f"Source directory does not exist: {source}")
    if not source.is_dir():
        raise NotADirectoryError(f"Source path is not a directory: {source}")

    files: List[Path] = []
    skipped: List[str] = []

    for path in sorted(source.rglob("*")):
        relative_path = path.relative_to(source)
        if should_skip_path(
            relative_path,
            skipped_directory_names=skipped_directory_names,
            skipped_file_suffixes=skipped_file_suffixes,
        ):
            skipped.append(str(relative_path))
            continue
        if path.is_file():
            files.append(path)

    return files, skipped


def clean_release_dir(release_dir: Path | str) -> None:
    """Delete a release directory if it exists, then recreate it."""
    release = _resolve(release_dir)
    if release.exists():
        shutil.rmtree(release)
    release.mkdir(parents=True, exist_ok=True)


def copy_release_files(
    source_dir: Path | str,
    release_dir: Path | str,
    *,
    clean: bool = False,
    skipped_directory_names: Iterable[str] = DEFAULT_SKIPPED_DIRECTORY_NAMES,
    skipped_file_suffixes: Iterable[str] = DEFAULT_SKIPPED_FILE_SUFFIXES,
) -> ReleaseResult:
    """Copy release files from source_dir to release_dir and return a structured result."""
    source = _resolve(source_dir)
    release = _resolve(release_dir)
    result = ReleaseResult(source_dir=source, release_dir=release)

    try:
        if clean:
            clean_release_dir(release)
        else:
            release.mkdir(parents=True, exist_ok=True)

        files, skipped = collect_release_files(
            source,
            skipped_directory_names=skipped_directory_names,
            skipped_file_suffixes=skipped_file_suffixes,
        )
        result.skipped_paths.extend(skipped)

        release_inside_source = release == source or source in release.parents

        for source_path in files:
            if release_inside_source and (source_path == release or release in source_path.parents):
                continue

            relative_path = source_path.relative_to(source)
            target_path = release / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_path, target_path)

            size = target_path.stat().st_size
            result.total_size_bytes += size
            result.files_count += 1
            result.copied_items.append(
                ReleaseItem(
                    source_path=source_path,
                    target_path=target_path,
                    relative_path=relative_path,
                    size_bytes=size,
                )
            )

        result.directories_count = len({item.target_path.parent for item in result.copied_items})
        return result

    except OSError as error:
        result.errors.append({
            "code": "RELEASE_COPY_ERROR",
            "message": str(error),
            "context": {"exception_type": type(error).__name__},
        })
        return result


def build_release_package(
    source_dir: Path | str,
    release_dir: Path | str,
    *,
    skipped_directory_names: Iterable[str] = DEFAULT_SKIPPED_DIRECTORY_NAMES,
    skipped_file_suffixes: Iterable[str] = DEFAULT_SKIPPED_FILE_SUFFIXES,
) -> ReleaseResult:
    """Build a clean release package by copying allowed files to a destination directory."""
    return copy_release_files(
        source_dir,
        release_dir,
        clean=True,
        skipped_directory_names=skipped_directory_names,
        skipped_file_suffixes=skipped_file_suffixes,
    )
