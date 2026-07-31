from __future__ import annotations

from typing import Any, Callable, Dict, Iterable, Sequence

from ..app_config import (
    GuiActionButton,
    GuiAppConfig,
    GuiMenuItem,
    SidebarConfig,
)
from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import get_neutral_button_colors, get_surface_colors
from ..styles.fonts import FontConfig
from .form_controls import get_button_style_options, normalize_button_style


class Sidebar:
    """Configurable sidebar with scrollable controls and fixed actions."""

    def __init__(
        self,
        parent: Any,
        app_config: GuiAppConfig,
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.app_config = app_config
        self.config: SidebarConfig = app_config.sidebar_config
        self.layout_profile = get_layout_profile(
            layout_profile
            if layout_profile is not None
            else app_config.layout_profile
        )
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )

        self.actions: Dict[str, Callable[[], None]] = {}
        self.primary_buttons: Dict[str, Any] = {}
        self.footer_buttons: Dict[str, Any] = {}
        self._primary_specs: Dict[str, GuiActionButton] = {}
        self._footer_specs: Dict[str, GuiMenuItem] = {}

        self.header_frame = None
        self.title_label = None
        self.subtitle_label = None
        self.primary_actions_frame = None
        self.primary_actions_label = None
        self.footer_frame = None
        self.footer_label = None

        self.frame = ctk.CTkFrame(
            parent,
            width=app_config.sidebar_width,
            corner_radius=0,
        )
        self.frame.grid_propagate(False)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)

        self.controls_frame = self._create_controls_frame()
        self.controls_frame.grid_columnconfigure(0, weight=1)

        if self.config.header_visible:
            self._build_header()

        self.controls_frame.grid(
            row=1,
            column=0,
            padx=self.layout_profile.sidebar_padding,
            pady=(
                self.layout_profile.sidebar_controls_pad_top,
                self.layout_profile.sidebar_controls_pad_bottom,
            ),
            sticky="nsew",
        )

        if self.config.primary_actions_visible and app_config.primary_actions:
            self._build_primary_actions(app_config.primary_actions)
            self.primary_actions_frame.grid(
                row=2,
                column=0,
                sticky="ew",
            )

        footer_items = app_config.resolved_footer_items
        if footer_items:
            self._build_footer(footer_items)
            self.footer_frame.grid(
                row=3,
                column=0,
                sticky="sew",
            )

    def _create_controls_frame(self) -> Any:
        if self.config.scrollable:
            frame = self.ctk.CTkScrollableFrame(
                self.frame,
                fg_color="transparent",
            )
            width = (
                self.config.scrollbar_width
                if self.config.scrollbar_width is not None
                else self.layout_profile.sidebar_scrollbar_width
            )
            if width is not None:
                try:
                    frame._scrollbar.configure(width=width)
                except Exception:
                    pass
            return frame

        return self.ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
            corner_radius=0,
        )

    def _build_header(self) -> None:
        self.header_frame = self.ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
        )
        self.header_frame.grid(
            row=0,
            column=0,
            padx=self.layout_profile.sidebar_header_pad_x,
            pady=(
                self.layout_profile.sidebar_header_pad_top,
                self.layout_profile.sidebar_header_pad_bottom,
            ),
            sticky="ew",
        )
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
        self.subtitle_label.grid(
            row=1,
            column=0,
            pady=(4, 0),
            sticky="ew",
        )

    def _new_fixed_frame(self) -> Any:
        return self.ctk.CTkFrame(
            self.frame,
            fg_color=("gray88", "gray18"),
            corner_radius=0,
        )

    def _configure_columns(self, frame: Any, columns: int) -> None:
        for column in range(columns):
            frame.grid_columnconfigure(
                column,
                weight=1,
                uniform="sidebar_fixed",
            )

    def _build_section_label(
        self,
        frame: Any,
        *,
        text: str,
        visible: bool,
        columns: int,
    ) -> Any | None:
        if not visible:
            return None

        label = self.ctk.CTkLabel(
            frame,
            text=text,
            font=self.font_config.tuple("small", "bold"),
            text_color=("gray35", "gray70"),
            anchor="w",
        )
        label.grid(
            row=0,
            column=0,
            columnspan=columns,
            padx=self.layout_profile.sidebar_padding,
            pady=(
                self.layout_profile.sidebar_footer_label_pad_top,
                self.layout_profile.sidebar_footer_label_pad_bottom,
            ),
            sticky="ew",
        )
        return label

    def _button_grid_options(
        self,
        *,
        index: int,
        columns: int,
        row_offset: int,
    ) -> dict[str, Any]:
        row = row_offset + (index // columns)
        column = index % columns
        left_pad = self.layout_profile.sidebar_padding
        right_pad = self.layout_profile.sidebar_padding

        if columns > 1:
            half_gap = max(1, self.layout_profile.inline_gap // 2)
            left_pad = (
                self.layout_profile.sidebar_padding
                if column == 0
                else half_gap
            )
            right_pad = (
                self.layout_profile.sidebar_padding
                if column == columns - 1
                else half_gap
            )

        return {
            "row": row,
            "column": column,
            "padx": (left_pad, right_pad),
            "pady": (
                0,
                self.layout_profile.sidebar_footer_button_gap,
            ),
            "sticky": "ew",
        }

    def _build_primary_actions(
        self,
        items: Sequence[GuiActionButton],
    ) -> None:
        self.primary_actions_frame = self._new_fixed_frame()
        columns = self.config.primary_action_columns
        self._configure_columns(self.primary_actions_frame, columns)

        self.primary_actions_label = self._build_section_label(
            self.primary_actions_frame,
            text=self.config.primary_actions_label,
            visible=self.config.primary_actions_label_visible,
            columns=columns,
        )
        row_offset = 1 if self.primary_actions_label is not None else 0

        for index, item in enumerate(items):
            button_text = f"{item.icon_text} {item.text}".strip()
            style = normalize_button_style(item.style)
            button = self.ctk.CTkButton(
                self.primary_actions_frame,
                text=button_text,
                state="normal" if item.enabled else "disabled",
                command=lambda key=item.key: self._execute_action(key),
                font=self.font_config.tuple("body", "bold"),
                height=self.layout_profile.action_height,
                anchor="center",
                **get_button_style_options(style),
            )
            button.grid(
                **self._button_grid_options(
                    index=index,
                    columns=columns,
                    row_offset=row_offset,
                )
            )
            self.primary_buttons[item.key] = button
            self._primary_specs[item.key] = item

    def _build_footer(self, items: Iterable[GuiMenuItem]) -> None:
        self.footer_frame = self._new_fixed_frame()
        columns = self.config.footer_columns
        self._configure_columns(self.footer_frame, columns)

        self.footer_label = self._build_section_label(
            self.footer_frame,
            text=self.config.footer_label,
            visible=self.config.footer_label_visible,
            columns=columns,
        )
        row_offset = 1 if self.footer_label is not None else 0
        style = normalize_button_style(self.config.footer_button_style)

        for index, item in enumerate(items):
            button_text = f"{item.icon_text} {item.text}".strip()
            button = self.ctk.CTkButton(
                self.footer_frame,
                text=button_text,
                state="normal" if item.enabled else "disabled",
                command=lambda key=item.key: self._execute_action(key),
                font=self.font_config.tuple("small"),
                height=self.layout_profile.menu_button_height,
                anchor="center" if columns > 1 else "w",
                **get_button_style_options(style),
            )
            button.grid(
                **self._button_grid_options(
                    index=index,
                    columns=columns,
                    row_offset=row_offset,
                )
            )
            self.footer_buttons[item.key] = button
            self._footer_specs[item.key] = item

    def _execute_action(self, key: str) -> None:
        callback = self.actions.get(key)
        if callable(callback):
            callback()

    def set_action(
        self,
        key: str,
        callback: Callable[[], None],
    ) -> None:
        self.actions[key] = callback

    def set_action_enabled(self, key: str, enabled: bool) -> None:
        button = self.get_action_button(key)
        if button is None:
            raise KeyError(f"Unknown sidebar action: {key}")
        button.configure(state="normal" if enabled else "disabled")

    def get_action_button(self, key: str) -> Any | None:
        return self.primary_buttons.get(key) or self.footer_buttons.get(key)

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
            if self.title_label is not None:
                self.title_label.configure(
                    font=self.font_config.tuple("title", "bold")
                )
            if self.subtitle_label is not None:
                self.subtitle_label.configure(
                    font=self.font_config.tuple("small")
                )
            if self.footer_label is not None:
                self.footer_label.configure(
                    font=self.font_config.tuple("small", "bold")
                )
            if self.primary_actions_label is not None:
                self.primary_actions_label.configure(
                    font=self.font_config.tuple("small", "bold")
                )
            for button in self.footer_buttons.values():
                button.configure(font=self.font_config.tuple("small"))
            for button in self.primary_buttons.values():
                button.configure(
                    font=self.font_config.tuple("body", "bold")
                )

        surface = get_surface_colors(
            appearance_mode,
            surface_theme,
        )
        neutral = get_neutral_button_colors(
            appearance_mode,
            surface_theme,
        )
        self.frame.configure(fg_color=surface["sidebar"])

        try:
            self.controls_frame.configure(
                fg_color=surface["sidebar"],
                scrollbar_button_color=surface["neutral"],
                scrollbar_button_hover_color=surface["neutral_hover"],
            )
        except Exception:
            self.controls_frame.configure(fg_color=surface["sidebar"])

        for frame in (
            self.primary_actions_frame,
            self.footer_frame,
        ):
            if frame is not None:
                frame.configure(fg_color=surface["sidebar_footer"])

        for label in (
            self.title_label,
            self.footer_label,
            self.primary_actions_label,
        ):
            if label is not None:
                try:
                    label.configure(text_color=neutral["text_color"])
                except Exception:
                    pass

        if self.subtitle_label is not None:
            try:
                self.subtitle_label.configure(
                    text_color=surface["border"]
                )
            except Exception:
                pass

        footer_options = get_button_style_options(
            self.config.footer_button_style,
            color_theme,
            surface_theme,
            appearance_mode,
        )
        for button in self.footer_buttons.values():
            button.configure(**footer_options)

        for key, button in self.primary_buttons.items():
            spec = self._primary_specs[key]
            options = get_button_style_options(
                spec.style,
                color_theme,
                surface_theme,
                appearance_mode,
            )
            button.configure(**options)
