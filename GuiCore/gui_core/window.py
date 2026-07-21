from __future__ import annotations

from .dependencies import require_customtkinter
from .layout import calculate_center_geometry, normalize_window_size
from .models import ThemeConfig, WindowConfig
from .theme import apply_theme


def create_main_window(
    window_config: WindowConfig,
    theme_config: ThemeConfig | None = None,
):
    """Create a CustomTkinter main window using ecosystem defaults."""
    apply_theme(theme_config)
    ctk = require_customtkinter()

    window = ctk.CTk()
    width, height = normalize_window_size(window_config.width, window_config.height)

    window.title(window_config.title)
    window.geometry(f"{width}x{height}")
    window.resizable(*window_config.resizable)

    min_width = window_config.min_width or width
    min_height = window_config.min_height or height
    window.minsize(min_width, min_height)

    try:
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        window.geometry(calculate_center_geometry(screen_width, screen_height, width, height))
    except Exception:
        # NOTE: Some headless environments cannot report screen information.
        pass

    return window
