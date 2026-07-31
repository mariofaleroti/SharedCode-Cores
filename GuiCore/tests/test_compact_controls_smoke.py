from __future__ import annotations

import unittest

from gui_core import (
    ChoiceOption,
    LabeledCheckBox,
    LabeledComboAction,
    LabeledComboBox,
    LabeledEntry,
    LabeledSwitch,
    PathPicker,
    SidebarFormSection,
    require_customtkinter,
)


class CompactControlsSmokeTests(unittest.TestCase):
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
        if getattr(cls, "root", None) is not None:
            cls.root.destroy()

    def test_entry_combo_picker_and_switch_accept_compact_overrides(self) -> None:
        entry = LabeledEntry(
            self.root,
            "Buscar",
            label_visible=False,
            height=25,
            width=280,
            font_role="small",
        )
        combo = LabeledComboBox(
            self.root,
            "Modo",
            ("Nombre", "Contenido"),
            height=25,
            width=280,
            font_role="small",
            label_gap=1,
        )
        picker = PathPicker(
            self.root,
            "Ruta",
            width=280,
            height=25,
            button_width=32,
            gap=5,
            font_role="small",
        )
        switch = LabeledSwitch(
            self.root,
            "Recordar ubicación",
            height=21,
            font_role="small",
        )
        checkbox = LabeledCheckBox(
            self.root,
            "Incluir subcarpetas",
            height=21,
            font_role="small",
        )

        self.assertIsNone(entry.label)
        self.assertEqual(int(entry.entry.cget("height")), 25)
        self.assertEqual(int(entry.entry.cget("width")), 280)
        self.assertEqual(int(combo.combo.cget("height")), 25)
        self.assertEqual(int(picker.button.cget("width")), 32)
        self.assertEqual(int(switch.switch.cget("height")), 21)
        self.assertEqual(int(checkbox.checkbox.cget("height")), 21)

        for control in (entry, combo, picker, switch, checkbox):
            control.frame.destroy()

    def test_combo_action_preserves_stable_values_and_action_state(self) -> None:
        calls = []
        control = LabeledComboAction(
            self.root,
            "Categoría",
            (
                ChoiceOption("Todos", "all"),
                ChoiceOption("Documentos", "documents"),
            ),
            default_value="Documentos",
            button_text="...",
            button_command=lambda: calls.append("action"),
            width=300,
            height=26,
            button_width=34,
            gap=6,
            font_role="small",
        )

        self.assertEqual(control.get_label(), "Documentos")
        self.assertEqual(control.get_value(), "documents")
        control.button.invoke()
        self.assertEqual(calls, ["action"])

        control.set_action_enabled(False)
        self.assertEqual(control.button.cget("state"), "disabled")
        control.set_values(("Uno", "Dos"), default_value="Dos")
        self.assertEqual(control.get_value(), "Dos")
        control.frame.destroy()

    def test_sidebar_section_builds_combo_action_without_manual_frames(self) -> None:
        section = SidebarFormSection(
            self.root,
            "Filtros",
            layout_profile="compact",
        )
        control = section.add_labeled_combo_action(
            "Tipo",
            ("Todos", "PDF"),
            button_text="...",
            width=280,
            font_role="small",
        )

        self.assertIsInstance(control, LabeledComboAction)
        self.assertIn(control, section._widgets)
        section.frame.destroy()


if __name__ == "__main__":
    unittest.main()
