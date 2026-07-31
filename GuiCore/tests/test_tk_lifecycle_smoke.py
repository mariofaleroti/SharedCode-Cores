from __future__ import annotations

import unittest

from tk_test_utils import destroy_tk_root

from gui_core import require_customtkinter
from gui_core.tk_lifecycle import (
    cancel_widget_after_callbacks,
    destroy_widget_tree,
)


class TkLifecycleSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.ctk = require_customtkinter()
            cls.root = cls.ctk.CTk()
            cls.root.withdraw()
        except Exception as error:
            raise unittest.SkipTest(
                f"A graphical CustomTkinter environment is not available: {error}"
            ) from error

    @classmethod
    def tearDownClass(cls) -> None:
        destroy_tk_root(getattr(cls, "root", None))
        cls.root = None

    def test_subtree_callbacks_are_cancelled_by_real_owner(self) -> None:
        window = self.ctk.CTkToplevel(self.root)
        window.withdraw()
        child = self.ctk.CTkFrame(window)
        child.pack()

        callback_id = child.after(60_000, lambda: None)
        command_name = str(
            child.tk.splitlist(
                child.tk.call("after", "info", callback_id)
            )[0]
        )
        self.assertIn(command_name, tuple(child._tclCommands or ()))

        cancelled = cancel_widget_after_callbacks(window)
        self.assertGreaterEqual(cancelled, 1)
        self.assertNotIn(command_name, tuple(child._tclCommands or ()))

        destroy_widget_tree(window)

    def test_destroy_widget_tree_ignores_callbacks_outside_subtree(self) -> None:
        external_id = self.root.after(60_000, lambda: None)

        window = self.ctk.CTkToplevel(self.root)
        window.withdraw()
        child = self.ctk.CTkLabel(window, text="Child")
        child.pack()
        child.after(60_000, lambda: None)

        destroy_widget_tree(window)

        pending = tuple(
            self.root.tk.splitlist(
                self.root.tk.call("after", "info")
            )
        )
        self.assertIn(external_id, pending)
        self.root.after_cancel(external_id)


if __name__ == "__main__":
    unittest.main()
