from __future__ import annotations

import unittest

from tk_test_utils import destroy_tk_root

from gui_core import (
    ActionButton,
    GuiAppConfig,
    LabeledEntry,
    SectionCard,
    Sidebar,
    require_customtkinter,
)


class LayoutProfileSmokeTests(unittest.TestCase):
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

    def test_compact_and_comfortable_controls_use_profile_heights(self) -> None:
        compact_entry = LabeledEntry(
            self.root,
            "Compacto",
            layout_profile="compact",
        )
        comfortable_button = ActionButton(
            self.root,
            "Cómodo",
            layout_profile="comfortable",
        )

        self.assertEqual(int(compact_entry.entry.cget("height")), 26)
        self.assertEqual(int(comfortable_button.button.cget("height")), 40)

        compact_entry.frame.destroy()
        comfortable_button.frame.destroy()

    def test_standard_sidebar_uses_standard_footer_height(self) -> None:
        sidebar = Sidebar(
            self.root,
            GuiAppConfig(
                app_name="Tool",
                maximize_on_start=False,
            ),
        )

        self.assertEqual(
            int(sidebar.footer_buttons["settings"].cget("height")),
            34,
        )
        sidebar.frame.destroy()

    def test_compact_section_card_uses_compact_geometry(self) -> None:
        card = SectionCard(
            self.root,
            "Estado",
            layout_profile="compact",
        )

        self.assertEqual(int(card.frame.cget("corner_radius")), 12)
        self.assertEqual(int(card.header_frame.grid_info()["padx"]), 12)
        self.assertEqual(int(card.title_label.grid_info()["padx"]), 0)
        card.frame.destroy()


if __name__ == "__main__":
    unittest.main()
