from __future__ import annotations

import threading
import time
import unittest

from file_scan_core import (
    DEFAULT_MAX_WORKERS,
    DEFAULT_QUEUE_CAPACITY,
    WorkerPoolStats,
    iter_bounded_workers,
    process_with_bounded_workers,
)


class BoundedWorkerPoolTests(unittest.TestCase):
    def test_public_defaults_match_current_scan_design(self) -> None:
        self.assertEqual(DEFAULT_MAX_WORKERS, 4)
        self.assertEqual(DEFAULT_QUEUE_CAPACITY, 40)

    def test_multiple_workers_process_items_concurrently(self) -> None:
        active_count = 0
        peak_active_count = 0
        counter_lock = threading.Lock()

        def worker(item: int) -> int:
            nonlocal active_count, peak_active_count
            with counter_lock:
                active_count += 1
                peak_active_count = max(peak_active_count, active_count)
            time.sleep(0.025)
            with counter_lock:
                active_count -= 1
            return item * 2

        result = process_with_bounded_workers(
            range(12),
            worker,
            max_workers=4,
            queue_capacity=4,
            preserve_input_order=True,
        )

        self.assertGreaterEqual(peak_active_count, 2)
        self.assertLessEqual(peak_active_count, 4)
        self.assertEqual(
            [task.value for task in result.results],
            [item * 2 for item in range(12)],
        )
        self.assertEqual(result.stats.completed_count, 12)
        self.assertEqual(result.stats.failed_count, 0)

    def test_producer_pauses_when_workers_and_queue_are_full(self) -> None:
        release_workers = threading.Event()
        produced_items: list[int] = []
        results: list[object] = []

        def source():
            for item in range(30):
                produced_items.append(item)
                yield item

        def worker(item: int) -> int:
            release_workers.wait(timeout=2)
            return item

        consumer = threading.Thread(
            target=lambda: results.extend(
                iter_bounded_workers(
                    source(),
                    worker,
                    max_workers=2,
                    queue_capacity=3,
                )
            ),
            daemon=True,
        )
        consumer.start()

        deadline = time.monotonic() + 2
        while len(produced_items) < 5 and time.monotonic() < deadline:
            time.sleep(0.005)

        time.sleep(0.03)
        self.assertEqual(len(produced_items), 5)

        release_workers.set()
        consumer.join(timeout=3)

        self.assertFalse(consumer.is_alive())
        self.assertEqual(len(results), 30)

    def test_worker_failure_is_isolated_and_structured(self) -> None:
        def worker(item: int) -> int:
            if item == 2:
                raise RuntimeError("broken candidate")
            return item + 10

        result = process_with_bounded_workers(
            range(5),
            worker,
            max_workers=2,
            queue_capacity=2,
            preserve_input_order=True,
        )

        self.assertEqual(result.stats.succeeded_count, 4)
        self.assertEqual(result.stats.failed_count, 1)
        self.assertEqual(len(result.failed_results), 1)
        self.assertEqual(result.failed_results[0].item, 2)
        self.assertEqual(result.failed_results[0].error_type, "RuntimeError")
        self.assertEqual(result.failed_results[0].error_message, "broken candidate")

    def test_input_order_can_be_preserved(self) -> None:
        def worker(item: int) -> int:
            time.sleep((5 - item) * 0.005)
            return item

        completion_order = process_with_bounded_workers(
            range(6),
            worker,
            max_workers=3,
            queue_capacity=3,
            preserve_input_order=False,
        )
        input_order = process_with_bounded_workers(
            range(6),
            worker,
            max_workers=3,
            queue_capacity=3,
            preserve_input_order=True,
        )

        self.assertNotEqual(
            [task.sequence for task in completion_order.results],
            list(range(6)),
        )
        self.assertEqual(
            [task.sequence for task in input_order.results],
            list(range(6)),
        )

    def test_stats_and_progress_events_are_updated_on_producer_thread(self) -> None:
        stats = WorkerPoolStats()
        events: list[dict[str, object]] = []

        results = list(
            iter_bounded_workers(
                range(4),
                lambda item: item,
                max_workers=2,
                queue_capacity=1,
                preserve_input_order=True,
                stats=stats,
                progress_callback=lambda event: events.append(dict(event)),
            )
        )

        self.assertEqual(len(results), 4)
        self.assertEqual(stats.submitted_count, 4)
        self.assertEqual(stats.completed_count, 4)
        self.assertEqual(stats.peak_in_flight_count, 3)
        self.assertLessEqual(stats.peak_queued_count, 1)
        self.assertTrue(stats.source_exhausted)
        self.assertEqual(events[-1]["completed"], 4)
        self.assertEqual(events[-1]["stage"], "processing")
        self.assertEqual(events[-1]["event"], "completed")
        self.assertEqual(events[-1]["active"], 0)
        self.assertEqual(events[-1]["queued"], 0)
        self.assertTrue(any(event.get("event") == "submitted" for event in events))
        self.assertTrue(any(int(event.get("active", 0)) > 0 for event in events))

    def test_cancellation_stops_source_and_marks_stats(self) -> None:
        cancel_event = threading.Event()
        stats = WorkerPoolStats()
        events: list[dict[str, object]] = []

        def source():
            for item in range(100):
                if item == 6:
                    cancel_event.set()
                yield item

        started_at = time.monotonic()
        results = list(
            iter_bounded_workers(
                source(),
                lambda item: (time.sleep(0.15), item)[1],
                max_workers=2,
                queue_capacity=4,
                cancel_requested=cancel_event.is_set,
                progress_callback=lambda event: events.append(dict(event)),
                stats=stats,
            )
        )
        elapsed = time.monotonic() - started_at

        self.assertLess(elapsed, 0.5)
        self.assertTrue(stats.cancellation_requested)
        self.assertFalse(stats.source_exhausted)
        self.assertLess(stats.submitted_count, 100)
        self.assertLessEqual(len(results), stats.completed_count)
        self.assertTrue(any(event.get("event") == "cancelled" for event in events))

    def test_invalid_limits_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            list(iter_bounded_workers([], lambda item: item, max_workers=0))

        with self.assertRaises(ValueError):
            list(iter_bounded_workers([], lambda item: item, queue_capacity=-1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
