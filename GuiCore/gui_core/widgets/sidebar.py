from __future__ import annotations

from typing import Any, Callable, Dict, Iterable

from ..app_config import GuiAppConfig, GuiMenuItem
from ..dependencies import require_customtkinter
from ..styles.colors import get_accent_colors, get_neutral_button_colors, get_surface_colors
from ..styles.fonts import FontConfig


class Sidebar:
    """Left navigation/control panel inspired by SmartFilter's final layout."""

    def __init__(
        self,
        parent: Any,
        app_config: GuiAppConfig,
        font_config: FontConfig | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.app_config = app_config
        self.font_config = font_config or FontConfig()
        self.actions: Dict[str, Callable[[], None]] = {}
        self.footer_buttons: Dict[str, Any] = {}
        self.footer_label = None

        self.frame = ctk.CTkFrame(parent, width=app_config.sidebar_width, corner_radius=0)
        self.frame.grid_propagate(False)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.controls_frame = ctk.CTkScrollableFrame(self.frame, fg_color="transparent")
        self.controls_frame.grid_columnconfigure(0, weight=1)

        self.footer_frame = ctk.CTkFrame(
            self.frame,
            fg_color=("gray88", "gray18"),
            corner_radius=0,
        )
        self.footer_frame.grid_columnconfigure(0, weight=1)

        self._build_header()
        self.controls_frame.grid(row=1, column=0, padx=14, pady=(8, 8), sticky="nsew")
        self._build_footer(app_config.footer_items)
        self.footer_frame.grid(row=2, column=0, sticky="sew")

    def _build_header(self) -> None:
        self.header_frame = self.ctk.CTkFrame(self.frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, padx=18, pady=(24, 8), sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = self.ctk.CTkLabel(
            self.header_frame,
            text=self.app_config.app_name,
            font=self.font_config.tuple("title", "bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew")

        subtitle_parts = []
        if self.app_config.app_subtitle:
            subtitle_parts.append(self.app_config.app_subtitle)
        if self.app_config.app_version:
            subtitle_parts.append(self.app_config.app_version)

        self.subtitle_label = self.ctk.CTkLabel(
            self.header_frame,
            text=" · ".join(subtitle_parts),
            font=self.font_config.tuple("small"),
            text_color="gray",
            anchor="w",
            justify="left",
            wraplength=max(self.app_config.sidebar_width - 42, 160),
        )
        self.subtitle_label.grid(row=1, column=0, pady=(4, 0), sticky="ew")

    def _build_footer(self, items: Iterable[GuiMenuItem]) -> None:
        label = self.ctk.CTkLabel(
            self.footer_frame,
            text="MENÚ",
            font=self.font_config.tuple("section", "bold"),
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        label.grid(row=0, column=0, padx=14, pady=(12, 6), sticky="ew")
        self.footer_label = label

        button_options = {
            "font": self.font_config.tuple("body"),
            "fg_color": ("gray75", "gray28"),
            "hover_color": ("gray68", "gray35"),
            "text_color": ("gray10", "gray95"),
            "height": 34,
            "anchor": "w",
        }

        for row, item in enumerate(items, start=1):
            button_text = f"{item.icon_text} {item.text}".strip()
            button = self.ctk.CTkButton(
                self.footer_frame,
                text=button_text,
                state="normal" if item.enabled else "disabled",
                command=lambda key=item.key: self._execute_action(key),
                **button_options,
            )
            button.grid(row=row, column=0, padx=14, pady=(0, 7), sticky="ew")
            self.footer_buttons[item.key] = button

    def _execute_action(self, key: str) -> None:
        callback = self.actions.get(key)
        if callable(callback):
            callback()

    def set_action(self, key: str, callback: Callable[[], None]) -> None:
        self.actions[key] = callback

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)


    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            self.title_label.configure(font=self.font_config.tuple("title", "bold"))
            self.subtitle_label.configure(font=self.font_config.tuple("small"))
            if self.footer_label is not None:
                self.footer_label.configure(font=self.font_config.tuple("section", "bold"))
            for button in self.footer_buttons.values():
                button.configure(font=self.font_config.tuple("body"))

        surface = get_surface_colors(appearance_mode, surface_theme)
        neutral = get_neutral_button_colors(appearance_mode, surface_theme)
        accent = get_accent_colors(color_theme)
        self.frame.configure(fg_color=surface["sidebar"])
        try:
            self.controls_frame.configure(
                fg_color=surface["sidebar"],
                scrollbar_button_color=surface["neutral"],
                scrollbar_button_hover_color=surface["neutral_hover"],
            )
        except Exception:
            self.controls_frame.configure(fg_color=surface["sidebar"])
        self.footer_frame.configure(fg_color=surface["sidebar_footer"])
        try:
            self.title_label.configure(text_color=neutral["text_color"])
            self.subtitle_label.configure(text_color=surface["border"])
            if self.footer_label is not None:
                self.footer_label.configure(text_color=neutral["text_color"])
        except Exception:
            pass
        for button in self.footer_buttons.values():
            button.configure(
                fg_color=accent["primary"],
                hover_color=accent["hover"],
                text_color="#ffffff",
            )
