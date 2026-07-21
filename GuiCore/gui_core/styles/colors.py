from __future__ import annotations

from typing import Dict, Iterable, Mapping


# Accent colors drive action elements: primary buttons, progress, table selection,
# switches and small emphasis elements. They are intentionally separate from the
# app surface palette so a tool can look graphite/dark while keeping a blue,
# purple or orange action color.
ACCENT_COLOR_PALETTE: Dict[str, Dict[str, str]] = {
    "blue": {"primary": "#1f6aa5", "hover": "#185985", "selected": "#1f6aa5"},
    "green": {"primary": "#2e7d32", "hover": "#256628", "selected": "#2e7d32"},
    "dark-blue": {"primary": "#14375f", "hover": "#0f2a49", "selected": "#174a7c"},
    "purple": {"primary": "#6f42c1", "hover": "#59359a", "selected": "#6f42c1"},
    "orange": {"primary": "#c76511", "hover": "#9f500d", "selected": "#c76511"},
    "red": {"primary": "#b3261e", "hover": "#8c1d18", "selected": "#b3261e"},
    "teal": {"primary": "#0f766e", "hover": "#0b5f59", "selected": "#0f766e"},
    "black": {"primary": "#111827", "hover": "#0b1120", "selected": "#30363d"},
    "charcoal": {"primary": "#252a2e", "hover": "#1b1f23", "selected": "#3a4046"},
    "graphite": {"primary": "#3b3f45", "hover": "#2f3338", "selected": "#4b5159"},
    "slate": {"primary": "#475569", "hover": "#334155", "selected": "#475569"},
    "gray": {"primary": "#5f6368", "hover": "#4a4d51", "selected": "#5f6368"},
}

ACCENT_COLOR_OPTIONS = tuple(ACCENT_COLOR_PALETTE.keys())


# Surface colors drive the app base: root, sidebar, content area, cards and
# neutral buttons. Each palette provides dark/light variants so the selected
# appearance can still decide contrast while the user controls the overall mood.
SURFACE_COLOR_PALETTE: Dict[str, Dict[str, Dict[str, str]]] = {
    "default": {
        "dark": {
            "root": "#242424",
            "sidebar": "#242424",
            "sidebar_footer": "#2b2b2b",
            "content": "#242424",
            "card": "#2b2b2b",
            "card_alt": "#303030",
            "neutral": "#4a4a4a",
            "neutral_hover": "#555555",
            "border": "#565b5e",
            "table_odd": "#242424",
            "table_even": "#1f1f1f",
            "table_heading": "#2b2b2b",
            "table_background": "#1f1f1f",
        },
        "light": {
            "root": "#ebebeb",
            "sidebar": "#ebebeb",
            "sidebar_footer": "#dedede",
            "content": "#ebebeb",
            "card": "#f4f4f4",
            "card_alt": "#ffffff",
            "neutral": "#d0d0d0",
            "neutral_hover": "#c2c2c2",
            "border": "#b8c0c8",
            "table_odd": "#e9eef3",
            "table_even": "#f7f7f7",
            "table_heading": "#e0e0e0",
            "table_background": "#f3f3f3",
        },
    },
    "onyx": {
        "dark": {
            "root": "#07090d",
            "sidebar": "#0b0f16",
            "sidebar_footer": "#111827",
            "content": "#080b10",
            "card": "#111827",
            "card_alt": "#172033",
            "neutral": "#202938",
            "neutral_hover": "#2b3648",
            "border": "#313b4d",
            "table_odd": "#111827",
            "table_even": "#0b0f16",
            "table_heading": "#171f2e",
            "table_background": "#0b0f16",
        },
        "light": {
            "root": "#e8edf5",
            "sidebar": "#eef2f8",
            "sidebar_footer": "#d9e1ec",
            "content": "#e8edf5",
            "card": "#f8fafc",
            "card_alt": "#ffffff",
            "neutral": "#cbd5e1",
            "neutral_hover": "#b7c4d4",
            "border": "#94a3b8",
            "table_odd": "#e2e8f0",
            "table_even": "#f8fafc",
            "table_heading": "#dbe3ee",
            "table_background": "#f1f5f9",
        },
    },
    "charcoal": {
        "dark": {
            "root": "#171a1d",
            "sidebar": "#1c2024",
            "sidebar_footer": "#252a2e",
            "content": "#171a1d",
            "card": "#252a2e",
            "card_alt": "#2e3439",
            "neutral": "#3b4248",
            "neutral_hover": "#48515a",
            "border": "#56616a",
            "table_odd": "#24292e",
            "table_even": "#1c2024",
            "table_heading": "#2e3439",
            "table_background": "#1c2024",
        },
        "light": {
            "root": "#edf0f2",
            "sidebar": "#f2f4f5",
            "sidebar_footer": "#dfe4e7",
            "content": "#edf0f2",
            "card": "#f8f9fa",
            "card_alt": "#ffffff",
            "neutral": "#d4dadd",
            "neutral_hover": "#c4ccd1",
            "border": "#9aa4aa",
            "table_odd": "#e5eaed",
            "table_even": "#f7f9fa",
            "table_heading": "#dce2e6",
            "table_background": "#f2f4f6",
        },
    },
    "graphite": {
        "dark": {
            "root": "#22252a",
            "sidebar": "#282c32",
            "sidebar_footer": "#30343b",
            "content": "#22252a",
            "card": "#30343b",
            "card_alt": "#383d45",
            "neutral": "#454b55",
            "neutral_hover": "#505762",
            "border": "#606874",
            "table_odd": "#292d33",
            "table_even": "#22252a",
            "table_heading": "#353a42",
            "table_background": "#22252a",
        },
        "light": {
            "root": "#eef0f3",
            "sidebar": "#f5f6f8",
            "sidebar_footer": "#e0e4e8",
            "content": "#eef0f3",
            "card": "#fafafa",
            "card_alt": "#ffffff",
            "neutral": "#d4d9de",
            "neutral_hover": "#c6ccd3",
            "border": "#a4adb7",
            "table_odd": "#e7ebef",
            "table_even": "#f8fafc",
            "table_heading": "#dfe4ea",
            "table_background": "#f2f5f8",
        },
    },
    "midnight": {
        "dark": {
            "root": "#07111f",
            "sidebar": "#0b1628",
            "sidebar_footer": "#101d32",
            "content": "#07111f",
            "card": "#101d32",
            "card_alt": "#162642",
            "neutral": "#213654",
            "neutral_hover": "#294263",
            "border": "#34506f",
            "table_odd": "#0f1b2d",
            "table_even": "#0a1424",
            "table_heading": "#15243b",
            "table_background": "#0a1424",
        },
        "light": {
            "root": "#eaf1fb",
            "sidebar": "#f0f5fc",
            "sidebar_footer": "#dbe8f7",
            "content": "#eaf1fb",
            "card": "#f8fbff",
            "card_alt": "#ffffff",
            "neutral": "#cddbeb",
            "neutral_hover": "#bbccdf",
            "border": "#98abc2",
            "table_odd": "#e1ebf6",
            "table_even": "#f7fbff",
            "table_heading": "#d8e5f2",
            "table_background": "#f0f6fd",
        },
    },
    "forest": {
        "dark": {
            "root": "#0d1812",
            "sidebar": "#122018",
            "sidebar_footer": "#1a2b21",
            "content": "#0d1812",
            "card": "#1a2b21",
            "card_alt": "#22372a",
            "neutral": "#2d4635",
            "neutral_hover": "#385942",
            "border": "#466b50",
            "table_odd": "#17251c",
            "table_even": "#101b14",
            "table_heading": "#203329",
            "table_background": "#101b14",
        },
        "light": {
            "root": "#edf7ef",
            "sidebar": "#f4fbf5",
            "sidebar_footer": "#dcefe1",
            "content": "#edf7ef",
            "card": "#f9fefa",
            "card_alt": "#ffffff",
            "neutral": "#cfe3d4",
            "neutral_hover": "#bdd7c4",
            "border": "#97b8a1",
            "table_odd": "#e2f1e6",
            "table_even": "#f7fcf8",
            "table_heading": "#d9eadf",
            "table_background": "#f0f8f2",
        },
    },
}

SURFACE_COLOR_OPTIONS = tuple(SURFACE_COLOR_PALETTE.keys())


def normalize_appearance_mode(appearance_mode: str | None) -> str:
    value = (appearance_mode or "dark").lower()
    if value in {"dark", "oscuro"}:
        return "dark"
    if value in {"light", "claro"}:
        return "light"
    if value in {"system", "sistema"}:
        # For widget-owned colors, system cannot be queried safely before CTk is
        # ready, so use the dark variant as the stable fallback.
        return "dark"
    return value if value in {"dark", "light"} else "dark"


def normalize_accent_color(value: str | None) -> str:
    normalized = str(value or "blue").strip().lower()
    return normalized if normalized in ACCENT_COLOR_PALETTE else "blue"


def normalize_surface_color(value: str | None) -> str:
    normalized = str(value or "default").strip().lower()
    return normalized if normalized in SURFACE_COLOR_PALETTE else "default"


def get_accent_colors(color_theme: str | None = "blue") -> Dict[str, str]:
    return dict(ACCENT_COLOR_PALETTE[normalize_accent_color(color_theme)])


def get_surface_colors(appearance_mode: str | None = "dark", surface_color: str | None = "default") -> Dict[str, str]:
    mode = normalize_appearance_mode(appearance_mode)
    palette = SURFACE_COLOR_PALETTE[normalize_surface_color(surface_color)]
    return dict(palette.get(mode) or palette["dark"])


def get_supported_accent_colors() -> Iterable[str]:
    return ACCENT_COLOR_OPTIONS


def get_supported_surface_colors() -> Iterable[str]:
    return SURFACE_COLOR_OPTIONS


def get_table_colors(
    appearance_mode: str | None = "dark",
    color_theme: str | None = "blue",
    surface_color: str | None = "default",
) -> Dict[str, str]:
    mode = normalize_appearance_mode(appearance_mode)
    accent = get_accent_colors(color_theme)
    surface = get_surface_colors(mode, surface_color)

    if mode == "dark":
        return {
            "background": surface["table_background"],
            "foreground": "#f2f2f2",
            "fieldbackground": surface["table_background"],
            "heading_background": surface["table_heading"],
            "heading_foreground": "#f2f2f2",
            "odd_row": surface["table_odd"],
            "even_row": surface["table_even"],
            "selected_background": accent["selected"],
            "selected_foreground": "#ffffff",
        }

    return {
        "background": surface["table_background"],
        "foreground": "#111111",
        "fieldbackground": surface["table_background"],
        "heading_background": surface["table_heading"],
        "heading_foreground": "#111111",
        "odd_row": surface["table_odd"],
        "even_row": surface["table_even"],
        "selected_background": accent["selected"],
        "selected_foreground": "#ffffff",
    }


def get_sidebar_listbox_colors(
    appearance_mode: str | None = "dark",
    color_theme: str | None = "blue",
    surface_color: str | None = "default",
) -> Dict[str, str]:
    mode = normalize_appearance_mode(appearance_mode)
    accent = get_accent_colors(color_theme)
    surface = get_surface_colors(mode, surface_color)

    if mode == "dark":
        return {
            "background": surface["sidebar_footer"],
            "foreground": "#f1f1f1",
            "select_background": accent["selected"],
            "select_foreground": "#ffffff",
            "border": surface["border"],
        }

    return {
        "background": surface["sidebar_footer"],
        "foreground": "#111111",
        "select_background": accent["selected"],
        "select_foreground": "#ffffff",
        "border": surface["border"],
    }



def get_control_colors(
    appearance_mode: str | None = "dark",
    surface_color: str | None = "default",
) -> Mapping[str, str]:
    """Return colors for entries, combos, checkboxes and neutral form surfaces.

    These colors deliberately follow the selected app base palette, not the
    accent palette. The accent palette is reserved for actions and emphasis.
    """

    surface = get_surface_colors(appearance_mode, surface_color)
    mode = normalize_appearance_mode(appearance_mode)
    return {
        "fg_color": surface["card_alt"],
        "hover_color": surface["neutral_hover"],
        "border_color": surface["border"],
        "text_color": "#f5f5f5" if mode == "dark" else "#111111",
        "placeholder_text_color": "#9aa0a6" if mode == "dark" else "#5f6368",
        "label_text_color": "#cbd5e1" if mode == "dark" else "#374151",
        "dropdown_fg_color": surface["card_alt"],
        "dropdown_hover_color": surface["neutral_hover"],
    }

def get_neutral_button_colors(
    appearance_mode: str | None = "dark",
    surface_color: str | None = "default",
) -> Mapping[str, str]:
    surface = get_surface_colors(appearance_mode, surface_color)
    mode = normalize_appearance_mode(appearance_mode)
    return {
        "fg_color": surface["neutral"],
        "hover_color": surface["neutral_hover"],
        "text_color": "#ffffff" if mode == "dark" else "#111111",
        "border_color": surface["border"],
    }
