from __future__ import annotations

import unittest

from tk_test_utils import destroy_tk_root

from gui_core import (
    GuiActionButton,
    GuiAppConfig,
    GuiMenuItem,
    Sidebar,
    SidebarConfig,
    require_customtkinter,
)


class SidebarConfigurationSmokeTests(unittest.TestCase):
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

    def test_two_column_footer_and_fixed_actions(self) -> None:
        calls = []
        sidebar = Sidebar(
            self.root,
            GuiAppConfig(
                app_name="Tool",
                layout_profile="compact",
                maximize_on_start=False,
                sidebar_config=SidebarConfig(
                    footer_columns=2,
                    footer_label_visible=False,
                    primary_action_columns=2,
                ),
                primary_actions=(
                    GuiActionButton("Ejecutar", "run"),
                    GuiActionButton(
                        "Limpiar",
                        "clear",
                        style="secondary",
                    ),
                ),
                footer_items=(
                    GuiMenuItem("Ayuda", "help"),
                    GuiMenuItem("Salir", "exit"),
                ),
            ),
        )
        sidebar.set_action("run", lambda: calls.append("run"))

        self.assertIsNone(sidebar.footer_label)
        self.assertEqual(
            int(sidebar.primary_buttons["run"].grid_info()["column"]),
            0,
        )
        self.assertEqual(
            int(sidebar.primary_buttons["clear"].grid_info()["column"]),
            1,
        )
        self.assertEqual(
            int(sidebar.footer_buttons["help"].grid_info()["column"]),
            0,
        )
        self.assertEqual(
            int(sidebar.footer_buttons["exit"].grid_info()["column"]),
            1,
        )

        sidebar.primary_buttons["run"].invoke()
        self.assertEqual(calls, ["run"])

        sidebar.set_action_enabled("run", False)
        self.assertEqual(
            sidebar.primary_buttons["run"].cget("state"),
            "disabled",
        )
        sidebar.frame.destroy()

    def test_header_and_scroll_can_be_disabled(self) -> None:
        sidebar = Sidebar(
            self.root,
            GuiAppConfig(
                app_name="Tool",
                maximize_on_start=False,
                sidebar_config=SidebarConfig(
                    header_visible=False,
                    scrollable=False,
                ),
                footer_items=(),
            ),
        )

        self.assertIsNone(sidebar.header_frame)
        self.assertNotIn("_scrollbar", vars(sidebar.controls_frame))
        self.assertIsNone(sidebar.footer_frame)
        sidebar.frame.destroy()

    def test_scrollbar_width_override_is_applied(self) -> None:
        sidebar = Sidebar(
            self.root,
            GuiAppConfig(
                app_name="Tool",
                maximize_on_start=False,
                sidebar_config=SidebarConfig(scrollbar_width=13),
            ),
        )

        self.assertEqual(
            int(sidebar.controls_frame._scrollbar.cget("width")),
            13,
        )
        sidebar.frame.destroy()


if __name__ == "__main__":
    unittest.main()
