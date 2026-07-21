from __future__ import annotations

from typing import Any

from ..dependencies import require_customtkinter
from ..styles.colors import get_surface_colors


class ContentPanel:
    """Main scroll-free content region used by ecosystem desktop tools."""

    def __init__(self, parent: Any) -> None:
        ctk = require_customtkinter()
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(0, weight=1)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def clear(self) -> None:
        for child in self.frame.winfo_children():
            child.destroy()

    def apply_visual_preferences(
        self,
        font_config: Any | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        surface = get_surface_colors(appearance_mode, surface_theme)
        self.frame.configure(fg_color=surface["content"])
