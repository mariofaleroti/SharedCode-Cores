from __future__ import annotations

import unittest

from tk_test_utils import destroy_tk_root

from gui_core import (
    MetricCard,
    MetricItem,
    MetricStrip,
    WidgetTooltip,
    require_customtkinter,
)


class MetricsTooltipsSmokeTests(unittest.TestCase):
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

    def test_metric_card_updates_value_semantic_and_tooltip(self) -> None:
        card = MetricCard(
            self.root,
            MetricItem(
                "processed",
                "Procesados",
                12,
                semantic="info",
                detail="Elementos",
                tooltip="Cantidad procesada.",
            ),
            layout_profile="compact",
        )

        updated = card.update_metric(
            value=18,
            semantic="success",
            detail="Completados",
            tooltip="Cantidad completada.",
        )
        self.assertEqual(updated.value, 18)
        self.assertEqual(card.value_label.cget("text"), "18")
        self.assertEqual(card.detail_label.cget("text"), "Completados")
        self.assertEqual(
            card.tooltip.spec.text,
            "Cantidad completada.",
        )
        card.destroy()

    def test_metric_strip_builds_grid_and_updates_by_key(self) -> None:
        strip = MetricStrip(
            self.root,
            (
                MetricItem("one", "Uno", 1),
                MetricItem("two", "Dos", 2),
                MetricItem("three", "Tres", 3),
            ),
            columns=2,
            layout_profile="compact",
        )

        self.assertEqual(len(strip.cards), 3)
        self.assertEqual(
            int(strip.cards["one"].frame.grid_info()["column"]),
            0,
        )
        self.assertEqual(
            int(strip.cards["two"].frame.grid_info()["column"]),
            1,
        )
        self.assertEqual(
            int(strip.cards["three"].frame.grid_info()["row"]),
            1,
        )

        updated = strip.update_metric(
            "two",
            value=22,
            detail="Actualizado",
        )
        self.assertEqual(updated.value, 22)
        self.assertEqual(
            strip.get_metric_card("two").value_label.cget("text"),
            "22",
        )
        strip.destroy()

    def test_tooltip_show_hide_and_destroy_cancel_callbacks(self) -> None:
        button = self.ctk.CTkButton(
            self.root,
            text="Ayuda",
        )
        button.grid(row=0, column=0)
        self.root.update_idletasks()

        tooltip = WidgetTooltip(
            button,
            "Descripción contextual.",
            title="Ayuda",
            delay_ms=10,
            visible_ms=0,
        )
        shown = tooltip.show_now()
        self.assertTrue(shown)
        self.assertTrue(tooltip.is_visible)

        tooltip.hide()
        self.assertFalse(tooltip.is_visible)

        tooltip.schedule()
        self.assertIsNotNone(tooltip._show_after_id)
        tooltip.destroy()
        self.assertIsNone(tooltip._show_after_id)
        self.assertFalse(tooltip.is_visible)
        button.destroy()

    def test_tooltip_without_text_does_not_open(self) -> None:
        label = self.ctk.CTkLabel(
            self.root,
            text="Sin ayuda",
        )
        tooltip = WidgetTooltip(
            label,
            "",
            enabled=True,
        )
        self.assertFalse(tooltip.show_now())
        tooltip.destroy()
        label.destroy()


if __name__ == "__main__":
    unittest.main()
