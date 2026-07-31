from __future__ import annotations

from typing import Any


def cancel_pending_after_callbacks(root: Any) -> None:
    """Cancel every pending Tk ``after`` callback registered on one root."""

    if root is None:
        return

    for _ in range(4):
        try:
            pending = root.tk.call("after", "info")
        except Exception:
            return

        if isinstance(pending, str):
            try:
                callback_ids = tuple(root.tk.splitlist(pending))
            except Exception:
                callback_ids = (pending,) if pending else ()
        else:
            try:
                callback_ids = tuple(pending)
            except TypeError:
                callback_ids = ()

        if not callback_ids:
            return

        for callback_id in callback_ids:
            try:
                root.after_cancel(callback_id)
            except Exception:
                try:
                    root.tk.call("after", "cancel", callback_id)
                except Exception:
                    pass


def destroy_tk_root(root: Any) -> None:
    """Destroy one Tk root without leaving delayed callbacks behind."""

    if root is None:
        return

    try:
        exists = bool(root.winfo_exists())
    except Exception:
        exists = False

    if not exists:
        return

    cancel_pending_after_callbacks(root)

    try:
        root.quit()
    except Exception:
        pass

    cancel_pending_after_callbacks(root)

    try:
        root.destroy()
    except Exception:
        pass
