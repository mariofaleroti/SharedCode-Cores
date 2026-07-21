from __future__ import annotations

from typing import Any

from ..dependencies import require_customtkinter
from ..styles.fonts import FontConfig


class StatusBar:
    """Small footer status line for general application state."""

    def __init__(self, parent: Any, font_config: FontConfig | None = None) -> None:
        ctk = require_customtkinter()
        self.font_config = font_config or FontConfig()
        self.frame = ctk.CTkFrame(parent, corner_radius=0, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(self.frame, text="Listo", font=self.font_config.tuple("small"), text_color="gray", anchor="w")
        self.label.grid(row=0, column=0, padx=20, pady=(4, 8), sticky="ew")

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def set_text(self, text: str) -> None:
        self.label.configure(text=text)

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            self.label.configure(font=self.font_config.tuple("small"))
