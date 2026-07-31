from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping, Sequence

from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import get_control_colors, get_surface_colors
from ..styles.fonts import FontConfig
from .form_controls import normalize_command_key
from .state_components import get_semantic_text_color
from .tooltip import WidgetTooltip


@dataclass(frozen=True)
class MetricItem:
    """One presentation-only metric declaration."""

    key: str
    title: str
    value: Any
    semantic: str = "neutral"
    detail: str = ""
    tooltip: str = ""

    def __post_init__(self) -> None:
        if not str(self.key).strip():
            raise ValueError("MetricItem.key cannot be empty.")
        if not str(self.title).strip():
            raise ValueError("MetricItem.title cannot be empty.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": str(self.key),
            "title": str(self.title),
            "value": self.value,
            "semantic": str(self.semantic or "neutral"),
            "detail": str(self.detail or ""),
            "tooltip": str(self.tooltip or ""),
        }


def coerce_metric_items(
    values: Mapping[str, Any]
    | Iterable[MetricItem | Mapping[str, Any] | Sequence[Any]],
) -> list[MetricItem]:
    """Normalize mappings and sequences into stable metric declarations."""

    if isinstance(values, Mapping):
        if {"key", "title", "value"} & set(values.keys()):
            values = (values,)
        else:
            return [
                MetricItem(
                    key=normalize_command_key(str(title)),
                    title=str(title),
                    value=value,
                )
                for title, value in values.items()
            ]

    result: list[MetricItem] = []
    for item in values:
        if isinstance(item, MetricItem):
            result.append(item)
            continue

        if isinstance(item, Mapping):
            title = str(
                item.get("title")
                or item.get("label")
                or item.get("key")
                or ""
            )
            key = str(item.get("key") or normalize_command_key(title))
            result.append(
                MetricItem(
                    key=key,
                    title=title,
                    value=item.get("value", ""),
                    semantic=str(item.get("semantic") or "neutral"),
                    detail=str(item.get("detail") or ""),
                    tooltip=str(item.get("tooltip") or ""),
                )
            )
            continue

        if isinstance(item, Sequence) and not isinstance(
            item,
            (str, bytes),
        ):
            parts = list(item)
            if len(parts) == 2:
                title, value = parts
                result.append(
                    MetricItem(
                        key=normalize_command_key(str(title)),
                        title=str(title),
                        value=value,
                    )
                )
                continue
            if len(parts) >= 3:
                key, title, value = parts[:3]
                detail = parts[3] if len(parts) >= 4 else ""
                semantic = parts[4] if len(parts) >= 5 else "neutral"
                tooltip = parts[5] if len(parts) >= 6 else ""
                result.append(
                    MetricItem(
                        key=str(key),
                        title=str(title),
                        value=value,
                        detail=str(detail or ""),
                        semantic=str(semantic or "neutral"),
                        tooltip=str(tooltip or ""),
                    )
                )

    return result


class MetricCard:
    """Compact metric presentation with optional semantic color and tooltip."""

    def __init__(
        self,
        parent: Any,
        metric: MetricItem | Mapping[str, Any] | Sequence[Any],
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        tooltip_delay_ms: int = 800,
        tooltip_visible_ms: int = 4000,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        coerced = coerce_metric_items((metric,))
        if len(coerced) != 1:
            raise ValueError("MetricCard requires exactly one metric.")
        self.metric = coerced[0]
        self.tooltip_delay_ms = int(tooltip_delay_ms)
        self.tooltip_visible_ms = int(tooltip_visible_ms)
        self._visual_context = {
            "color_theme": "blue",
            "surface_theme": "default",
            "appearance_mode": "dark",
        }

        self.frame = ctk.CTkFrame(
            parent,
            corner_radius=self.layout_profile.card_corner_radius,
        )
        self.frame.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(
            self.frame,
            text=self.metric.title,
            font=self.font_config.tuple("small", "bold"),
            anchor="w",
        )
        self.title_label.grid(
            row=0,
            column=0,
            padx=self.layout_profile.card_inner_pad_x,
            pady=(
                self.layout_profile.card_content_pad_top,
                self.layout_profile.label_gap,
            ),
            sticky="ew",
        )

        self.value_label = ctk.CTkLabel(
            self.frame,
            text=str(self.metric.value),
            font=self.font_config.tuple("title", "bold"),
            anchor="w",
        )
        self.value_label.grid(
            row=1,
            column=0,
            padx=self.layout_profile.card_inner_pad_x,
            sticky="ew",
        )

        self.detail_label = ctk.CTkLabel(
            self.frame,
            text=str(self.metric.detail or ""),
            font=self.font_config.tuple("small"),
            anchor="w",
            justify="left",
            wraplength=260,
        )
        self.detail_label.grid(
            row=2,
            column=0,
            padx=self.layout_profile.card_inner_pad_x,
            pady=(
                self.layout_profile.label_gap,
                self.layout_profile.card_content_pad_bottom,
            ),
            sticky="ew",
        )

        self.tooltip = WidgetTooltip(
            self.frame,
            self.metric.tooltip,
            title=self.metric.title,
            delay_ms=self.tooltip_delay_ms,
            visible_ms=self.tooltip_visible_ms,
            enabled=bool(self.metric.tooltip),
            bind_descendants=True,
            font_config=self.font_config,
        )
        self.apply_visual_preferences(self.font_config)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def pack(self, *args: Any, **kwargs: Any) -> None:
        self.frame.pack(*args, **kwargs)

    def set_metric(self, metric: MetricItem) -> None:
        self.metric = metric
        self.title_label.configure(text=metric.title)
        self.value_label.configure(text=str(metric.value))
        self.detail_label.configure(text=str(metric.detail or ""))
        self.tooltip.set_text(
            metric.tooltip,
            title=metric.title,
        )
        self.tooltip.set_enabled(bool(metric.tooltip))
        self.apply_visual_preferences(
            self.font_config,
            **self._visual_context,
        )

    def update_metric(
        self,
        *,
        value: Any | None = None,
        detail: str | None = None,
        semantic: str | None = None,
        tooltip: str | None = None,
        title: str | None = None,
    ) -> MetricItem:
        updates: dict[str, Any] = {}
        if value is not None:
            updates["value"] = value
        if detail is not None:
            updates["detail"] = detail
        if semantic is not None:
            updates["semantic"] = semantic
        if tooltip is not None:
            updates["tooltip"] = tooltip
        if title is not None:
            updates["title"] = title

        updated = replace(self.metric, **updates)
        self.set_metric(updated)
        return updated

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
        surface = get_surface_colors(
            appearance_mode,
            surface_theme,
        )
        controls = get_control_colors(
            appearance_mode,
            surface_theme,
        )

        try:
            self.frame.configure(
                fg_color=surface["card_alt"],
                border_width=1,
                border_color=surface["border"],
            )
            self.title_label.configure(
                font=self.font_config.tuple("small", "bold"),
                text_color=controls["label_text_color"],
            )
            self.value_label.configure(
                font=self.font_config.tuple("title", "bold"),
                text_color=get_semantic_text_color(
                    self.metric.semantic,
                    color_theme=color_theme,
                    appearance_mode=appearance_mode,
                    surface_theme=surface_theme,
                ),
            )
            self.detail_label.configure(
                font=self.font_config.tuple("small"),
                text_color=controls["label_text_color"],
            )
        except Exception:
            pass

        self.tooltip.apply_visual_preferences(
            self.font_config,
            color_theme,
            surface_theme,
            appearance_mode,
        )

    def destroy(self) -> None:
        self.tooltip.destroy()
        try:
            self.frame.destroy()
        except Exception:
            pass


class MetricStrip:
    """Responsive row/grid of reusable MetricCard widgets."""

    def __init__(
        self,
        parent: Any,
        metrics: Mapping[str, Any]
        | Iterable[MetricItem | Mapping[str, Any] | Sequence[Any]]
        = (),
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        columns: int = 4,
        tooltip_delay_ms: int = 800,
        tooltip_visible_ms: int = 4000,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.columns = int(columns)
        if self.columns < 1 or self.columns > 8:
            raise ValueError("columns must be between 1 and 8.")

        self.tooltip_delay_ms = int(tooltip_delay_ms)
        self.tooltip_visible_ms = int(tooltip_visible_ms)
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.cards: dict[str, MetricCard] = {}
        self._metrics: list[MetricItem] = []
        self._visual_context = {
            "color_theme": "blue",
            "surface_theme": "default",
            "appearance_mode": "dark",
        }

        for column in range(self.columns):
            self.frame.grid_columnconfigure(
                column,
                weight=1,
                uniform="metric_strip",
            )
        self.set_metrics(metrics)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def pack(self, *args: Any, **kwargs: Any) -> None:
        self.frame.pack(*args, **kwargs)

    def set_metrics(
        self,
        metrics: Mapping[str, Any]
        | Iterable[MetricItem | Mapping[str, Any] | Sequence[Any]],
    ) -> None:
        normalized = coerce_metric_items(metrics)
        keys = [metric.key for metric in normalized]
        if len(keys) != len(set(keys)):
            raise ValueError("Metric keys must be unique.")

        for card in self.cards.values():
            card.destroy()
        self.cards.clear()
        self._metrics = normalized

        for index, metric in enumerate(self._metrics):
            row = index // self.columns
            column = index % self.columns
            card = MetricCard(
                self.frame,
                metric,
                self.font_config,
                self.layout_profile,
                tooltip_delay_ms=self.tooltip_delay_ms,
                tooltip_visible_ms=self.tooltip_visible_ms,
            )
            card.grid(
                row=row,
                column=column,
                padx=(
                    0 if column == 0 else self.layout_profile.inline_gap // 2,
                    0
                    if column == self.columns - 1
                    else self.layout_profile.inline_gap // 2,
                ),
                pady=(
                    0 if row == 0 else self.layout_profile.widget_gap // 2,
                    self.layout_profile.widget_gap // 2,
                ),
                sticky="nsew",
            )
            self.cards[metric.key] = card

        self.apply_visual_preferences(
            self.font_config,
            **self._visual_context,
        )

    def get_metric_card(self, key: str) -> MetricCard | None:
        return self.cards.get(str(key))

    def update_metric(
        self,
        key: str,
        **updates: Any,
    ) -> MetricItem:
        card = self.cards.get(str(key))
        if card is None:
            raise KeyError(f"Unknown metric: {key}")

        updated = card.update_metric(**updates)
        self._metrics = [
            updated if item.key == updated.key else item
            for item in self._metrics
        ]
        return updated

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
        try:
            self.frame.configure(fg_color="transparent")
        except Exception:
            pass

        for card in self.cards.values():
            card.apply_visual_preferences(
                self.font_config,
                color_theme,
                surface_theme,
                appearance_mode,
            )

    def destroy(self) -> None:
        for card in self.cards.values():
            card.destroy()
        self.cards.clear()
        try:
            self.frame.destroy()
        except Exception:
            pass
