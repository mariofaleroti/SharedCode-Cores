from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import (
    get_accent_colors,
    get_control_colors,
    get_surface_colors,
)
from ..styles.fonts import FontConfig
from .form_controls import get_button_style_options


VALID_STATE_KINDS = {
    "empty",
    "loading",
    "error",
    "ready",
    "info",
    "warning",
}


def normalize_state_kind(value: str | None) -> str:
    normalized = str(value or "empty").strip().lower()
    return normalized if normalized in VALID_STATE_KINDS else "empty"


@dataclass(frozen=True)
class KeyValueItem:
    """One display-only field/value pair for status summaries."""

    field: str
    value: Any
    semantic: str = "neutral"

    def to_dict(self) -> dict[str, Any]:
        return {
            "field": str(self.field),
            "value": self.value,
            "semantic": str(self.semantic or "neutral"),
        }


def coerce_key_value_items(
    values: Mapping[str, Any]
    | Iterable[KeyValueItem | Mapping[str, Any] | Sequence[Any]],
) -> list[KeyValueItem]:
    """Normalize mapping and sequence inputs into stable status rows."""

    if isinstance(values, Mapping):
        return [
            KeyValueItem(str(field), value)
            for field, value in values.items()
        ]

    result: list[KeyValueItem] = []
    for item in values:
        if isinstance(item, KeyValueItem):
            result.append(item)
            continue
        if isinstance(item, Mapping):
            field = item.get("field", item.get("key", ""))
            value = item.get("value", "")
            semantic = item.get("semantic", "neutral")
            if str(field).strip():
                result.append(
                    KeyValueItem(
                        str(field),
                        value,
                        str(semantic or "neutral"),
                    )
                )
            continue
        if isinstance(item, Sequence) and not isinstance(
            item,
            (str, bytes),
        ):
            parts = list(item)
            if len(parts) >= 2 and str(parts[0]).strip():
                semantic = parts[2] if len(parts) >= 3 else "neutral"
                result.append(
                    KeyValueItem(
                        str(parts[0]),
                        parts[1],
                        str(semantic or "neutral"),
                    )
                )
    return result


def get_semantic_text_color(
    semantic: str | None,
    *,
    color_theme: str | None = "blue",
    appearance_mode: str | None = "dark",
    surface_theme: str | None = "default",
) -> Any:
    normalized = str(semantic or "neutral").strip().lower()
    controls = get_control_colors(appearance_mode, surface_theme)
    accent = get_accent_colors(color_theme)

    if normalized in {"accent", "info"}:
        return accent["primary"]
    if normalized in {"success", "ready", "ok"}:
        return ("#1f7a36", "#4caf50")
    if normalized in {"warning", "attention"}:
        return ("#a65f00", "#ffb74d")
    if normalized in {"danger", "error", "failed"}:
        return ("#b3261e", "#ef5350")
    return controls["text_color"]


class KeyValueTable:
    """Compact field/value status view without business semantics."""

    def __init__(
        self,
        parent: Any,
        items: Mapping[str, Any]
        | Iterable[KeyValueItem | Mapping[str, Any] | Sequence[Any]]
        = (),
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        field_width: int | None = None,
        row_gap: int | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.field_width = field_width
        self.row_gap = (
            self.layout_profile.widget_gap
            if row_gap is None
            else max(0, int(row_gap))
        )
        self.frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        self.frame.grid_columnconfigure(1, weight=1)
        self._items: list[KeyValueItem] = []
        self._row_widgets: list[tuple[Any, Any]] = []
        self._visual_context = {
            "color_theme": "blue",
            "surface_theme": "default",
            "appearance_mode": "dark",
        }
        self.set_items(items)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def set_items(
        self,
        items: Mapping[str, Any]
        | Iterable[KeyValueItem | Mapping[str, Any] | Sequence[Any]],
    ) -> None:
        self._items = coerce_key_value_items(items)
        self._rebuild_rows()

    def clear(self) -> None:
        self.set_items(())

    def _rebuild_rows(self) -> None:
        for field_label, value_label in self._row_widgets:
            field_label.destroy()
            value_label.destroy()
        self._row_widgets.clear()

        for row, item in enumerate(self._items):
            field_kwargs: dict[str, Any] = {
                "text": item.field,
                "font": self.font_config.tuple("small", "bold"),
                "anchor": "w",
            }
            if self.field_width is not None:
                field_kwargs["width"] = int(self.field_width)

            field_label = self.ctk.CTkLabel(
                self.frame,
                **field_kwargs,
            )
            field_label.grid(
                row=row,
                column=0,
                padx=(0, self.layout_profile.inline_gap),
                pady=(0, self.row_gap),
                sticky="w",
            )

            value_label = self.ctk.CTkLabel(
                self.frame,
                text=str(item.value),
                font=self.font_config.tuple("body"),
                anchor="w",
                justify="left",
            )
            value_label.grid(
                row=row,
                column=1,
                pady=(0, self.row_gap),
                sticky="ew",
            )
            self._row_widgets.append((field_label, value_label))

        self.apply_visual_preferences(
            self.font_config,
            **self._visual_context,
        )

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
        self._visual_context = {
            "color_theme": color_theme or "blue",
            "surface_theme": surface_theme or "default",
            "appearance_mode": appearance_mode or "dark",
        }
        controls = get_control_colors(
            appearance_mode,
            surface_theme,
        )
        self.frame.configure(fg_color="transparent")

        for item, widgets in zip(self._items, self._row_widgets):
            field_label, value_label = widgets
            field_label.configure(
                font=self.font_config.tuple("small", "bold"),
                text_color=controls["label_text_color"],
            )
            value_label.configure(
                font=self.font_config.tuple("body"),
                text_color=get_semantic_text_color(
                    item.semantic,
                    color_theme=color_theme,
                    appearance_mode=appearance_mode,
                    surface_theme=surface_theme,
                ),
            )


class EmptyState:
    """Reusable empty/loading/error/ready state with an optional action."""

    def __init__(
        self,
        parent: Any,
        title: str,
        description: str = "",
        *,
        state: str = "empty",
        action_text: str = "",
        action_command: Callable[[], None] | None = None,
        action_style: str = "secondary",
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.state = normalize_state_kind(state)
        self.action_style = action_style

        self.frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        self.frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.frame,
            text=title,
            font=self.font_config.tuple("section", "bold"),
            anchor="center",
        )
        self.title_label.grid(
            row=0,
            column=0,
            pady=(0, self.layout_profile.label_gap),
            sticky="ew",
        )

        self.description_label = ctk.CTkLabel(
            self.frame,
            text=description,
            font=self.font_config.tuple("body"),
            text_color="gray",
            anchor="center",
            justify="center",
            wraplength=620,
        )
        self.description_label.grid(
            row=1,
            column=0,
            pady=(0, self.layout_profile.widget_gap),
            sticky="ew",
        )

        self.action_button = None
        if action_text:
            self.action_button = ctk.CTkButton(
                self.frame,
                text=action_text,
                command=action_command,
                height=self.layout_profile.action_height,
                font=self.font_config.tuple("body", "bold"),
                **get_button_style_options(action_style),
            )
            self.action_button.grid(
                row=2,
                column=0,
                padx=80,
                sticky="ew",
            )

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def set_state(
        self,
        state: str,
        *,
        title: str | None = None,
        description: str | None = None,
    ) -> None:
        self.state = normalize_state_kind(state)
        if title is not None:
            self.title_label.configure(text=str(title))
        if description is not None:
            self.description_label.configure(text=str(description))

    def set_action_enabled(self, enabled: bool) -> None:
        if self.action_button is not None:
            self.action_button.configure(
                state="normal" if enabled else "disabled"
            )

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
        controls = get_control_colors(
            appearance_mode,
            surface_theme,
        )
        self.title_label.configure(
            font=self.font_config.tuple("section", "bold"),
            text_color=get_semantic_text_color(
                self.state,
                color_theme=color_theme,
                appearance_mode=appearance_mode,
                surface_theme=surface_theme,
            ),
        )
        self.description_label.configure(
            font=self.font_config.tuple("body"),
            text_color=controls["label_text_color"],
        )
        if self.action_button is not None:
            self.action_button.configure(
                font=self.font_config.tuple("body", "bold"),
                **get_button_style_options(
                    self.action_style,
                    color_theme,
                    surface_theme,
                    appearance_mode,
                ),
            )
