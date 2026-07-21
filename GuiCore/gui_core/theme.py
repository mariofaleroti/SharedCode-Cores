from __future__ import annotations

from .dependencies import require_customtkinter
from .models import ThemeConfig
from .preferences import normalize_color_theme

APPEARANCE_MODE_MAP = {
    "Oscuro": "dark",
    "Claro": "light",
    "Sistema": "system",
    "dark": "dark",
    "light": "light",
    "system": "system",
}

# CustomTkinter ships only these built-in themes. Extra GuiCore base colors are
# applied through GuiCore-owned widgets instead of forcing a runtime CTk theme
# reload, which avoids the frozen-window behavior seen in larger apps.
CUSTOMTKINTER_COLOR_THEME_MAP = {
    "blue": "blue",
    "green": "green",
    "dark-blue": "dark-blue",
    "purple": "blue",
    "orange": "blue",
    "red": "blue",
    "teal": "blue",
    "black": "blue",
    "charcoal": "blue",
    "graphite": "blue",
    "slate": "blue",
    "gray": "blue",
}


def normalize_appearance_mode(value: str | None) -> str:
    return APPEARANCE_MODE_MAP.get(str(value or "dark"), "dark")


def normalize_customtkinter_color_theme(value: str | None) -> str:
    return CUSTOMTKINTER_COLOR_THEME_MAP.get(normalize_color_theme(value), "blue")


def apply_theme(theme_config: ThemeConfig | None = None, include_color_theme: bool = True) -> None:
    """Apply the ecosystem CustomTkinter theme.

    Use `include_color_theme=True` before the main window is built. For live
    changes in an already rendered app, use `apply_runtime_theme` so CustomTkinter
    does not try to rebuild its default theme while widgets are active.
    """

    ctk = require_customtkinter()
    config = theme_config or ThemeConfig()
    ctk.set_appearance_mode(normalize_appearance_mode(config.appearance_mode))
    if include_color_theme:
        ctk.set_default_color_theme(normalize_customtkinter_color_theme(config.color_theme))


def apply_runtime_theme(theme_config: ThemeConfig | None = None) -> None:
    """Keep runtime theme changes deliberately no-op/safe.

    In larger CustomTkinter apps, switching the global appearance mode while the
    interface is already rendered can freeze the window on some Windows systems.
    GuiCore therefore applies the global appearance only during startup. Runtime
    settings changes refresh GuiCore-owned widgets such as accents, fonts and
    table density; a changed appearance mode should be persisted by the concrete
    app and applied on the next launch.
    """

    return None
