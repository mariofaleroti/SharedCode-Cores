from __future__ import annotations

from .constants import MIN_WINDOW_HEIGHT, MIN_WINDOW_WIDTH


def normalize_window_size(width: int, height: int) -> tuple[int, int]:
    """Enforce minimum window dimensions for ecosystem tools."""
    return max(int(width), MIN_WINDOW_WIDTH), max(int(height), MIN_WINDOW_HEIGHT)


def calculate_center_geometry(screen_width: int, screen_height: int, width: int, height: int) -> str:
    """Return a Tk geometry string centered on a screen."""
    width, height = normalize_window_size(width, height)
    x = max((int(screen_width) - width) // 2, 0)
    y = max((int(screen_height) - height) // 2, 0)
    return f"{width}x{height}+{x}+{y}"
