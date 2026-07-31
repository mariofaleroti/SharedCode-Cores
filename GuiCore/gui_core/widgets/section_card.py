from __future__ import annotations

from typing import Any

from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import get_surface_colors
from ..styles.fonts import FontConfig


class SectionCard:
    """Reusable rounded panel with an optional title/subtitle and a content area."""

    def __init__(
        self,
        parent: Any,
        title: str = "",
        subtitle: str = "",
        font_config: FontConfig | None = None,
        corner_radius: int | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        resolved_corner_radius = (
            self.layout_profile.card_corner_radius
            if corner_radius is None
            else int(corner_radius)
        )
        self.frame = ctk.CTkFrame(parent, corner_radius=resolved_corner_radius)
        self.frame.grid_columnconfigure(0, weight=1)
        self.content_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.content_frame.grid_columnconfigure(0, weight=1)

        row = 0
        self.title_label = None
        self.subtitle_label = None

        if title:
            self.title_label = ctk.CTkLabel(
                self.frame,
                text=title,
                font=self.font_config.tuple("section", "bold"),
                anchor="w",
            )
            self.title_label.grid(
                row=row,
                column=0,
                padx=self.layout_profile.card_inner_pad_x,
                pady=(
                    self.layout_profile.card_header_pad_top,
                    self.layout_profile.card_title_gap,
                ),
                sticky="ew",
            )
            row += 1

        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self.frame,
                text=subtitle,
                font=self.font_config.tuple("small"),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=760,
            )
            self.subtitle_label.grid(
                row=row,
                column=0,
                padx=self.layout_profile.card_inner_pad_x,
                pady=(0, self.layout_profile.card_subtitle_gap),
                sticky="ew",
            )
            row += 1

        self.content_frame.grid(
            row=row,
            column=0,
            padx=self.layout_profile.card_inner_pad_x,
            pady=(
                self.layout_profile.card_content_pad_top,
                self.layout_profile.card_content_pad_bottom,
            ),
            sticky="nsew",
        )
        self.frame.grid_rowconfigure(row, weight=1)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def pack(self, *args: Any, **kwargs: Any) -> None:
        self.frame.pack(*args, **kwargs)

    def hide(self) -> None:
        self.frame.grid_remove()

    def show(self) -> None:
        self.frame.grid()

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            if self.title_label is not None:
                self.title_label.configure(font=self.font_config.tuple("section", "bold"))
            if self.subtitle_label is not None:
                self.subtitle_label.configure(font=self.font_config.tuple("small"))
        surface = get_surface_colors(appearance_mode, surface_theme)
        self.frame.configure(fg_color=surface["card"])
