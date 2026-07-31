from __future__ import annotations

import unittest

from tk_test_utils import destroy_tk_root

from gui_core import (
    GuiAppConfig,
    GuiPreferences,
    SettingsWindow,
    Sidebar,
    VISUAL_PREFERENCES_ADVANCED,
    VISUAL_PREFERENCES_BASIC,
    require_customtkinter,
)


class VisualPreferencesModesSmokeTests(unittest.TestCase):
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

    def test_none_mode_sidebar_omits_settings_button(self) -> None:
        sidebar = Sidebar(
            self.root,
            GuiAppConfig(
                app_name="Tool",
                visual_preferences="none",
                maximize_on_start=False,
            ),
        )
        self.assertNotIn("settings", sidebar.footer_buttons)
        self.assertIn("help", sidebar.footer_buttons)
        sidebar.frame.destroy()

    def test_basic_settings_show_essential_controls_only(self) -> None:
        original = GuiPreferences(
            color_theme="purple",
            surface_theme="onyx",
        )
        window = SettingsWindow(
            self.root,
            preferences=original,
            preference_mode=VISUAL_PREFERENCES_BASIC,
        )
        self.assertTrue(hasattr(window, "appearance_combo"))
        self.assertTrue(hasattr(window, "font_family_combo"))
        self.assertTrue(hasattr(window, "table_density_combo"))
        self.assertFalse(hasattr(window, "color_theme_combo"))
        self.assertFalse(hasattr(window, "surface_theme_combo"))
        collected = window.collect_preferences()
        self.assertEqual(collected.color_theme, "purple")
        self.assertEqual(collected.surface_theme, "onyx")
        window.close()
        window.close()  # Closing a secondary window is idempotent.

    def test_advanced_settings_show_palette_controls(self) -> None:
        window = SettingsWindow(
            self.root,
            preference_mode=VISUAL_PREFERENCES_ADVANCED,
        )
        self.assertTrue(hasattr(window, "color_theme_combo"))
        self.assertTrue(hasattr(window, "surface_theme_combo"))
        self.assertTrue(hasattr(window, "accent_preview_bar"))
        window.close()


if __name__ == "__main__":
    unittest.main()
