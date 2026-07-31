from __future__ import annotations

from typing import Any


def widget_exists(widget: Any) -> bool:
    """Return whether a Tk widget still exists without raising Tcl errors."""

    if widget is None:
        return False
    try:
        return bool(widget.winfo_exists())
    except Exception:
        return False


def iter_widget_tree(widget: Any) -> tuple[Any, ...]:
    """Return one Tk widget and every currently reachable descendant."""

    if widget is None:
        return ()

    collected: list[Any] = []
    pending = [widget]
    seen: set[int] = set()

    while pending:
        current = pending.pop(0)
        identity = id(current)
        if identity in seen:
            continue
        seen.add(identity)
        collected.append(current)

        try:
            children = list(current.winfo_children())
        except Exception:
            children = []
        pending.extend(children)

    return tuple(collected)


def _pending_after_ids(widget: Any) -> tuple[str, ...]:
    try:
        pending = widget.tk.call("after", "info")
    except Exception:
        return ()

    if isinstance(pending, str):
        if not pending:
            return ()
        try:
            return tuple(widget.tk.splitlist(pending))
        except Exception:
            return (pending,)

    try:
        return tuple(str(value) for value in pending)
    except TypeError:
        return ()


def _after_command_name(widget: Any, callback_id: str) -> str | None:
    try:
        data = widget.tk.call("after", "info", callback_id)
        parts = widget.tk.splitlist(data)
    except Exception:
        return None

    if not parts:
        return None
    return str(parts[0])


def _registered_commands(widget: Any) -> tuple[str, ...]:
    commands = getattr(widget, "_tclCommands", None)
    if not commands:
        return ()
    try:
        return tuple(str(command) for command in commands)
    except TypeError:
        return ()


def cancel_widget_after_callbacks(widget: Any) -> int:
    """Cancel pending ``after`` callbacks owned by one widget subtree.

    Tk keeps one global callback queue per interpreter, but each Python command
    belongs to the widget that registered it. Calling ``after_cancel`` from a
    different widget deletes the Tcl command globally without removing it from
    the real owner's ``_tclCommands`` list. Python 3.13 then attempts to delete
    that stale command again during widget destruction and raises:

        _tkinter.TclError: can't delete Tcl command

    This helper maps every pending callback back to its real owner before
    cancelling it. Callbacks outside the supplied subtree remain untouched.
    """

    if not widget_exists(widget):
        return 0

    cancelled = 0

    # A callback can schedule another callback while the queue is being
    # inspected. A few bounded passes keep teardown deterministic.
    for _ in range(6):
        tree = iter_widget_tree(widget)
        command_owners: dict[str, Any] = {}

        for owner in tree:
            for command_name in _registered_commands(owner):
                command_owners[command_name] = owner

        owned_callbacks: list[tuple[Any, str]] = []
        for callback_id in _pending_after_ids(widget):
            command_name = _after_command_name(widget, callback_id)
            if command_name is None:
                continue
            owner = command_owners.get(command_name)
            if owner is not None:
                owned_callbacks.append((owner, callback_id))

        if not owned_callbacks:
            break

        pass_cancelled = 0
        for owner, callback_id in owned_callbacks:
            try:
                owner.after_cancel(callback_id)
            except Exception:
                # Never delete an unknown Tcl command manually here. Leaving
                # the owner's command registered is safer than creating a
                # stale entry that fails during destroy().
                try:
                    owner.tk.call("after", "cancel", callback_id)
                except Exception:
                    continue
            pass_cancelled += 1

        cancelled += pass_cancelled
        if pass_cancelled == 0:
            break

    return cancelled


def destroy_widget_tree(
    widget: Any,
    *,
    release_grab: bool = False,
    quit_mainloop: bool = False,
) -> None:
    """Safely destroy a Tk root or toplevel and its descendant callbacks."""

    if not widget_exists(widget):
        return

    if release_grab:
        try:
            widget.grab_release()
        except Exception:
            pass

    cancel_widget_after_callbacks(widget)

    if quit_mainloop:
        try:
            widget.quit()
        except Exception:
            pass
        cancel_widget_after_callbacks(widget)

    try:
        widget.destroy()
    except Exception:
        # A partially destroyed window should not make application shutdown
        # fail. Owner-aware cancellation above prevents the known Python 3.13
        # duplicate-command deletion path.
        pass
