from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Mapping


@dataclass(frozen=True)
class GuiLayoutProfile:
    """Reusable density and spacing tokens for GuiCore application shells.

    Layout profiles contain visual geometry only. They never define project
    content, commands, persistence, or business behavior.
    """

    name: str = "standard"
    font_size_offset: int = 0
    control_height: int = 28
    toggle_height: int = 24
    action_height: int = 34
    menu_button_height: int = 34
    picker_button_width: int = 34
    label_gap: int = 4
    widget_gap: int = 10
    inline_gap: int = 8
    button_gap: int = 10
    section_title_pad_top: int = 4
    section_title_pad_bottom: int = 5
    section_subtitle_pad_bottom: int = 8
    sidebar_padding: int = 14
    sidebar_header_pad_x: int = 18
    sidebar_header_pad_top: int = 24
    sidebar_header_pad_bottom: int = 8
    sidebar_controls_pad_top: int = 8
    sidebar_controls_pad_bottom: int = 8
    sidebar_footer_label_pad_top: int = 12
    sidebar_footer_label_pad_bottom: int = 6
    sidebar_footer_button_gap: int = 7
    sidebar_scrollbar_width: int | None = None
    content_pad_x: int = 20
    content_pad_top: int = 20
    content_card_gap: int = 12
    card_inner_pad_x: int = 16
    card_header_pad_top: int = 14
    card_title_gap: int = 2
    card_subtitle_gap: int = 8
    card_content_pad_top: int = 8
    card_content_pad_bottom: int = 16
    card_corner_radius: int = 14

    def __post_init__(self) -> None:
        if not str(self.name).strip():
            raise ValueError("GuiLayoutProfile.name cannot be empty.")
        if not -4 <= int(self.font_size_offset) <= 4:
            raise ValueError("font_size_offset must be between -4 and 4.")

        positive_fields = (
            "control_height",
            "toggle_height",
            "action_height",
            "menu_button_height",
            "picker_button_width",
            "sidebar_padding",
            "sidebar_header_pad_x",
            "sidebar_scrollbar_width",
            "content_pad_x",
            "card_inner_pad_x",
            "card_corner_radius",
        )
        non_negative_fields = tuple(
            field_name
            for field_name in self.__dataclass_fields__
            if field_name not in {"name", "font_size_offset", *positive_fields}
        )

        for field_name in positive_fields:
            value = getattr(self, field_name)
            if value is None:
                continue
            if int(value) <= 0:
                raise ValueError(f"{field_name} must be greater than zero.")
        for field_name in non_negative_fields:
            value = getattr(self, field_name)
            if value is None:
                continue
            if int(value) < 0:
                raise ValueError(f"{field_name} cannot be negative.")

    def to_dict(self) -> dict[str, Any]:
        return {
            field_name: getattr(self, field_name)
            for field_name in self.__dataclass_fields__
        }


COMPACT_LAYOUT_PROFILE = GuiLayoutProfile(
    name="compact",
    font_size_offset=-1,
    control_height=26,
    toggle_height=22,
    action_height=30,
    menu_button_height=26,
    picker_button_width=30,
    label_gap=2,
    widget_gap=6,
    inline_gap=6,
    button_gap=6,
    section_title_pad_top=2,
    section_title_pad_bottom=3,
    section_subtitle_pad_bottom=5,
    sidebar_padding=10,
    sidebar_header_pad_x=12,
    sidebar_header_pad_top=14,
    sidebar_header_pad_bottom=5,
    sidebar_controls_pad_top=4,
    sidebar_controls_pad_bottom=4,
    sidebar_footer_label_pad_top=6,
    sidebar_footer_label_pad_bottom=3,
    sidebar_footer_button_gap=4,
    sidebar_scrollbar_width=8,
    content_pad_x=14,
    content_pad_top=14,
    content_card_gap=8,
    card_inner_pad_x=12,
    card_header_pad_top=10,
    card_title_gap=1,
    card_subtitle_gap=5,
    card_content_pad_top=5,
    card_content_pad_bottom=12,
    card_corner_radius=12,
)

STANDARD_LAYOUT_PROFILE = GuiLayoutProfile()

COMFORTABLE_LAYOUT_PROFILE = GuiLayoutProfile(
    name="comfortable",
    font_size_offset=1,
    control_height=32,
    toggle_height=28,
    action_height=40,
    menu_button_height=40,
    picker_button_width=40,
    label_gap=6,
    widget_gap=14,
    inline_gap=10,
    button_gap=12,
    section_title_pad_top=6,
    section_title_pad_bottom=7,
    section_subtitle_pad_bottom=11,
    sidebar_padding=18,
    sidebar_header_pad_x=22,
    sidebar_header_pad_top=28,
    sidebar_header_pad_bottom=12,
    sidebar_controls_pad_top=12,
    sidebar_controls_pad_bottom=12,
    sidebar_footer_label_pad_top=16,
    sidebar_footer_label_pad_bottom=8,
    sidebar_footer_button_gap=9,
    sidebar_scrollbar_width=12,
    content_pad_x=24,
    content_pad_top=24,
    content_card_gap=16,
    card_inner_pad_x=20,
    card_header_pad_top=18,
    card_title_gap=4,
    card_subtitle_gap=11,
    card_content_pad_top=11,
    card_content_pad_bottom=20,
    card_corner_radius=16,
)

LAYOUT_PROFILE_NAMES = ("compact", "standard", "comfortable")

_LAYOUT_PROFILE_ALIASES = {
    "compact": "compact",
    "compacto": "compact",
    "compacta": "compact",
    "dense": "compact",
    "standard": "standard",
    "estandar": "standard",
    "estándar": "standard",
    "normal": "standard",
    "comfortable": "comfortable",
    "comodo": "comfortable",
    "cómodo": "comfortable",
    "comoda": "comfortable",
    "cómoda": "comfortable",
}

_LAYOUT_PROFILES: Mapping[str, GuiLayoutProfile] = MappingProxyType(
    {
        "compact": COMPACT_LAYOUT_PROFILE,
        "standard": STANDARD_LAYOUT_PROFILE,
        "comfortable": COMFORTABLE_LAYOUT_PROFILE,
    }
)


def normalize_layout_profile_name(value: str | None) -> str:
    normalized = str(value or "standard").strip().lower().replace("-", "_")
    return _LAYOUT_PROFILE_ALIASES.get(normalized, "standard")


def get_layout_profile(
    value: str | GuiLayoutProfile | None = "standard",
) -> GuiLayoutProfile:
    """Return a validated predefined or custom layout profile."""

    if isinstance(value, GuiLayoutProfile):
        return value
    return _LAYOUT_PROFILES[normalize_layout_profile_name(value)]
