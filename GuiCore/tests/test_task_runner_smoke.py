from __future__ import annotations

import time
import unittest

from tk_test_utils import destroy_tk_root

from gui_core import (
    TASK_STATE_CANCELLED,
    TASK_STATE_COMPLETED,
    GuiAppConfig,
    GuiAppWindow,
    require_customtkinter,
)


class TaskRunnerSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        probe = None
        try:
            ctk = require_customtkinter()
            probe = ctk.CTk()
            probe.withdraw()
            probe.update_idletasks()
        except Exception as error:
            raise unittest.SkipTest(
                f"A graphical CustomTkinter environment is not available: {error}"
            ) from error
        finally:
            destroy_tk_root(probe)

    def pump(self, app, runner, timeout=3.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            app.root.update()
            if not runner.is_active:
                app.root.update_idletasks()
                return
            time.sleep(0.005)
        self.fail(f"Task did not finish. state={runner.state}")

    def test_app_task_updates_progress_and_completes(self) -> None:
        app = GuiAppWindow(
            GuiAppConfig(
                app_name="Task Smoke",
                maximize_on_start=False,
            )
        )
        values = []

        def worker(context):
            for index in range(1, 4):
                context.report_progress(
                    index,
                    3,
                    message=f"Paso {index}",
                    force=True,
                )
                context.sleep(0.01)
            return "done"

        runner = app.start_task(
            worker,
            task_key="progress",
            name="progress",
            start_message="Iniciando",
            success_message="Completado",
            on_success=values.append,
        )
        self.pump(app, runner)

        self.assertEqual(runner.state, TASK_STATE_COMPLETED)
        self.assertEqual(values, ["done"])
        self.assertEqual(app.progress_panel.label.cget("text"), "Completado")
        self.assertFalse(app.progress_panel.cancel_button.winfo_ismapped())
        app.destroy()

    def test_cancel_button_requests_cooperative_cancellation(self) -> None:
        app = GuiAppWindow(
            GuiAppConfig(
                app_name="Cancel Smoke",
                maximize_on_start=False,
            )
        )

        def worker(context):
            for index in range(100):
                context.report_progress(index, 100, force=True)
                context.sleep(0.02)

        runner = app.start_task(
            worker,
            task_key="cancel",
            name="cancel",
            cancellable=True,
        )
        app.root.update()
        self.assertTrue(app.progress_panel.cancel_button.winfo_ismapped())
        app.progress_panel.cancel_button.invoke()
        self.pump(app, runner)

        self.assertEqual(runner.state, TASK_STATE_CANCELLED)
        self.assertEqual(
            app.progress_panel.label.cget("text"),
            "Operación cancelada",
        )
        app.destroy()

    def test_duplicate_task_key_is_rejected(self) -> None:
        app = GuiAppWindow(
            GuiAppConfig(
                app_name="Duplicate Smoke",
                maximize_on_start=False,
            )
        )

        def worker(context):
            context.sleep(0.2)

        runner = app.start_task(worker, task_key="same")
        with self.assertRaises(RuntimeError):
            app.start_task(worker, task_key="same")
        runner.cancel()
        self.pump(app, runner)
        app.destroy()

    def test_destroy_window_while_task_runs_is_safe(self) -> None:
        app = GuiAppWindow(
            GuiAppConfig(
                app_name="Destroy Smoke",
                maximize_on_start=False,
            )
        )

        def worker(context):
            context.sleep(1.0)

        runner = app.start_task(worker, task_key="destroy")
        app.destroy()
        self.assertEqual(runner.state, TASK_STATE_CANCELLED)


if __name__ == "__main__":
    unittest.main()
