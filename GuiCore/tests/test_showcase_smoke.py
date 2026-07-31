from __future__ import annotations

import importlib.util
import pathlib
import unittest

from tk_test_utils import destroy_tk_root

from gui_core import require_customtkinter


class ShowcaseSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            require_customtkinter()
        except Exception as error:
            raise unittest.SkipTest(
                f"A graphical CustomTkinter environment is not available: {error}"
            ) from error

        example_path = (
            pathlib.Path(__file__).resolve().parents[1]
            / "examples"
            / "guicore_1_1_showcase.py"
        )
        spec = importlib.util.spec_from_file_location(
            "guicore_1_1_showcase",
            example_path,
        )
        if spec is None or spec.loader is None:
            raise RuntimeError("Could not load showcase module.")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_official_showcase_builds_integrated_contract(self) -> None:
        app, references = self.module.build_showcase("basic")
        try:
            self.assertEqual(app.visual_preferences_mode, "basic")
            self.assertIn("settings", app.sidebar.footer_buttons)
            self.assertIn("run", app.sidebar.primary_buttons)
            self.assertIn("cancel", app.sidebar.primary_buttons)
            self.assertEqual(len(references["metrics"].cards), 4)
            self.assertGreaterEqual(references["table"].get_row_count(), 1)
            self.assertFalse(references["details_card"].is_collapsed)
        finally:
            app.destroy()

    def test_showcase_none_mode_has_no_settings_action(self) -> None:
        app, _references = self.module.build_showcase("none")
        try:
            self.assertNotIn("settings", app.sidebar.footer_buttons)
            self.assertIsNone(app.show_settings())
        finally:
            app.destroy()


if __name__ == "__main__":
    unittest.main()
