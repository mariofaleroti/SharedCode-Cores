from .secondary_window import (
    SecondaryWindow,
    SecondaryWindowConfig,
    calculate_child_geometry,
    normalize_secondary_window_size,
)
from .settings_window import SettingsWindow, show_settings_window

__all__ = [
    "SecondaryWindow",
    "SecondaryWindowConfig",
    "SettingsWindow",
    "calculate_child_geometry",
    "normalize_secondary_window_size",
    "show_settings_window",
    "WINDOW_ICON_FALLBACK_PATH_ATTR",
    "WINDOW_ICON_IMAGE_ATTR",
    "WINDOW_ICON_PATH_ATTR",
    "WindowIconResult",
    "apply_window_icon",
    "coerce_icon_path",
    "get_window_icon_metadata",
    "resolve_window_icon_path",
    "set_window_icon_metadata",
]

from .window_icon import (
    WINDOW_ICON_FALLBACK_PATH_ATTR,
    WINDOW_ICON_IMAGE_ATTR,
    WINDOW_ICON_PATH_ATTR,
    WindowIconResult,
    apply_window_icon,
    coerce_icon_path,
    get_window_icon_metadata,
    resolve_window_icon_path,
    set_window_icon_metadata,
)
