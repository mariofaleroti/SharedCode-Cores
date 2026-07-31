from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import get_control_colors, get_surface_colors
from ..styles.fonts import FontConfig
from .form_controls import (
    get_button_style_options,
    normalize_button_style,
    normalize_command_key,
)


@dataclass(frozen=True)
class CardHeaderAction:
    """Declarative action displayed in a card header."""

    text: str
    command: Callable[[], None] | None = None
    command_key: str | None = None
    style: str = "secondary"
    enabled: bool = True
    icon_text: str = ""
    width: int | None = None

    @property
    def key(self) -> str:
        return self.command_key or normalize_command_key(self.text)


class SectionCard:
    """Reusable panel with header actions and a flexible content area."""

    def __init__(
        self,
        parent: Any,
        title: str = "",
        subtitle: str = "",
        font_config: FontConfig | None = None,
        corner_radius: int | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        header_actions: Sequence[CardHeaderAction] = (),
        force_header: bool = False,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self._title_text = str(title or "")
        self._subtitle_text = str(subtitle or "")
        self._header_action_specs: dict[str, CardHeaderAction] = {}
        self.header_action_buttons: dict[str, Any] = {}

        resolved_corner_radius = (
            self.layout_profile.card_corner_radius
            if corner_radius is None
            else int(corner_radius)
        )
        self.frame = ctk.CTkFrame(
            parent,
            corner_radius=resolved_corner_radius,
        )
        self.frame.grid_columnconfigure(0, weight=1)

        self.header_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
        )
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.header_text_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent",
        )
        self.header_text_frame.grid_columnconfigure(0, weight=1)
        self.header_text_frame.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self.header_actions_frame = ctk.CTkFrame(
            self.header_frame,
            fg_color="transparent",
        )
        self.header_actions_frame.grid(
            row=0,
            column=1,
            padx=(self.layout_profile.inline_gap, 0),
            sticky="e",
        )

        self.title_label = None
        self.subtitle_label = None

        if self._title_text:
            self.title_label = ctk.CTkLabel(
                self.header_text_frame,
                text=self._title_text,
                font=self.font_config.tuple("section", "bold"),
                anchor="w",
            )
            self.title_label.grid(
                row=0,
                column=0,
                sticky="ew",
            )

        if self._subtitle_text:
            self.subtitle_label = ctk.CTkLabel(
                self.header_text_frame,
                text=self._subtitle_text,
                font=self.font_config.tuple("small"),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=760,
            )
            self.subtitle_label.grid(
                row=1,
                column=0,
                pady=(self.layout_profile.card_title_gap, 0),
                sticky="ew",
            )

        self.set_header_actions(header_actions)

        self._header_visible = bool(
            force_header
            or self._title_text
            or self._subtitle_text
            or header_actions
        )
        header_row = 0
        if self._header_visible:
            self.header_frame.grid(
                row=header_row,
                column=0,
                padx=self.layout_profile.card_inner_pad_x,
                pady=(
                    self.layout_profile.card_header_pad_top,
                    self.layout_profile.card_subtitle_gap,
                ),
                sticky="ew",
            )
            content_row = 1
        else:
            content_row = 0

        self.content_row = content_row
        self.content_frame = ctk.CTkFrame(
            self.frame,
            fg_color="transparent",
        )
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid(
            row=content_row,
            column=0,
            padx=self.layout_profile.card_inner_pad_x,
            pady=(
                self.layout_profile.card_content_pad_top,
                self.layout_profile.card_content_pad_bottom,
            ),
            sticky="nsew",
        )
        self.frame.grid_rowconfigure(content_row, weight=1)

    def _create_header_button(
        self,
        action: CardHeaderAction,
        column: int,
    ) -> Any:
        options = get_button_style_options(action.style)
        kwargs: dict[str, Any] = {
            "text": f"{action.icon_text} {action.text}".strip(),
            "command": action.command,
            "state": "normal" if action.enabled else "disabled",
            "height": self.layout_profile.control_height,
            "font": self.font_config.tuple("small"),
            **options,
        }
        if action.width is not None:
            kwargs["width"] = int(action.width)

        button = self.ctk.CTkButton(
            self.header_actions_frame,
            **kwargs,
        )
        button.grid(
            row=0,
            column=column,
            padx=(
                0 if column == 0 else self.layout_profile.inline_gap,
                0,
            ),
            sticky="e",
        )
        return button

    def set_header_actions(
        self,
        actions: Sequence[CardHeaderAction],
    ) -> None:
        for child in self.header_actions_frame.winfo_children():
            child.destroy()
        self.header_action_buttons.clear()
        self._header_action_specs.clear()

        for column, action in enumerate(actions):
            key = action.key
            self._header_action_specs[key] = action
            self.header_action_buttons[key] = self._create_header_button(
                action,
                column,
            )

    def append_header_action(
        self,
        action: CardHeaderAction,
    ) -> Any:
        key = action.key
        column = len(self.header_action_buttons)
        self._header_action_specs[key] = action
        button = self._create_header_button(action, column)
        self.header_action_buttons[key] = button
        return button

    def set_header_action_enabled(
        self,
        key: str,
        enabled: bool,
    ) -> None:
        button = self.header_action_buttons.get(key)
        if button is None:
            raise KeyError(f"Unknown card header action: {key}")
        button.configure(state="normal" if enabled else "disabled")

    def get_header_action_button(self, key: str) -> Any | None:
        return self.header_action_buttons.get(key)

    def set_title(self, title: str) -> None:
        self._title_text = str(title or "")
        if self.title_label is None:
            self.title_label = self.ctk.CTkLabel(
                self.header_text_frame,
                text=self._title_text,
                font=self.font_config.tuple("section", "bold"),
                anchor="w",
            )
            self.title_label.grid(row=0, column=0, sticky="ew")
        else:
            self.title_label.configure(text=self._title_text)

    def set_subtitle(self, subtitle: str) -> None:
        self._subtitle_text = str(subtitle or "")
        if self.subtitle_label is None:
            self.subtitle_label = self.ctk.CTkLabel(
                self.header_text_frame,
                text=self._subtitle_text,
                font=self.font_config.tuple("small"),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=760,
            )
            self.subtitle_label.grid(
                row=1,
                column=0,
                pady=(self.layout_profile.card_title_gap, 0),
                sticky="ew",
            )
        else:
            self.subtitle_label.configure(text=self._subtitle_text)

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
                self.title_label.configure(
                    font=self.font_config.tuple("section", "bold")
                )
            if self.subtitle_label is not None:
                self.subtitle_label.configure(
                    font=self.font_config.tuple("small")
                )
            for button in self.header_action_buttons.values():
                button.configure(
                    font=self.font_config.tuple("small")
                )

        surface = get_surface_colors(
            appearance_mode,
            surface_theme,
        )
        controls = get_control_colors(
            appearance_mode,
            surface_theme,
        )
        self.frame.configure(fg_color=surface["card"])
        if self.subtitle_label is not None:
            self.subtitle_label.configure(
                text_color=controls["label_text_color"]
            )

        for key, button in self.header_action_buttons.items():
            spec = self._header_action_specs[key]
            button.configure(
                **get_button_style_options(
                    normalize_button_style(spec.style),
                    color_theme,
                    surface_theme,
                    appearance_mode,
                )
            )


class CollapsibleSectionCard(SectionCard):
    """SectionCard that can hide and restore its content area."""

    TOGGLE_ACTION_KEY = "__toggle_card__"

    def __init__(
        self,
        parent: Any,
        title: str = "",
        subtitle: str = "",
        font_config: FontConfig | None = None,
        corner_radius: int | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        header_actions: Sequence[CardHeaderAction] = (),
        collapsed: bool = False,
        collapsed_summary: str = "",
        on_toggle: Callable[[bool], None] | None = None,
    ) -> None:
        self.collapsed_summary = str(collapsed_summary or "")
        self.on_toggle = on_toggle
        self._expanded_subtitle = str(subtitle or "")
        self.is_collapsed = False

        super().__init__(
            parent,
            title,
            subtitle,
            font_config,
            corner_radius,
            layout_profile,
            header_actions=header_actions,
            force_header=True,
        )

        self.toggle_button = self.append_header_action(
            CardHeaderAction(
                text="−",
                command=self.toggle,
                command_key=self.TOGGLE_ACTION_KEY,
                style="ghost",
                width=self.layout_profile.control_height,
            )
        )
        self.set_collapsed(collapsed, notify=False)

    def set_collapsed(
        self,
        collapsed: bool,
        *,
        notify: bool = True,
    ) -> None:
        new_state = bool(collapsed)
        self.is_collapsed = new_state

        if new_state:
            self.content_frame.grid_remove()
            self.frame.grid_rowconfigure(self.content_row, weight=0)
            self.toggle_button.configure(text="+")
            if self.collapsed_summary:
                self.set_subtitle(self.collapsed_summary)
        else:
            self.content_frame.grid()
            self.frame.grid_rowconfigure(self.content_row, weight=1)
            self.toggle_button.configure(text="−")
            self.set_subtitle(self._expanded_subtitle)

        if notify and callable(self.on_toggle):
            self.on_toggle(self.is_collapsed)

    def toggle(self) -> None:
        self.set_collapsed(not self.is_collapsed)

    def set_collapsed_summary(self, summary: str) -> None:
        self.collapsed_summary = str(summary or "")
        if self.is_collapsed and self.collapsed_summary:
            self.set_subtitle(self.collapsed_summary)
