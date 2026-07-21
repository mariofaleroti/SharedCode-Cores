from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Mapping

from .constants import DEFAULT_APPEARANCE_MODE, DEFAULT_COLOR_THEME, DEFAULT_SURFACE_THEME
from .models import ThemeConfig
from .styles.colors import (
    ACCENT_COLOR_OPTIONS,
    SURFACE_COLOR_OPTIONS,
    normalize_accent_color,
    normalize_surface_color,
)
from .styles.fonts import (
    APP_FONT_FAMILY_OPTIONS,
    APP_FONT_SIZE_OPTIONS,
    FontConfig,
    normalize_font_family,
    normalize_font_size_option,
)
from .styles.table_style import RESULTS_DENSITY_OPTIONS, get_results_density_row_height

APPEARANCE_LABEL_OPTIONS = ["Sistema", "Oscuro", "Claro"]
APPEARANCE_VALUE_TO_LABEL = {
    "system": "Sistema",
    "dark": "Oscuro",
    "light": "Claro",
    "Sistema": "Sistema",
    "Oscuro": "Oscuro",
    "Claro": "Claro",
}
APPEARANCE_LABEL_TO_VALUE = {
    "Sistema": "system",
    "Oscuro": "dark",
    "Claro": "light",
    "system": "system",
    "dark": "dark",
    "light": "light",
}

# Backward-compatible names: historically GuiCore called the action/accent color
# "color_theme". Newer UI labels expose it as "color de acento" while keeping
# the same raw key for old settings files.
COLOR_THEME_OPTIONS = list(ACCENT_COLOR_OPTIONS)
COLOR_THEME_VALUE_TO_LABEL = {
    "blue": "Azul",
    "green": "Verde",
    "dark-blue": "Azul oscuro",
    "purple": "Morado",
    "orange": "Naranja",
    "red": "Rojo",
    "teal": "Turquesa",
    "black": "Negro",
    "charcoal": "Carbón",
    "graphite": "Grafito",
    "slate": "Pizarra",
    "gray": "Gris",
}
COLOR_THEME_LABEL_TO_VALUE = {label: value for value, label in COLOR_THEME_VALUE_TO_LABEL.items()}
COLOR_THEME_LABEL_OPTIONS = [COLOR_THEME_VALUE_TO_LABEL[value] for value in COLOR_THEME_OPTIONS]

SURFACE_THEME_OPTIONS = list(SURFACE_COLOR_OPTIONS)
SURFACE_THEME_VALUE_TO_LABEL = {
    "default": "Predeterminado",
    "onyx": "Ónix",
    "charcoal": "Carbón",
    "graphite": "Grafito",
    "midnight": "Medianoche",
    "forest": "Bosque",
}
SURFACE_THEME_LABEL_TO_VALUE = {label: value for value, label in SURFACE_THEME_VALUE_TO_LABEL.items()}
SURFACE_THEME_LABEL_OPTIONS = [SURFACE_THEME_VALUE_TO_LABEL[value] for value in SURFACE_THEME_OPTIONS]


def normalize_appearance_label(value: str | None) -> str:
    """Return the user-facing appearance label used by settings windows."""

    return APPEARANCE_VALUE_TO_LABEL.get(str(value or DEFAULT_APPEARANCE_MODE), "Oscuro")


def normalize_appearance_value(value: str | None) -> str:
    """Return the CustomTkinter appearance value from a label or raw value."""

    return APPEARANCE_LABEL_TO_VALUE.get(str(value or DEFAULT_APPEARANCE_MODE), "dark")


def normalize_color_theme(value: str | None) -> str:
    value_text = str(value or DEFAULT_COLOR_THEME).strip()
    raw_value = COLOR_THEME_LABEL_TO_VALUE.get(value_text, value_text)
    return normalize_accent_color(raw_value)


def normalize_color_theme_label(value: str | None) -> str:
    normalized = normalize_color_theme(value)
    return COLOR_THEME_VALUE_TO_LABEL.get(normalized, COLOR_THEME_VALUE_TO_LABEL[DEFAULT_COLOR_THEME])


def normalize_surface_theme(value: str | None) -> str:
    value_text = str(value or DEFAULT_SURFACE_THEME).strip()
    raw_value = SURFACE_THEME_LABEL_TO_VALUE.get(value_text, value_text)
    return normalize_surface_color(raw_value)


def normalize_surface_theme_label(value: str | None) -> str:
    normalized = normalize_surface_theme(value)
    return SURFACE_THEME_VALUE_TO_LABEL.get(normalized, SURFACE_THEME_VALUE_TO_LABEL[DEFAULT_SURFACE_THEME])


def normalize_table_density(value: str | None) -> str:
    normalized = str(value or "Normal").strip()
    return normalized if normalized in RESULTS_DENSITY_OPTIONS else "Normal"


@dataclass(frozen=True)
class GuiPreferences:
    """Common visual preferences that any GuiCore-based tool can reuse.

    GuiCore owns the visual vocabulary. Each concrete tool still decides where to
    persist these values: ConfigCore, its own JSON file, a profile, or memory only.
    """

    appearance_mode: str = DEFAULT_APPEARANCE_MODE
    color_theme: str = DEFAULT_COLOR_THEME
    font_family: str = "Segoe UI"
    font_size: str = "Normal"
    table_density: str = "Normal"
    surface_theme: str = DEFAULT_SURFACE_THEME

    def normalized(self) -> "GuiPreferences":
        return GuiPreferences(
            appearance_mode=normalize_appearance_value(self.appearance_mode),
            color_theme=normalize_color_theme(self.color_theme),
            font_family=normalize_font_family(self.font_family),
            font_size=normalize_font_size_option(self.font_size),
            table_density=normalize_table_density(self.table_density),
            surface_theme=normalize_surface_theme(self.surface_theme),
        )

    @property
    def appearance_label(self) -> str:
        return normalize_appearance_label(self.appearance_mode)

    @property
    def color_theme_label(self) -> str:
        return normalize_color_theme_label(self.color_theme)

    @property
    def surface_theme_label(self) -> str:
        return normalize_surface_theme_label(self.surface_theme)

    def to_theme_config(self) -> ThemeConfig:
        normalized = self.normalized()
        return ThemeConfig(appearance_mode=normalized.appearance_mode, color_theme=normalized.color_theme)

    def to_font_config(self) -> FontConfig:
        normalized = self.normalized()
        return FontConfig(family=normalized.font_family, size_option=normalized.font_size)

    def to_dict(self) -> Dict[str, Any]:
        normalized = self.normalized()
        return {
            "appearance_mode": normalized.appearance_mode,
            "appearance_label": normalize_appearance_label(normalized.appearance_mode),
            "color_theme": normalized.color_theme,
            "accent_color": normalized.color_theme,
            "color_theme_label": normalize_color_theme_label(normalized.color_theme),
            "accent_color_label": normalize_color_theme_label(normalized.color_theme),
            "surface_theme": normalized.surface_theme,
            "surface_theme_label": normalize_surface_theme_label(normalized.surface_theme),
            "font_family": normalized.font_family,
            "font_size": normalized.font_size,
            "table_density": normalized.table_density,
            "table_row_height": get_results_density_row_height(normalized.table_density),
        }

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any] | None) -> "GuiPreferences":
        if not values:
            return cls()
        return cls(
            appearance_mode=str(values.get("appearance_mode") or values.get("appearance") or DEFAULT_APPEARANCE_MODE),
            color_theme=str(values.get("color_theme") or values.get("accent_color") or DEFAULT_COLOR_THEME),
            font_family=str(values.get("font_family") or "Segoe UI"),
            font_size=str(values.get("font_size") or values.get("font_size_option") or "Normal"),
            table_density=str(values.get("table_density") or values.get("density") or "Normal"),
            surface_theme=str(values.get("surface_theme") or values.get("base_color") or values.get("base_theme") or DEFAULT_SURFACE_THEME),
        ).normalized()
