from __future__ import annotations

from typing import Any

from gui_core.tk_lifecycle import (
    cancel_widget_after_callbacks,
    destroy_widget_tree,
)


def cancel_pending_after_callbacks(root: Any) -> int:
    """Compatibility wrapper around owner-aware GuiCore teardown."""

    return cancel_widget_after_callbacks(root)


def destroy_tk_root(root: Any) -> None:
    """Destroy one Tk root through the production lifecycle helper."""

    destroy_widget_tree(
        root,
        quit_mainloop=True,
    )
