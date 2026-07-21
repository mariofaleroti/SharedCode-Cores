"""
Shared result models for FileScanCore.

DESIGN:
Models in this module describe scan and worker-pipeline output only.
They must not contain tool-specific behavior or filesystem actions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Generic, TypeVar


TItem = TypeVar("TItem")
TResult = TypeVar("TResult")


@dataclass(slots=True)
class WorkerPoolStats:
    """Mutable counters collected by a bounded worker pipeline."""

    max_workers: int = 0
    queue_capacity: int = 0
    submitted_count: int = 0
    completed_count: int = 0
    succeeded_count: int = 0
    failed_count: int = 0
    cancelled_count: int = 0
    cancellation_requested: bool = False
    peak_in_flight_count: int = 0
    peak_queued_count: int = 0
    elapsed_seconds: float = 0.0
    source_exhausted: bool = False

    def reset(self, *, max_workers: int, queue_capacity: int) -> None:
        """Resets counters so a stats instance can be reused safely."""

        self.max_workers = max_workers
        self.queue_capacity = queue_capacity
        self.submitted_count = 0
        self.completed_count = 0
        self.succeeded_count = 0
        self.failed_count = 0
        self.cancelled_count = 0
        self.cancellation_requested = False
        self.peak_in_flight_count = 0
        self.peak_queued_count = 0
        self.elapsed_seconds = 0.0
        self.source_exhausted = False


@dataclass(slots=True, frozen=True)
class WorkerTaskResult(Generic[TItem, TResult]):
    """Structured outcome for one item processed by a worker."""

    sequence: int
    item: TItem
    succeeded: bool
    value: TResult | None = None
    error_type: str | None = None
    error_message: str = ""
    elapsed_seconds: float = 0.0


@dataclass(slots=True)
class WorkerPoolResult(Generic[TItem, TResult]):
    """Collected result returned by a bounded worker pipeline."""

    results: list[WorkerTaskResult[TItem, TResult]] = field(default_factory=list)
    stats: WorkerPoolStats = field(default_factory=WorkerPoolStats)

    @property
    def succeeded_results(self) -> list[WorkerTaskResult[TItem, TResult]]:
        """Returns successful task results."""

        return [result for result in self.results if result.succeeded]

    @property
    def failed_results(self) -> list[WorkerTaskResult[TItem, TResult]]:
        """Returns failed task results."""

        return [result for result in self.results if not result.succeeded]


@dataclass(slots=True, frozen=True)
class ScanError:
    """Represents a non-fatal filesystem scan error."""

    path: Path
    error_type: str
    message: str
    exception_type: str | None = None
    stage: str = "scan"

    def to_dict(self) -> dict[str, str | None]:
        """Returns a JSON-safe diagnostic representation."""

        return {
            "path": str(self.path),
            "error_type": self.error_type,
            "message": self.message,
            "exception_type": self.exception_type,
            "stage": self.stage,
        }


@dataclass(slots=True)
class DirectoryWalkStats:
    """Mutable counters collected during a directory walk."""

    scanned_count: int = 0
    skipped_count: int = 0
    policy_skipped_count: int = 0
    link_or_reparse_skipped_count: int = 0
    name_skipped_count: int = 0
    keyword_skipped_count: int = 0
    revisited_skipped_count: int = 0


@dataclass(slots=True)
class DirectoryWalkResult:
    """Collected result returned by a directory walk operation."""

    root_path: Path
    directories: list[Path] = field(default_factory=list)
    errors: list[ScanError] = field(default_factory=list)
    scanned_count: int = 0
    skipped_count: int = 0
    policy_skipped_count: int = 0
    link_or_reparse_skipped_count: int = 0
    name_skipped_count: int = 0
    keyword_skipped_count: int = 0
    revisited_skipped_count: int = 0


@dataclass(slots=True, frozen=True)
class MarkerMatch:
    """
    Represents a directory that contains a marker.

    NOTE:
    The marker meaning belongs to the consuming tool.
    FileScanCore only reports that the marker exists.
    """

    root_path: Path
    directory_path: Path
    marker_path: Path
    marker_name: str
    depth: int


@dataclass(slots=True)
class MarkerScanResult:
    """Collected result returned by marker scanning."""

    marker_name: str
    root_paths: list[Path] = field(default_factory=list)
    matches: list[MarkerMatch] = field(default_factory=list)
    errors: list[ScanError] = field(default_factory=list)
    scanned_count: int = 0
    skipped_count: int = 0
    policy_skipped_count: int = 0
    link_or_reparse_skipped_count: int = 0
    name_skipped_count: int = 0
    keyword_skipped_count: int = 0
    revisited_skipped_count: int = 0

    @property
    def has_matches(self) -> bool:
        """Returns True when at least one marker match was found."""

        return bool(self.matches)
