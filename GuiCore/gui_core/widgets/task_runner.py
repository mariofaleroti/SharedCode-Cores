from __future__ import annotations

import queue
import threading
import time
import traceback
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .progress_panel import calculate_progress_value


TASK_STATE_IDLE = "idle"
TASK_STATE_RUNNING = "running"
TASK_STATE_CANCELLING = "cancelling"
TASK_STATE_COMPLETED = "completed"
TASK_STATE_FAILED = "failed"
TASK_STATE_CANCELLED = "cancelled"

VALID_TASK_STATES = {
    TASK_STATE_IDLE,
    TASK_STATE_RUNNING,
    TASK_STATE_CANCELLING,
    TASK_STATE_COMPLETED,
    TASK_STATE_FAILED,
    TASK_STATE_CANCELLED,
}
TERMINAL_TASK_STATES = {
    TASK_STATE_COMPLETED,
    TASK_STATE_FAILED,
    TASK_STATE_CANCELLED,
}
ACTIVE_TASK_STATES = {
    TASK_STATE_RUNNING,
    TASK_STATE_CANCELLING,
}


def normalize_task_state(value: str | None) -> str:
    normalized = str(value or TASK_STATE_IDLE).strip().lower()
    return normalized if normalized in VALID_TASK_STATES else TASK_STATE_IDLE


@dataclass(frozen=True)
class TaskProgress:
    """One progress update produced by a worker without touching Tk."""

    current: int | float = 0
    total: int | float = 0
    message: str = ""
    unit: str = "elementos"
    indeterminate: bool = False

    @property
    def fraction(self) -> float:
        if self.indeterminate:
            return 0.0
        return calculate_progress_value(self.current, self.total)

    @property
    def percent(self) -> int:
        return int(self.fraction * 100)

    def to_dict(self) -> dict[str, Any]:
        return {
            "current": self.current,
            "total": self.total,
            "message": str(self.message),
            "unit": str(self.unit),
            "indeterminate": bool(self.indeterminate),
            "fraction": self.fraction,
            "percent": self.percent,
        }


@dataclass(frozen=True)
class TaskError:
    """Controlled representation of an exception raised by a worker."""

    exception_type: str
    message: str
    traceback_text: str = ""

    def to_dict(self) -> dict[str, str]:
        return {
            "exception_type": str(self.exception_type),
            "message": str(self.message),
            "traceback": str(self.traceback_text),
        }


@dataclass(frozen=True)
class TaskResult:
    """Terminal result delivered on the GUI thread."""

    status: str
    value: Any = None
    error: TaskError | None = None

    @property
    def succeeded(self) -> bool:
        return self.status == TASK_STATE_COMPLETED

    @property
    def failed(self) -> bool:
        return self.status == TASK_STATE_FAILED

    @property
    def cancelled(self) -> bool:
        return self.status == TASK_STATE_CANCELLED

    def to_dict(self, *, include_value: bool = True) -> dict[str, Any]:
        data: dict[str, Any] = {
            "status": self.status,
            "succeeded": self.succeeded,
            "failed": self.failed,
            "cancelled": self.cancelled,
            "error": self.error.to_dict() if self.error is not None else None,
        }
        if include_value:
            data["value"] = self.value
        return data


class TaskCancelledError(RuntimeError):
    """Cooperative cancellation signal raised inside one worker."""


class CancellationToken:
    """Thread-safe cooperative cancellation token."""

    def __init__(self) -> None:
        self._event = threading.Event()

    @property
    def is_cancelled(self) -> bool:
        return self._event.is_set()

    def cancel(self) -> None:
        self._event.set()

    def throw_if_cancelled(self) -> None:
        if self.is_cancelled:
            raise TaskCancelledError("Task cancellation requested.")

    def wait(self, timeout: float | None = None) -> bool:
        return self._event.wait(timeout)


class TaskContext:
    """Worker-side API for progress, cancellation and responsive waits."""

    def __init__(
        self,
        cancellation_token: CancellationToken,
        progress_callback: Callable[[TaskProgress], None],
        *,
        min_progress_interval_seconds: float = 0.05,
    ) -> None:
        self.cancellation_token = cancellation_token
        self._progress_callback = progress_callback
        self.min_progress_interval_seconds = max(
            0.0,
            float(min_progress_interval_seconds),
        )
        self._last_progress_time = 0.0
        self._last_progress: TaskProgress | None = None

    @property
    def is_cancelled(self) -> bool:
        return self.cancellation_token.is_cancelled

    @property
    def last_progress(self) -> TaskProgress | None:
        return self._last_progress

    def check_cancelled(self) -> None:
        self.cancellation_token.throw_if_cancelled()

    def report_progress(
        self,
        current: int | float,
        total: int | float,
        *,
        message: str = "",
        unit: str = "elementos",
        force: bool = False,
    ) -> bool:
        self.check_cancelled()
        progress = TaskProgress(
            current=current,
            total=total,
            message=message,
            unit=unit,
            indeterminate=False,
        )
        return self._emit_progress(progress, force=force)

    def report_indeterminate(
        self,
        message: str = "Procesando...",
        *,
        force: bool = False,
    ) -> bool:
        self.check_cancelled()
        return self._emit_progress(
            TaskProgress(
                message=message,
                indeterminate=True,
            ),
            force=force,
        )

    def _emit_progress(
        self,
        progress: TaskProgress,
        *,
        force: bool,
    ) -> bool:
        now = time.monotonic()
        reached_end = (
            not progress.indeterminate
            and float(progress.total) > 0
            and float(progress.current) >= float(progress.total)
        )
        if (
            not force
            and not reached_end
            and self._last_progress_time > 0
            and now - self._last_progress_time
            < self.min_progress_interval_seconds
        ):
            self._last_progress = progress
            return False

        self._last_progress_time = now
        self._last_progress = progress
        self._progress_callback(progress)
        return True

    def sleep(
        self,
        seconds: float,
        *,
        check_interval_seconds: float = 0.05,
    ) -> None:
        remaining = max(0.0, float(seconds))
        interval = max(0.001, float(check_interval_seconds))
        end_time = time.monotonic() + remaining

        while True:
            self.check_cancelled()
            wait_time = min(interval, max(0.0, end_time - time.monotonic()))
            if wait_time <= 0:
                return
            if self.cancellation_token.wait(wait_time):
                self.check_cancelled()


def set_component_enabled(component: Any, enabled: bool) -> bool:
    """Enable/disable a wrapper or Tk widget without assuming its concrete type."""

    method = getattr(component, "set_enabled", None)
    if callable(method):
        method(bool(enabled))
        return True

    configure = getattr(component, "configure", None)
    if callable(configure):
        try:
            configure(state="normal" if enabled else "disabled")
            return True
        except Exception:
            pass

    for attribute in (
        "button",
        "entry",
        "combo",
        "switch",
        "checkbox",
    ):
        child = getattr(component, attribute, None)
        configure = getattr(child, "configure", None)
        if callable(configure):
            try:
                configure(state="normal" if enabled else "disabled")
                return True
            except Exception:
                continue
    return False


class GuiTaskRunner:
    """Run one cooperative worker and deliver every callback on the GUI thread."""

    def __init__(
        self,
        root: Any,
        *,
        poll_interval_ms: int = 40,
        progress_interval_seconds: float = 0.05,
    ) -> None:
        self.root = root
        self.poll_interval_ms = max(1, int(poll_interval_ms))
        self.progress_interval_seconds = max(
            0.0,
            float(progress_interval_seconds),
        )
        self.owner_thread_id = threading.get_ident()
        self.state = TASK_STATE_IDLE
        self.name = "task"
        self.result: TaskResult | None = None
        self.callback_errors: list[Exception] = []

        self._events: queue.Queue[tuple[str, Any]] = queue.Queue()
        self._thread: threading.Thread | None = None
        self._token: CancellationToken | None = None
        self._poll_after_id: str | None = None
        self._destroyed = False
        self._controls: tuple[Any, ...] = ()
        self._callbacks: dict[str, Callable[..., Any] | None] = {}

    @property
    def is_active(self) -> bool:
        return self.state in ACTIVE_TASK_STATES

    @property
    def is_running(self) -> bool:
        return self.state == TASK_STATE_RUNNING

    @property
    def thread(self) -> threading.Thread | None:
        return self._thread

    @property
    def cancellation_token(self) -> CancellationToken | None:
        return self._token

    def _assert_owner_thread(self) -> None:
        if threading.get_ident() != self.owner_thread_id:
            raise RuntimeError(
                "GuiTaskRunner.start must be called from its owner GUI thread."
            )

    def start(
        self,
        worker: Callable[[TaskContext], Any],
        *,
        name: str = "task",
        disable_while_running: Iterable[Any] = (),
        on_started: Callable[["GuiTaskRunner"], None] | None = None,
        on_state_change: Callable[[str], None] | None = None,
        on_progress: Callable[[TaskProgress], None] | None = None,
        on_success: Callable[[Any], None] | None = None,
        on_error: Callable[[TaskError], None] | None = None,
        on_cancelled: Callable[[TaskResult], None] | None = None,
        on_finished: Callable[[TaskResult], None] | None = None,
    ) -> "GuiTaskRunner":
        self._assert_owner_thread()
        if self._destroyed:
            raise RuntimeError("GuiTaskRunner has already been destroyed.")
        if self.is_active:
            raise RuntimeError("A task is already running in this runner.")
        if not callable(worker):
            raise TypeError("worker must be callable.")

        self.name = str(name or "task")
        self.result = None
        self.callback_errors.clear()
        self._events = queue.Queue()
        self._token = CancellationToken()
        self._controls = tuple(disable_while_running)
        self._callbacks = {
            "started": on_started,
            "state": on_state_change,
            "progress": on_progress,
            "success": on_success,
            "error": on_error,
            "cancelled": on_cancelled,
            "finished": on_finished,
        }

        self.state = TASK_STATE_RUNNING
        self._set_controls_enabled(False)
        self._safe_callback("state", self.state)
        self._safe_callback("started", self)

        token = self._token

        def worker_entry() -> None:
            context = TaskContext(
                token,
                lambda progress: self._events.put(("progress", progress)),
                min_progress_interval_seconds=self.progress_interval_seconds,
            )
            try:
                value = worker(context)
                if token.is_cancelled:
                    terminal = TaskResult(TASK_STATE_CANCELLED)
                else:
                    terminal = TaskResult(
                        TASK_STATE_COMPLETED,
                        value=value,
                    )
            except TaskCancelledError:
                terminal = TaskResult(TASK_STATE_CANCELLED)
            except Exception as error:
                task_error = TaskError(
                    exception_type=type(error).__name__,
                    message=str(error),
                    traceback_text=traceback.format_exc(),
                )
                terminal = TaskResult(
                    TASK_STATE_FAILED,
                    error=task_error,
                )
            self._events.put(("terminal", terminal))

        self._thread = threading.Thread(
            target=worker_entry,
            name=f"GuiTaskRunner-{self.name}",
            daemon=True,
        )
        self._thread.start()
        self._schedule_poll(0)
        return self

    def _safe_callback(self, key: str, *args: Any) -> None:
        callback = self._callbacks.get(key)
        if not callable(callback):
            return
        try:
            callback(*args)
        except Exception as error:
            self.callback_errors.append(error)

    def _schedule_poll(self, delay_ms: int | None = None) -> None:
        if self._destroyed or self._poll_after_id is not None:
            return
        try:
            self._poll_after_id = self.root.after(
                self.poll_interval_ms if delay_ms is None else max(0, int(delay_ms)),
                self._poll_events,
            )
        except Exception:
            self._poll_after_id = None
            self.destroy()

    def _poll_events(self) -> None:
        self._poll_after_id = None
        if self._destroyed:
            return

        latest_progress: TaskProgress | None = None
        terminal: TaskResult | None = None
        state_events: list[str] = []

        while True:
            try:
                event_type, payload = self._events.get_nowait()
            except queue.Empty:
                break

            if event_type == "progress":
                latest_progress = payload
            elif event_type == "state":
                state_events.append(str(payload))
            elif event_type == "terminal":
                terminal = payload

        for state in state_events:
            self._safe_callback("state", state)

        if latest_progress is not None:
            self._safe_callback("progress", latest_progress)

        if terminal is not None:
            self._finish(terminal)
            return

        thread_alive = self._thread is not None and self._thread.is_alive()
        if thread_alive or not self._events.empty():
            self._schedule_poll()

    def _finish(self, result: TaskResult) -> None:
        self.result = result
        self.state = normalize_task_state(result.status)
        self._set_controls_enabled(True)
        self._safe_callback("state", self.state)

        if result.succeeded:
            self._safe_callback("success", result.value)
        elif result.failed and result.error is not None:
            self._safe_callback("error", result.error)
        elif result.cancelled:
            self._safe_callback("cancelled", result)

        self._safe_callback("finished", result)

    def cancel(self) -> bool:
        if not self.is_active or self._token is None:
            return False
        if self.state != TASK_STATE_CANCELLING:
            self.state = TASK_STATE_CANCELLING
            self._events.put(("state", self.state))
        self._token.cancel()
        return True

    def _set_controls_enabled(self, enabled: bool) -> None:
        for component in self._controls:
            try:
                set_component_enabled(component, enabled)
            except Exception:
                pass

    def destroy(self) -> None:
        if self._destroyed:
            return
        self._destroyed = True
        if self._token is not None:
            self._token.cancel()
        if self._poll_after_id is not None:
            try:
                self.root.after_cancel(self._poll_after_id)
            except Exception:
                pass
            self._poll_after_id = None
        self._set_controls_enabled(True)
        if self.is_active:
            self.state = TASK_STATE_CANCELLED
            self.result = TaskResult(TASK_STATE_CANCELLED)
        self._callbacks.clear()
