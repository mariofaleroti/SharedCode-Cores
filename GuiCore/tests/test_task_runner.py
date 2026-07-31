from __future__ import annotations

import threading
import time
import unittest

from gui_core import (
    TASK_STATE_CANCELLED,
    TASK_STATE_COMPLETED,
    TASK_STATE_FAILED,
    TASK_STATE_RUNNING,
    CancellationToken,
    GuiTaskRunner,
    TaskCancelledError,
    TaskContext,
    TaskError,
    TaskProgress,
    TaskResult,
    normalize_task_state,
    set_component_enabled,
)


class FakeTkRoot:
    def __init__(self) -> None:
        self.owner_thread_id = threading.get_ident()
        self.after_thread_ids = []
        self._callbacks = {}
        self._order = []
        self._counter = 0

    def after(self, _delay_ms, callback):
        self.after_thread_ids.append(threading.get_ident())
        self._counter += 1
        callback_id = f"after-{self._counter}"
        self._callbacks[callback_id] = callback
        self._order.append(callback_id)
        return callback_id

    def after_cancel(self, callback_id):
        self._callbacks.pop(callback_id, None)
        if callback_id in self._order:
            self._order.remove(callback_id)

    def run_pending(self, limit=100):
        count = 0
        while self._order and count < limit:
            callback_id = self._order.pop(0)
            callback = self._callbacks.pop(callback_id, None)
            if callback is not None:
                callback()
            count += 1
        return count


class FakeControl:
    def __init__(self) -> None:
        self.states = []

    def set_enabled(self, enabled):
        self.states.append(bool(enabled))


class TaskRunnerTests(unittest.TestCase):
    def pump(self, root, runner, timeout=2.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            root.run_pending()
            if not runner.is_active and not root._order:
                return
            time.sleep(0.002)
        self.fail(f"Task did not finish. state={runner.state}")

    def test_progress_and_result_contracts(self):
        progress = TaskProgress(3, 4, "Procesando", "archivos")
        self.assertEqual(progress.fraction, 0.75)
        self.assertEqual(progress.percent, 75)
        self.assertEqual(progress.to_dict()["unit"], "archivos")

        result = TaskResult(TASK_STATE_COMPLETED, value={"ok": True})
        self.assertTrue(result.succeeded)
        self.assertFalse(result.failed)
        self.assertEqual(result.to_dict()["value"], {"ok": True})
        self.assertEqual(normalize_task_state("UNKNOWN"), "idle")

    def test_cancellation_token_and_context_sleep_are_cooperative(self):
        token = CancellationToken()
        context = TaskContext(token, lambda _progress: None)
        token.cancel()
        self.assertTrue(token.is_cancelled)
        with self.assertRaises(TaskCancelledError):
            context.check_cancelled()

    def test_success_callbacks_run_only_on_owner_thread(self):
        root = FakeTkRoot()
        runner = GuiTaskRunner(root, poll_interval_ms=1)
        owner_thread = threading.get_ident()
        worker_threads = []
        callback_threads = []
        values = []
        progress_updates = []

        def worker(context):
            worker_threads.append(threading.get_ident())
            context.report_progress(1, 2, message="Mitad", force=True)
            context.report_progress(2, 2, message="Completo")
            return 42

        runner.start(
            worker,
            on_started=lambda _runner: callback_threads.append(threading.get_ident()),
            on_progress=lambda value: (
                callback_threads.append(threading.get_ident()),
                progress_updates.append(value),
            ),
            on_success=lambda value: (
                callback_threads.append(threading.get_ident()),
                values.append(value),
            ),
            on_finished=lambda _result: callback_threads.append(threading.get_ident()),
        )
        self.pump(root, runner)

        self.assertEqual(runner.state, TASK_STATE_COMPLETED)
        self.assertEqual(values, [42])
        self.assertTrue(progress_updates)
        self.assertNotEqual(worker_threads[0], owner_thread)
        self.assertTrue(all(item == owner_thread for item in callback_threads))
        self.assertTrue(all(item == owner_thread for item in root.after_thread_ids))

    def test_error_is_controlled_and_controls_are_restored(self):
        root = FakeTkRoot()
        control = FakeControl()
        runner = GuiTaskRunner(root, poll_interval_ms=1)
        errors = []

        def worker(_context):
            raise ValueError("invalid input")

        runner.start(
            worker,
            disable_while_running=(control,),
            on_error=errors.append,
        )
        self.pump(root, runner)

        self.assertEqual(runner.state, TASK_STATE_FAILED)
        self.assertEqual(control.states, [False, True])
        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], TaskError)
        self.assertEqual(errors[0].exception_type, "ValueError")
        self.assertIn("invalid input", errors[0].message)
        self.assertIn("ValueError", errors[0].traceback_text)

    def test_cancel_changes_terminal_state(self):
        root = FakeTkRoot()
        runner = GuiTaskRunner(root, poll_interval_ms=1)
        cancelled = []

        def worker(context):
            while True:
                context.sleep(0.01, check_interval_seconds=0.002)

        runner.start(worker, on_cancelled=cancelled.append)
        self.assertTrue(runner.cancel())
        self.pump(root, runner)

        self.assertEqual(runner.state, TASK_STATE_CANCELLED)
        self.assertEqual(len(cancelled), 1)
        self.assertTrue(cancelled[0].cancelled)
        self.assertFalse(runner.cancel())

    def test_duplicate_start_is_rejected(self):
        root = FakeTkRoot()
        runner = GuiTaskRunner(root, poll_interval_ms=1)
        release = threading.Event()

        def worker(context):
            while not release.is_set():
                context.check_cancelled()
                time.sleep(0.002)

        runner.start(worker)
        with self.assertRaises(RuntimeError):
            runner.start(worker)
        release.set()
        self.pump(root, runner)

    def test_progress_is_throttled_and_latest_value_reaches_gui(self):
        root = FakeTkRoot()
        runner = GuiTaskRunner(
            root,
            poll_interval_ms=1,
            progress_interval_seconds=10.0,
        )
        updates = []

        def worker(context):
            for index in range(1, 501):
                context.report_progress(index, 500)

        runner.start(worker, on_progress=updates.append)
        self.pump(root, runner)

        self.assertLess(len(updates), 20)
        self.assertEqual(updates[-1].current, 500)

    def test_destroy_during_task_cancels_poll_and_restores_controls(self):
        root = FakeTkRoot()
        control = FakeControl()
        runner = GuiTaskRunner(root, poll_interval_ms=1)

        def worker(context):
            context.sleep(1.0)

        runner.start(worker, disable_while_running=(control,))
        runner.destroy()
        root.run_pending()

        self.assertEqual(runner.state, TASK_STATE_CANCELLED)
        self.assertEqual(control.states, [False, True])
        self.assertFalse(root._order)

    def test_set_component_enabled_supports_generic_widgets(self):
        control = FakeControl()
        self.assertTrue(set_component_enabled(control, False))
        self.assertEqual(control.states, [False])


if __name__ == "__main__":
    unittest.main()
