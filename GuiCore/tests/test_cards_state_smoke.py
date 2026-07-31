from __future__ import annotations

import unittest

from gui_core import (
    CardHeaderAction,
    CollapsibleSectionCard,
    EmptyState,
    GuiAppConfig,
    GuiAppWindow,
    KeyValueItem,
    KeyValueTable,
    SectionCard,
    require_customtkinter,
)


class CardsStateSmokeTests(unittest.TestCase):
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

    def test_section_card_header_action_invokes_callback(self) -> None:
        calls = []
        card = SectionCard(
            self.root,
            "Estado",
            "Resumen operativo",
            header_actions=(
                CardHeaderAction(
                    "Actualizar",
                    command=lambda: calls.append("refresh"),
                    command_key="refresh",
                ),
            ),
        )

        card.header_action_buttons["refresh"].invoke()
        self.assertEqual(calls, ["refresh"])
        card.set_header_action_enabled("refresh", False)
        self.assertEqual(
            card.header_action_buttons["refresh"].cget("state"),
            "disabled",
        )
        card.frame.destroy()

    def test_collapsible_card_hides_and_restores_content(self) -> None:
        states = []
        card = CollapsibleSectionCard(
            self.root,
            "Detalle",
            "Información completa",
            collapsed_summary="Panel contraído",
            on_toggle=states.append,
        )
        label = self.ctk.CTkLabel(
            card.content_frame,
            text="Contenido",
        )
        label.grid(row=0, column=0)

        card.set_collapsed(True)
        self.assertTrue(card.is_collapsed)
        self.assertFalse(card.content_frame.winfo_ismapped())
        self.assertEqual(card.subtitle_label.cget("text"), "Panel contraído")

        card.set_collapsed(False)
        self.assertFalse(card.is_collapsed)
        self.assertEqual(
            card.subtitle_label.cget("text"),
            "Información completa",
        )
        self.assertEqual(states, [True, False])
        card.frame.destroy()

    def test_key_value_table_and_empty_state_render(self) -> None:
        table = KeyValueTable(
            self.root,
            (
                KeyValueItem("Estado", "Operativo", "success"),
                KeyValueItem("Tarea", "Instalada"),
            ),
        )
        self.assertEqual(len(table._row_widgets), 2)
        table.set_items({"Rutas": 2})
        self.assertEqual(len(table._row_widgets), 1)

        calls = []
        empty = EmptyState(
            self.root,
            "Sin resultados",
            "Ejecutar una búsqueda para comenzar.",
            action_text="Buscar",
            action_command=lambda: calls.append("search"),
        )
        empty.action_button.invoke()
        self.assertEqual(calls, ["search"])
        empty.set_state(
            "error",
            title="No se pudo cargar",
        )
        self.assertEqual(empty.state, "error")
        self.assertEqual(
            empty.title_label.cget("text"),
            "No se pudo cargar",
        )

        table.frame.destroy()
        empty.frame.destroy()

    def test_app_window_declares_card_weight_minsize_and_sticky(self) -> None:
        app = GuiAppWindow(
            GuiAppConfig(
                app_name="Cards",
                maximize_on_start=False,
            )
        )
        card = app.add_content_card(
            "Principal",
            row_weight=3,
            min_height=320,
            sticky="nsew",
        )
        second = app.add_collapsible_card(
            "Secundaria",
            row_weight=1,
            min_height=140,
            collapsed=True,
        )

        first_row = int(card.frame.grid_info()["row"])
        second_row = int(second.frame.grid_info()["row"])
        self.assertEqual(
            int(app.content_panel.frame.grid_rowconfigure(first_row)["weight"]),
            3,
        )
        self.assertEqual(
            int(app.content_panel.frame.grid_rowconfigure(first_row)["minsize"]),
            320,
        )
        self.assertEqual(card.frame.grid_info()["sticky"], "nesw")
        self.assertEqual(
            int(app.content_panel.frame.grid_rowconfigure(second_row)["weight"]),
            1,
        )
        app.root.destroy()


if __name__ == "__main__":
    unittest.main()
