"""
Bounded concurrent worker utilities for filesystem consumers.

DESIGN:
FileScanCore coordinates a producer-consumer flow without knowing how files are
interpreted. The consuming tool supplies an iterable of candidates and a worker
function. The iterable can keep scanning while a fixed group of threads handles
previous candidates.

WARNING:
The worker must return data instead of mutating shared counters or lists. Results
are aggregated by the caller on the producer thread to avoid race conditions.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Mapping
from concurrent.futures import FIRST_COMPLETED, Future, ThreadPoolExecutor, wait
from time import perf_counter
from typing import TypeVar

from .models import WorkerPoolResult, WorkerPoolStats, WorkerTaskResult

TItem = TypeVar("TItem")
TResult = TypeVar("TResult")

WorkerCallable = Callable[[TItem], TResult]
WorkerProgressCallback = Callable[[Mapping[str, object]], None]
CancelRequestedCallback = Callable[[], bool]

DEFAULT_MAX_WORKERS = 4
DEFAULT_QUEUE_CAPACITY = 40
DEFAULT_THREAD_NAME_PREFIX = "filescan-worker"


def _validate_limits(max_workers: int, queue_capacity: int) -> None:
    """Validates bounded worker pool limits."""

    if max_workers < 1:
        raise ValueError("max_workers must be at least 1.")
    if queue_capacity < 0:
        raise ValueError("queue_capacity cannot be negative.")


def _execute_worker(
    sequence: int,
    item: TItem,
    worker: WorkerCallable[TItem, TResult],
) -> WorkerTaskResult[TItem, TResult]:
    """Runs one worker call and converts failures into a structured result."""

    started_at = perf_counter()

    try:
        value = worker(item)
    except Exception as error:  # noqa: BLE001 - task isolation is intentional.
        return WorkerTaskResult(
            sequence=sequence,
            item=item,
            succeeded=False,
            value=None,
            error_type=type(error).__name__,
            error_message=str(error),
            elapsed_seconds=perf_counter() - started_at,
        )

    return WorkerTaskResult(
        sequence=sequence,
        item=item,
        succeeded=True,
        value=value,
        elapsed_seconds=perf_counter() - started_at,
    )


def _emit_progress(
    callback: WorkerProgressCallback | None,
    stats: WorkerPoolStats,
    *,
    event: str,
) -> None:
    """Emits a stable progress event from the producer thread."""

    if callback is None:
        return

    in_flight_count = max(0, stats.submitted_count - stats.completed_count - stats.cancelled_count)
    queued_count = max(0, in_flight_count - stats.max_workers)
    active_count = max(0, in_flight_count - queued_count)
    callback(
        {
            "stage": "processing",
            "event": event,
            "submitted": stats.submitted_count,
            "completed": stats.completed_count,
            "succeeded": stats.succeeded_count,
            "failed": stats.failed_count,
            "cancelled": stats.cancelled_count,
            "cancellation_requested": stats.cancellation_requested,
            "in_flight": in_flight_count,
            "active": active_count,
            "queued": queued_count,
            "max_workers": stats.max_workers,
            "queue_capacity": stats.queue_capacity,
        }
    )


def _is_cancel_requested(callback: CancelRequestedCallback | None) -> bool:
    if callback is None:
        return False
    try:
        return bool(callback())
    except Exception:
        # Cancellation is advisory. A faulty callback must not crash the scan.
        return False


def iter_bounded_workers(
    items: Iterable[TItem],
    worker: WorkerCallable[TItem, TResult],
    *,
    max_workers: int = DEFAULT_MAX_WORKERS,
    queue_capacity: int = DEFAULT_QUEUE_CAPACITY,
    preserve_input_order: bool = False,
    progress_callback: WorkerProgressCallback | None = None,
    cancel_requested: CancelRequestedCallback | None = None,
    stats: WorkerPoolStats | None = None,
    thread_name_prefix: str = DEFAULT_THREAD_NAME_PREFIX,
) -> Iterator[WorkerTaskResult[TItem, TResult]]:
    """
    Processes items with a fixed thread pool and bounded pending work.

    The caller's thread remains the producer. It keeps consuming ``items`` while
    workers are available or the waiting queue has free capacity. Once the bound
    is reached, production pauses until at least one task finishes.

    ``queue_capacity`` counts waiting tasks only. Therefore the maximum number of
    submitted but unfinished tasks is ``max_workers + queue_capacity``.

    ``cancel_requested`` is optional and intentionally generic. Once it returns
    true, FileScanCore stops consuming the source, cancels tasks that have not
    started, and returns without waiting for active workers. Active calls finish
    naturally in the background and their results are discarded by the caller.
    """

    _validate_limits(max_workers=max_workers, queue_capacity=queue_capacity)

    effective_stats = stats or WorkerPoolStats()
    effective_stats.reset(
        max_workers=max_workers,
        queue_capacity=queue_capacity,
    )

    max_in_flight = max_workers + queue_capacity
    item_iterator = iter(items)
    pending: dict[Future[WorkerTaskResult[TItem, TResult]], int] = {}
    ordered_buffer: dict[int, WorkerTaskResult[TItem, TResult]] = {}
    next_sequence_to_yield = 0
    next_sequence_to_submit = 0
    source_exhausted = False
    cancellation_requested = False
    pipeline_started_at = perf_counter()
    executor = ThreadPoolExecutor(
        max_workers=max_workers,
        thread_name_prefix=thread_name_prefix,
    )

    try:
        while pending or not source_exhausted:
            if _is_cancel_requested(cancel_requested):
                cancellation_requested = True
                effective_stats.cancellation_requested = True
                source_exhausted = True
                for future in tuple(pending):
                    if future.cancel():
                        effective_stats.cancelled_count += 1
                        pending.pop(future, None)
                _emit_progress(progress_callback, effective_stats, event="cancelled")
                break

            while not source_exhausted and len(pending) < max_in_flight:
                if _is_cancel_requested(cancel_requested):
                    cancellation_requested = True
                    effective_stats.cancellation_requested = True
                    source_exhausted = True
                    break

                try:
                    item = next(item_iterator)
                except StopIteration:
                    source_exhausted = True
                    break

                sequence = next_sequence_to_submit
                next_sequence_to_submit += 1
                future = executor.submit(_execute_worker, sequence, item, worker)
                pending[future] = sequence

                effective_stats.submitted_count += 1
                effective_stats.peak_in_flight_count = max(
                    effective_stats.peak_in_flight_count,
                    len(pending),
                )
                effective_stats.peak_queued_count = max(
                    effective_stats.peak_queued_count,
                    max(0, len(pending) - max_workers),
                )
                _emit_progress(progress_callback, effective_stats, event="submitted")

            if cancellation_requested:
                for future in tuple(pending):
                    if future.cancel():
                        effective_stats.cancelled_count += 1
                        pending.pop(future, None)
                _emit_progress(progress_callback, effective_stats, event="cancelled")
                break
            if not pending:
                continue

            completed_futures, _not_done = wait(
                pending,
                timeout=0.10 if cancel_requested is not None else None,
                return_when=FIRST_COMPLETED,
            )
            if not completed_futures:
                continue

            # Sorting this completion batch by sequence makes behavior more
            # deterministic without forcing global input-order blocking.
            completed_results = sorted(
                (future.result() for future in completed_futures),
                key=lambda result: result.sequence,
            )

            for future in completed_futures:
                pending.pop(future, None)

            for result in completed_results:
                effective_stats.completed_count += 1
                if result.succeeded:
                    effective_stats.succeeded_count += 1
                else:
                    effective_stats.failed_count += 1

                _emit_progress(progress_callback, effective_stats, event="completed")

                if preserve_input_order:
                    ordered_buffer[result.sequence] = result
                    while next_sequence_to_yield in ordered_buffer:
                        yield ordered_buffer.pop(next_sequence_to_yield)
                        next_sequence_to_yield += 1
                else:
                    yield result
    finally:
        if cancellation_requested:
            for future in tuple(pending):
                if future.cancel():
                    effective_stats.cancelled_count += 1
            executor.shutdown(wait=False, cancel_futures=True)
        else:
            executor.shutdown(wait=True, cancel_futures=False)
        effective_stats.elapsed_seconds = perf_counter() - pipeline_started_at
        effective_stats.source_exhausted = source_exhausted and not cancellation_requested


def process_with_bounded_workers(
    items: Iterable[TItem],
    worker: WorkerCallable[TItem, TResult],
    *,
    max_workers: int = DEFAULT_MAX_WORKERS,
    queue_capacity: int = DEFAULT_QUEUE_CAPACITY,
    preserve_input_order: bool = False,
    progress_callback: WorkerProgressCallback | None = None,
    cancel_requested: CancelRequestedCallback | None = None,
    thread_name_prefix: str = DEFAULT_THREAD_NAME_PREFIX,
) -> WorkerPoolResult[TItem, TResult]:
    """Collects all structured results from ``iter_bounded_workers``."""

    stats = WorkerPoolStats()
    results = list(
        iter_bounded_workers(
            items=items,
            worker=worker,
            max_workers=max_workers,
            queue_capacity=queue_capacity,
            preserve_input_order=preserve_input_order,
            progress_callback=progress_callback,
            cancel_requested=cancel_requested,
            stats=stats,
            thread_name_prefix=thread_name_prefix,
        )
    )

    return WorkerPoolResult(results=results, stats=stats)
