from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

from .constants import DEFAULT_APPEARANCE_MODE, DEFAULT_COLOR_THEME, DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH


@dataclass(frozen=True)
class ThemeConfig:
    appearance_mode: str = DEFAULT_APPEARANCE_MODE
    color_theme: str = DEFAULT_COLOR_THEME

    def to_dict(self) -> Dict[str, Any]:
        return {
            "appearance_mode": self.appearance_mode,
            "color_theme": self.color_theme,
        }


@dataclass(frozen=True)
class WindowConfig:
    title: str
    width: int = DEFAULT_WINDOW_WIDTH
    height: int = DEFAULT_WINDOW_HEIGHT
    min_width: Optional[int] = None
    min_height: Optional[int] = None
    resizable: Tuple[bool, bool] = (True, True)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "resizable": list(self.resizable),
        }
