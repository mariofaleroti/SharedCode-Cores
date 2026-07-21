"""
FileScanCore provides safe filesystem scanning utilities for external tools.

DESIGN:
This package must remain tool-agnostic.
It does not know about ShadowBackup, Smart Filter, Toolkit or any consumer.
"""

from .errors import build_scan_error, build_validation_error
from .exclusion_policy import (
    DirectoryExclusionMatch,
    DirectoryExclusionPolicy,
    DirectoryExclusionRule,
)
from .filters import DEFAULT_SKIPPED_DIRECTORY_NAMES
from .markers import (
    directory_contains_marker,
    find_marker_directories,
    validate_marker_name,
)
from .models import (
    DirectoryWalkResult,
    DirectoryWalkStats,
    MarkerMatch,
    MarkerScanResult,
    ScanError,
    WorkerPoolResult,
    WorkerPoolStats,
    WorkerTaskResult,
)
from .walker import iter_safe_directories, walk_directories
from .worker_pool import (
    DEFAULT_MAX_WORKERS,
    DEFAULT_QUEUE_CAPACITY,
    iter_bounded_workers,
    process_with_bounded_workers,
)

__all__ = [
    "DEFAULT_MAX_WORKERS",
    "DEFAULT_QUEUE_CAPACITY",
    "DEFAULT_SKIPPED_DIRECTORY_NAMES",
    "DirectoryExclusionMatch",
    "DirectoryExclusionPolicy",
    "DirectoryExclusionRule",
    "DirectoryWalkResult",
    "DirectoryWalkStats",
    "MarkerMatch",
    "MarkerScanResult",
    "ScanError",
    "WorkerPoolResult",
    "WorkerPoolStats",
    "WorkerTaskResult",
    "build_scan_error",
    "build_validation_error",
    "directory_contains_marker",
    "find_marker_directories",
    "iter_bounded_workers",
    "validate_marker_name",
    "iter_safe_directories",
    "walk_directories",
    "process_with_bounded_workers",
]
