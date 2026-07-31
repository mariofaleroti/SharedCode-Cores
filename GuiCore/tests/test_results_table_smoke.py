from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import unittest

from gui_core import ResultsTable, TableColumn


class ResultsTableSmokeTests(unittest.TestCase):
    """Construct real ttk widgets when a graphical display is available."""

    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.root = tk.Tk()
            cls.root.withdraw()
        except tk.TclError as error:
            raise unittest.SkipTest(
                f"A graphical display is not available: {error}"
            ) from error

    @classmethod
    def tearDownClass(cls) -> None:
        if getattr(cls, "root", None) is not None:
            cls.root.destroy()

    def test_table_opens_when_sorting_is_disabled(self) -> None:
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0)

        table = ResultsTable(
            frame,
            columns=(
                TableColumn("field", "Campo", sortable=True),
                TableColumn("value", "Valor", sortable=False),
            ),
            enable_sorting=False,
            enable_tooltips=False,
        )

        self.assertEqual(table.tree.heading("field", "text"), "Campo")
        self.assertEqual(table.tree.heading("value", "text"), "Valor")
        self.assertEqual(table.tree.get_children(), ())

        frame.destroy()

    def test_table_opens_with_mixed_sortable_columns(self) -> None:
        frame = ttk.Frame(self.root)
        frame.grid(row=0, column=0)

        table = ResultsTable(
            frame,
            columns=(
                TableColumn("name", "Nombre"),
                TableColumn("status", "Estado", sortable=False),
            ),
            enable_sorting=True,
            enable_tooltips=False,
        )
        table.set_rows(
            (
                {"name": "Beta", "status": "OK"},
                {"name": "Alpha", "status": "OK"},
            )
        )

        self.assertEqual(len(table.tree.get_children()), 2)
        table.sort_by_column("name")
        first_item = table.tree.get_children()[0]
        self.assertEqual(table.tree.item(first_item, "values")[0], "Alpha")

        frame.destroy()


if __name__ == "__main__":
    unittest.main()
