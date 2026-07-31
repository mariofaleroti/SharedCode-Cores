from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping, Sequence

from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import get_accent_colors, get_control_colors, get_neutral_button_colors, get_surface_colors
from ..styles.fonts import FontConfig

VALID_BUTTON_STYLES = {"primary", "secondary", "danger", "ghost"}
VALID_PICKER_MODES = {"folder", "file", "save_file"}


@dataclass(frozen=True)
class ChoiceOption:
    """Declarative option for combo-like controls.

    `label` is what the user sees. `value` is the stable value a tool can use in
    its own logic. GuiCore does not interpret the value.
    """

    label: str
    value: Any | None = None

    @property
    def resolved_value(self) -> Any:
        return self.label if self.value is None else self.value

    def to_dict(self) -> dict[str, Any]:
        return {"label": self.label, "value": self.resolved_value}


@dataclass(frozen=True)
class ButtonSpec:
    """Declarative button contract for sidebar/action areas."""

    text: str
    command_key: str | None = None
    style: str = "primary"
    enabled: bool = True

    @property
    def key(self) -> str:
        return self.command_key or normalize_command_key(self.text)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "command_key": self.key,
            "style": normalize_button_style(self.style),
            "enabled": self.enabled,
        }


def normalize_command_key(text: str | None) -> str:
    value = str(text or "").lower().strip().replace(" ", "_").replace("-", "_")
    return "_".join(part for part in value.split("_") if part) or "action"


def normalize_button_style(style: str | None) -> str:
    value = str(style or "primary").lower().strip()
    if value not in VALID_BUTTON_STYLES:
        return "primary"
    return value


def normalize_picker_mode(mode: str | None) -> str:
    value = str(mode or "folder").lower().strip().replace("-", "_")
    if value not in VALID_PICKER_MODES:
        return "folder"
    return value


def resolve_control_dimension(
    value: int | None,
    fallback: int,
    *,
    field_name: str = "dimension",
) -> int:
    """Resolve one optional positive control dimension."""

    resolved = int(fallback if value is None else value)
    if resolved <= 0:
        raise ValueError(f"{field_name} must be greater than zero.")
    return resolved


def resolve_control_gap(
    value: int | None,
    fallback: int,
    *,
    field_name: str = "gap",
) -> int:
    """Resolve one optional non-negative control spacing value."""

    resolved = int(fallback if value is None else value)
    if resolved < 0:
        raise ValueError(f"{field_name} cannot be negative.")
    return resolved


def normalize_control_state(enabled: bool = True) -> str:
    return "normal" if bool(enabled) else "disabled"


def coerce_choice_options(values: Iterable[str | ChoiceOption | Mapping[str, Any]]) -> list[ChoiceOption]:
    """Normalize combo values while keeping display labels stable and unique."""

    options: list[ChoiceOption] = []
    seen: set[str] = set()

    for item in values:
        if isinstance(item, ChoiceOption):
            option = item
        elif isinstance(item, Mapping):
            option = ChoiceOption(label=str(item.get("label") or item.get("text") or item.get("value") or ""), value=item.get("value"))
        else:
            option = ChoiceOption(label=str(item))

        label = option.label.strip()
        if not label or label in seen:
            continue
        seen.add(label)
        options.append(ChoiceOption(label=label, value=option.resolved_value))

    return options


def get_choice_labels(values: Iterable[str | ChoiceOption | Mapping[str, Any]]) -> list[str]:
    return [option.label for option in coerce_choice_options(values)]


def get_button_style_options(
    style: str | None = "primary",
    color_theme: str | None = "blue",
    surface_theme: str | None = "default",
    appearance_mode: str | None = "dark",
) -> dict[str, Any]:
    """Return CustomTkinter-compatible visual options for a named button style."""

    normalized = normalize_button_style(style)
    if normalized == "primary":
        accent = get_accent_colors(color_theme)
        return {
            "fg_color": accent["primary"],
            "hover_color": accent["hover"],
            "text_color": "#ffffff",
        }
    if normalized == "secondary":
        neutral = get_neutral_button_colors(appearance_mode, surface_theme)
        return {
            "fg_color": neutral["fg_color"],
            "hover_color": neutral["hover_color"],
            "text_color": neutral["text_color"],
        }
    if normalized == "danger":
        return {
            "fg_color": ("#b3261e", "#b3261e"),
            "hover_color": ("#8c1d18", "#8c1d18"),
            "text_color": "#ffffff",
        }
    if normalized == "ghost":
        neutral = get_neutral_button_colors(appearance_mode, surface_theme)
        return {
            "fg_color": "transparent",
            "hover_color": neutral["hover_color"],
            "text_color": neutral["text_color"],
            "border_width": 1,
            "border_color": neutral["border_color"],
        }
    return {}


def apply_standard_control_colors(
    control: Any,
    appearance_mode: str | None = "dark",
    surface_theme: str | None = "default",
    *,
    include_dropdown: bool = False,
) -> None:
    """Apply the selected base palette to a CTk input-like control."""

    colors = get_control_colors(appearance_mode, surface_theme)
    options: dict[str, Any] = {
        "fg_color": colors["fg_color"],
        "border_color": colors["border_color"],
        "text_color": colors["text_color"],
    }
    if include_dropdown:
        options.update(
            {
                "button_color": colors["fg_color"],
                "button_hover_color": colors["hover_color"],
                "dropdown_fg_color": colors["dropdown_fg_color"],
                "dropdown_hover_color": colors["dropdown_hover_color"],
                "dropdown_text_color": colors["text_color"],
            }
        )
    else:
        options["placeholder_text_color"] = colors["placeholder_text_color"]
    try:
        control.configure(**options)
    except Exception:
        # Older CustomTkinter versions may not support every option. Apply the
        # minimum safe subset instead of failing the whole UI refresh.
        safe_options = {key: value for key, value in options.items() if key in {"fg_color", "border_color", "text_color"}}
        try:
            control.configure(**safe_options)
        except Exception:
            pass


class SidebarFormSection:
    """Reusable sidebar section for tool-specific controls.

    The section owns only layout and visual consistency. Every tool decides what
    the controls mean and which callbacks they execute.
    """

    def __init__(
        self,
        parent: Any,
        title: str,
        subtitle: str = "",
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.frame = ctk.CTkFrame(parent, fg_color="transparent", corner_radius=10)
        self.frame.grid_columnconfigure(0, weight=1)
        self._next_row = 0
        self._widgets: list[Any] = []
        self._last_font_config: FontConfig | None = self.font_config
        self._last_color_theme: str | None = None
        self._last_surface_theme: str | None = None
        self._last_appearance_mode: str | None = None

        self.title_label = ctk.CTkLabel(
            self.frame,
            text=title,
            font=self.font_config.tuple("section", "bold"),
            anchor="w",
        )
        self.title_label.grid(
            row=self._next_row,
            column=0,
            padx=2,
            pady=(
                self.layout_profile.section_title_pad_top,
                self.layout_profile.section_title_pad_bottom,
            ),
            sticky="ew",
        )
        self._next_row += 1

        self.subtitle_label = None
        if subtitle:
            self.subtitle_label = ctk.CTkLabel(
                self.frame,
                text=subtitle,
                font=self.font_config.tuple("small"),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=210,
            )
            self.subtitle_label.grid(
                row=self._next_row,
                column=0,
                padx=2,
                pady=(0, self.layout_profile.section_subtitle_pad_bottom),
                sticky="ew",
            )
            self._next_row += 1

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def add_widget(
        self,
        widget: Any,
        pady: tuple[int, int] | None = None,
        sticky: str = "ew",
    ) -> Any:
        resolved_pady = pady or (0, self.layout_profile.widget_gap)
        widget.grid(
            row=self._next_row,
            column=0,
            pady=resolved_pady,
            sticky=sticky,
        )
        self._next_row += 1
        self._widgets.append(widget)
        # A section can be registered in GuiAppWindow before the app adds its
        # controls. Keep the last visual preferences and apply them to every
        # new child immediately, so controls created after startup do not fall
        # back to CustomTkinter/default blue until the next manual refresh.
        self._apply_visual_preferences_to_child(widget)
        return widget

    def _apply_visual_preferences_to_child(self, widget: Any) -> None:
        apply_method = getattr(widget, "apply_visual_preferences", None)
        if not callable(apply_method):
            return
        try:
            apply_method(
                font_config=self._last_font_config or self.font_config,
                color_theme=self._last_color_theme,
                surface_theme=self._last_surface_theme,
                appearance_mode=self._last_appearance_mode,
            )
        except TypeError:
            try:
                apply_method(font_config=self._last_font_config or self.font_config, color_theme=self._last_color_theme)
            except Exception:
                pass
        except Exception:
            pass

    def add_labeled_entry(self, label: str, **kwargs: Any) -> "LabeledEntry":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(LabeledEntry(self.frame, label, font_config=self.font_config, **kwargs))

    def add_labeled_combo(self, label: str, values: Iterable[str | ChoiceOption | Mapping[str, Any]], **kwargs: Any) -> "LabeledComboBox":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(LabeledComboBox(self.frame, label, values, font_config=self.font_config, **kwargs))

    def add_path_picker(self, label: str, **kwargs: Any) -> "PathPicker":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(PathPicker(self.frame, label, font_config=self.font_config, **kwargs))

    def add_labeled_combo_action(
        self,
        label: str,
        values: Iterable[str | ChoiceOption | Mapping[str, Any]],
        **kwargs: Any,
    ) -> "LabeledComboAction":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(
            LabeledComboAction(
                self.frame,
                label,
                values,
                font_config=self.font_config,
                **kwargs,
            )
        )

    def add_checkbox(self, text: str, **kwargs: Any) -> "LabeledCheckBox":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(LabeledCheckBox(self.frame, text, font_config=self.font_config, **kwargs))

    def add_switch(self, text: str, **kwargs: Any) -> "LabeledSwitch":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(LabeledSwitch(self.frame, text, font_config=self.font_config, **kwargs))

    def add_action_button(self, text: str, command: Callable[[], None] | None = None, **kwargs: Any) -> "ActionButton":
        kwargs.setdefault("layout_profile", self.layout_profile)
        return self.add_widget(ActionButton(self.frame, text, command=command, font_config=self.font_config, **kwargs))

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            self.title_label.configure(font=self.font_config.tuple("section", "bold"))
            if self.subtitle_label is not None:
                self.subtitle_label.configure(font=self.font_config.tuple("small"))
        self._last_font_config = self.font_config
        self._last_color_theme = color_theme
        self._last_surface_theme = surface_theme
        self._last_appearance_mode = appearance_mode
        surface = get_surface_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color=surface["sidebar"])
            self.title_label.configure(text_color=get_control_colors(appearance_mode, surface_theme)["text_color"])
            if self.subtitle_label is not None:
                self.subtitle_label.configure(text_color=get_control_colors(appearance_mode, surface_theme)["label_text_color"])
        except Exception:
            pass
        for widget in list(self._widgets):
            self._apply_visual_preferences_to_child(widget)


class LabeledEntry:
    """Label + entry control with reusable density overrides."""

    def __init__(
        self,
        parent: Any,
        label: str,
        placeholder: str = "",
        value: str = "",
        font_config: FontConfig | None = None,
        enabled: bool = True,
        show: str | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        label_visible: bool = True,
        height: int | None = None,
        width: int | None = None,
        font_role: str = "body",
        label_font_role: str = "small",
        label_weight: str | None = "bold",
        label_gap: int | None = None,
        on_change: Callable[[str], None] | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        self.label_font_role = str(label_font_role or "small")
        self.label_weight = label_weight
        self.on_change = on_change

        control_height = resolve_control_dimension(
            height,
            self.layout_profile.control_height,
            field_name="height",
        )
        control_width = (
            None
            if width is None
            else resolve_control_dimension(width, width, field_name="width")
        )
        resolved_label_gap = resolve_control_gap(
            label_gap,
            self.layout_profile.label_gap,
            field_name="label_gap",
        )

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = None
        entry_row = 0
        if label_visible and str(label).strip():
            self.label = ctk.CTkLabel(
                self.frame,
                text=label,
                font=self.font_config.tuple(
                    self.label_font_role,
                    self.label_weight,
                ),
                text_color=("gray30", "gray72"),
                anchor="w",
            )
            self.label.grid(
                row=0,
                column=0,
                padx=2,
                pady=(0, resolved_label_gap),
                sticky="ew",
            )
            entry_row = 1

        entry_kwargs: dict[str, Any] = {
            "placeholder_text": placeholder,
            "font": self.font_config.tuple(self.font_role),
            "state": normalize_control_state(enabled),
            "height": control_height,
        }
        if control_width is not None:
            entry_kwargs["width"] = control_width
        if show:
            entry_kwargs["show"] = show

        self.entry = ctk.CTkEntry(self.frame, **entry_kwargs)
        self.entry.grid(row=entry_row, column=0, sticky="ew")
        if callable(self.on_change):
            self.entry.bind(
                "<KeyRelease>",
                lambda _event: self.on_change(self.get_value()),
                add="+",
            )
        if value:
            self.set_value(value)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def get_value(self) -> str:
        return self.entry.get()

    def set_value(self, value: str) -> None:
        previous_state = str(self.entry.cget("state"))
        if previous_state == "disabled":
            self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        if previous_state == "disabled":
            self.entry.configure(state="disabled")

    def clear(self) -> None:
        self.set_value("")

    def set_enabled(self, enabled: bool) -> None:
        self.entry.configure(state=normalize_control_state(enabled))

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            if self.label is not None:
                self.label.configure(
                    font=self.font_config.tuple(
                        self.label_font_role,
                        self.label_weight,
                    )
                )
            self.entry.configure(
                font=self.font_config.tuple(self.font_role)
            )
        colors = get_control_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color="transparent")
            if self.label is not None:
                self.label.configure(
                    text_color=colors["label_text_color"]
                )
            apply_standard_control_colors(
                self.entry,
                appearance_mode,
                surface_theme,
            )
        except Exception:
            pass

class LabeledComboBox:
    """Label + combo control with stable values and density overrides."""

    def __init__(
        self,
        parent: Any,
        label: str,
        values: Iterable[str | ChoiceOption | Mapping[str, Any]],
        default_value: str | None = None,
        font_config: FontConfig | None = None,
        enabled: bool = True,
        command: Callable[[str], None] | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        label_visible: bool = True,
        height: int | None = None,
        width: int | None = None,
        font_role: str = "body",
        label_font_role: str = "small",
        label_weight: str | None = "bold",
        label_gap: int | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        self.label_font_role = str(label_font_role or "small")
        self.label_weight = label_weight
        self.options = coerce_choice_options(values)
        labels = [option.label for option in self.options]
        self._value_by_label = {
            option.label: option.resolved_value
            for option in self.options
        }

        control_height = resolve_control_dimension(
            height,
            self.layout_profile.control_height,
            field_name="height",
        )
        control_width = (
            None
            if width is None
            else resolve_control_dimension(width, width, field_name="width")
        )
        resolved_label_gap = resolve_control_gap(
            label_gap,
            self.layout_profile.label_gap,
            field_name="label_gap",
        )

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = None
        combo_row = 0
        if label_visible and str(label).strip():
            self.label = ctk.CTkLabel(
                self.frame,
                text=label,
                font=self.font_config.tuple(
                    self.label_font_role,
                    self.label_weight,
                ),
                text_color=("gray30", "gray72"),
                anchor="w",
            )
            self.label.grid(
                row=0,
                column=0,
                padx=2,
                pady=(0, resolved_label_gap),
                sticky="ew",
            )
            combo_row = 1

        combo_kwargs: dict[str, Any] = {
            "values": labels,
            "font": self.font_config.tuple(self.font_role),
            "dropdown_font": self.font_config.tuple(self.font_role),
            "state": normalize_control_state(enabled),
            "command": command,
            "height": control_height,
        }
        if control_width is not None:
            combo_kwargs["width"] = control_width

        self.combo = ctk.CTkComboBox(self.frame, **combo_kwargs)
        self.combo.grid(row=combo_row, column=0, sticky="ew")

        if default_value and default_value in labels:
            self.combo.set(default_value)
        elif labels:
            self.combo.set(labels[0])

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def get_label(self) -> str:
        return self.combo.get()

    def get_value(self) -> Any:
        label = self.get_label()
        return self._value_by_label.get(label, label)

    def set_value(self, value: str) -> None:
        self.combo.set(str(value))

    def set_values(
        self,
        values: Iterable[str | ChoiceOption | Mapping[str, Any]],
        default_value: str | None = None,
    ) -> None:
        self.options = coerce_choice_options(values)
        labels = [option.label for option in self.options]
        self._value_by_label = {
            option.label: option.resolved_value
            for option in self.options
        }
        current = self.combo.get()
        self.combo.configure(values=labels)
        if default_value and default_value in labels:
            self.combo.set(default_value)
        elif current in labels:
            self.combo.set(current)
        elif labels:
            self.combo.set(labels[0])
        else:
            self.combo.set("")

    def set_enabled(self, enabled: bool) -> None:
        self.combo.configure(state=normalize_control_state(enabled))

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            if self.label is not None:
                self.label.configure(
                    font=self.font_config.tuple(
                        self.label_font_role,
                        self.label_weight,
                    )
                )
            self.combo.configure(
                font=self.font_config.tuple(self.font_role),
                dropdown_font=self.font_config.tuple(self.font_role),
            )
        colors = get_control_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color="transparent")
            if self.label is not None:
                self.label.configure(
                    text_color=colors["label_text_color"]
                )
            apply_standard_control_colors(
                self.combo,
                appearance_mode,
                surface_theme,
                include_dropdown=True,
            )
        except Exception:
            pass

class PathPicker:
    """Entry + browse button with reusable compact geometry."""

    def __init__(
        self,
        parent: Any,
        label: str,
        placeholder: str = "Seleccionar ruta...",
        value: str = "",
        mode: str = "folder",
        button_text: str = "...",
        font_config: FontConfig | None = None,
        enabled: bool = True,
        filetypes: Sequence[tuple[str, str]] | None = None,
        title: str | None = None,
        on_change: Callable[[str], None] | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        label_visible: bool = True,
        height: int | None = None,
        width: int | None = None,
        button_width: int | None = None,
        gap: int | None = None,
        font_role: str = "body",
        button_font_role: str | None = None,
        label_font_role: str = "small",
        label_weight: str | None = "bold",
        label_gap: int | None = None,
        button_style: str = "primary",
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        self.button_font_role = str(button_font_role or self.font_role)
        self.label_font_role = str(label_font_role or "small")
        self.label_weight = label_weight
        self.button_style = normalize_button_style(button_style)
        self.mode = normalize_picker_mode(mode)
        self.filetypes = tuple(
            filetypes or (("Todos los archivos", "*.*"),)
        )
        self.dialog_title = title or (
            "Seleccionar carpeta"
            if self.mode == "folder"
            else "Seleccionar archivo"
        )
        self.on_change = on_change

        control_height = resolve_control_dimension(
            height,
            self.layout_profile.control_height,
            field_name="height",
        )
        auxiliary_width = resolve_control_dimension(
            button_width,
            self.layout_profile.picker_button_width,
            field_name="button_width",
        )
        auxiliary_gap = resolve_control_gap(
            gap,
            self.layout_profile.inline_gap,
            field_name="gap",
        )
        resolved_label_gap = resolve_control_gap(
            label_gap,
            self.layout_profile.label_gap,
            field_name="label_gap",
        )

        entry_width = None
        if width is not None:
            total_width = resolve_control_dimension(
                width,
                width,
                field_name="width",
            )
            entry_width = total_width - auxiliary_width - auxiliary_gap
            if entry_width <= 0:
                raise ValueError(
                    "width must be greater than button_width + gap."
                )

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = None
        control_row = 0
        if label_visible and str(label).strip():
            self.label = ctk.CTkLabel(
                self.frame,
                text=label,
                font=self.font_config.tuple(
                    self.label_font_role,
                    self.label_weight,
                ),
                text_color=("gray30", "gray72"),
                anchor="w",
            )
            self.label.grid(
                row=0,
                column=0,
                columnspan=2,
                padx=2,
                pady=(0, resolved_label_gap),
                sticky="ew",
            )
            control_row = 1

        entry_kwargs: dict[str, Any] = {
            "placeholder_text": placeholder,
            "font": self.font_config.tuple(self.font_role),
            "state": normalize_control_state(enabled),
            "height": control_height,
        }
        if entry_width is not None:
            entry_kwargs["width"] = entry_width

        self.entry = ctk.CTkEntry(self.frame, **entry_kwargs)
        self.entry.grid(
            row=control_row,
            column=0,
            sticky="ew",
        )

        self.button = ctk.CTkButton(
            self.frame,
            text=button_text,
            width=auxiliary_width,
            height=control_height,
            command=self.open_dialog,
            state=normalize_control_state(enabled),
            font=self.font_config.tuple(self.button_font_role),
            **get_button_style_options(self.button_style),
        )
        self.button.grid(
            row=control_row,
            column=1,
            padx=(auxiliary_gap, 0),
            sticky="e",
        )

        if value:
            self.set_value(value)

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def get_value(self) -> str:
        return self.entry.get()

    def set_value(self, value: str) -> None:
        previous_state = str(self.entry.cget("state"))
        if previous_state == "disabled":
            self.entry.configure(state="normal")
        self.entry.delete(0, "end")
        self.entry.insert(0, str(value))
        if previous_state == "disabled":
            self.entry.configure(state="disabled")
        if callable(self.on_change):
            self.on_change(str(value))

    def clear(self) -> None:
        self.set_value("")

    def set_enabled(self, enabled: bool) -> None:
        state = normalize_control_state(enabled)
        self.entry.configure(state=state)
        self.button.configure(state=state)

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            if self.label is not None:
                self.label.configure(
                    font=self.font_config.tuple(
                        self.label_font_role,
                        self.label_weight,
                    )
                )
            self.entry.configure(
                font=self.font_config.tuple(self.font_role)
            )
            self.button.configure(
                font=self.font_config.tuple(self.button_font_role)
            )
        colors = get_control_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color="transparent")
            if self.label is not None:
                self.label.configure(
                    text_color=colors["label_text_color"]
                )
            apply_standard_control_colors(
                self.entry,
                appearance_mode,
                surface_theme,
            )
            self.button.configure(
                **get_button_style_options(
                    self.button_style,
                    color_theme,
                    surface_theme,
                    appearance_mode,
                )
            )
        except Exception:
            pass

    def open_dialog(self) -> str | None:
        try:
            from tkinter import filedialog

            if self.mode == "file":
                selected = filedialog.askopenfilename(
                    title=self.dialog_title,
                    filetypes=self.filetypes,
                )
            elif self.mode == "save_file":
                selected = filedialog.asksaveasfilename(
                    title=self.dialog_title,
                    filetypes=self.filetypes,
                )
            else:
                selected = filedialog.askdirectory(
                    title=self.dialog_title
                )
        except Exception:
            selected = ""

        if selected:
            self.set_value(str(selected))
            return str(selected)
        return None

class LabeledComboAction:
    """Combo box with one auxiliary action button."""

    def __init__(
        self,
        parent: Any,
        label: str,
        values: Iterable[str | ChoiceOption | Mapping[str, Any]],
        default_value: str | None = None,
        combo_command: Callable[[str], None] | None = None,
        button_text: str = "...",
        button_command: Callable[[], None] | None = None,
        font_config: FontConfig | None = None,
        enabled: bool = True,
        button_enabled: bool | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        label_visible: bool = True,
        height: int | None = None,
        width: int | None = None,
        button_width: int | None = None,
        gap: int | None = None,
        font_role: str = "body",
        button_font_role: str | None = None,
        label_font_role: str = "small",
        label_weight: str | None = "bold",
        label_gap: int | None = None,
        button_style: str = "secondary",
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        self.button_font_role = str(button_font_role or self.font_role)
        self.label_font_role = str(label_font_role or "small")
        self.label_weight = label_weight
        self.button_style = normalize_button_style(button_style)
        self.options = coerce_choice_options(values)
        labels = [option.label for option in self.options]
        self._value_by_label = {
            option.label: option.resolved_value
            for option in self.options
        }

        control_height = resolve_control_dimension(
            height,
            self.layout_profile.control_height,
            field_name="height",
        )
        auxiliary_width = resolve_control_dimension(
            button_width,
            self.layout_profile.picker_button_width,
            field_name="button_width",
        )
        auxiliary_gap = resolve_control_gap(
            gap,
            self.layout_profile.inline_gap,
            field_name="gap",
        )
        resolved_label_gap = resolve_control_gap(
            label_gap,
            self.layout_profile.label_gap,
            field_name="label_gap",
        )

        combo_width = None
        if width is not None:
            total_width = resolve_control_dimension(
                width,
                width,
                field_name="width",
            )
            combo_width = total_width - auxiliary_width - auxiliary_gap
            if combo_width <= 0:
                raise ValueError(
                    "width must be greater than button_width + gap."
                )

        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = None
        control_row = 0
        if label_visible and str(label).strip():
            self.label = ctk.CTkLabel(
                self.frame,
                text=label,
                font=self.font_config.tuple(
                    self.label_font_role,
                    self.label_weight,
                ),
                text_color=("gray30", "gray72"),
                anchor="w",
            )
            self.label.grid(
                row=0,
                column=0,
                columnspan=2,
                padx=2,
                pady=(0, resolved_label_gap),
                sticky="ew",
            )
            control_row = 1

        combo_kwargs: dict[str, Any] = {
            "values": labels,
            "font": self.font_config.tuple(self.font_role),
            "dropdown_font": self.font_config.tuple(self.font_role),
            "state": normalize_control_state(enabled),
            "command": combo_command,
            "height": control_height,
        }
        if combo_width is not None:
            combo_kwargs["width"] = combo_width

        self.combo = ctk.CTkComboBox(self.frame, **combo_kwargs)
        self.combo.grid(
            row=control_row,
            column=0,
            sticky="ew",
        )

        resolved_button_enabled = (
            enabled
            if button_enabled is None
            else bool(button_enabled)
        )
        self.button = ctk.CTkButton(
            self.frame,
            text=button_text,
            width=auxiliary_width,
            height=control_height,
            command=button_command,
            state=normalize_control_state(resolved_button_enabled),
            font=self.font_config.tuple(self.button_font_role),
            **get_button_style_options(self.button_style),
        )
        self.button.grid(
            row=control_row,
            column=1,
            padx=(auxiliary_gap, 0),
            sticky="e",
        )

        if default_value and default_value in labels:
            self.combo.set(default_value)
        elif labels:
            self.combo.set(labels[0])

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def get_label(self) -> str:
        return self.combo.get()

    def get_value(self) -> Any:
        label = self.get_label()
        return self._value_by_label.get(label, label)

    def set_value(self, value: str) -> None:
        self.combo.set(str(value))

    def set_values(
        self,
        values: Iterable[str | ChoiceOption | Mapping[str, Any]],
        default_value: str | None = None,
    ) -> None:
        self.options = coerce_choice_options(values)
        labels = [option.label for option in self.options]
        self._value_by_label = {
            option.label: option.resolved_value
            for option in self.options
        }
        current = self.combo.get()
        self.combo.configure(values=labels)
        if default_value and default_value in labels:
            self.combo.set(default_value)
        elif current in labels:
            self.combo.set(current)
        elif labels:
            self.combo.set(labels[0])
        else:
            self.combo.set("")

    def set_enabled(self, enabled: bool) -> None:
        state = normalize_control_state(enabled)
        self.combo.configure(state=state)
        self.button.configure(state=state)

    def set_action_enabled(self, enabled: bool) -> None:
        self.button.configure(
            state=normalize_control_state(enabled)
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
            if self.label is not None:
                self.label.configure(
                    font=self.font_config.tuple(
                        self.label_font_role,
                        self.label_weight,
                    )
                )
            self.combo.configure(
                font=self.font_config.tuple(self.font_role),
                dropdown_font=self.font_config.tuple(self.font_role),
            )
            self.button.configure(
                font=self.font_config.tuple(self.button_font_role)
            )
        colors = get_control_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color="transparent")
            if self.label is not None:
                self.label.configure(
                    text_color=colors["label_text_color"]
                )
            apply_standard_control_colors(
                self.combo,
                appearance_mode,
                surface_theme,
                include_dropdown=True,
            )
            self.button.configure(
                **get_button_style_options(
                    self.button_style,
                    color_theme,
                    surface_theme,
                    appearance_mode,
                )
            )
        except Exception:
            pass

class LabeledCheckBox:
    """Reusable checkbox row with configurable size and font role."""

    def __init__(
        self,
        parent: Any,
        text: str,
        default: bool = False,
        font_config: FontConfig | None = None,
        enabled: bool = True,
        command: Callable[[], None] | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        height: int | None = None,
        width: int | None = None,
        font_role: str = "body",
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        control_height = resolve_control_dimension(
            height,
            self.layout_profile.toggle_height,
            field_name="height",
        )

        self.variable = ctk.BooleanVar(value=bool(default))
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        kwargs: dict[str, Any] = {
            "text": text,
            "variable": self.variable,
            "command": command,
            "font": self.font_config.tuple(self.font_role),
            "state": normalize_control_state(enabled),
            "height": control_height,
        }
        if width is not None:
            kwargs["width"] = resolve_control_dimension(
                width,
                width,
                field_name="width",
            )

        self.checkbox = ctk.CTkCheckBox(self.frame, **kwargs)
        self.checkbox.grid(
            row=0,
            column=0,
            padx=2,
            pady=0,
            sticky="ew",
        )

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def get_value(self) -> bool:
        return bool(self.variable.get())

    def set_value(self, value: bool) -> None:
        self.variable.set(bool(value))

    def set_enabled(self, enabled: bool) -> None:
        self.checkbox.configure(
            state=normalize_control_state(enabled)
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
            self.checkbox.configure(
                font=self.font_config.tuple(self.font_role)
            )
        colors = get_control_colors(appearance_mode, surface_theme)
        accent = get_accent_colors(color_theme)
        try:
            self.checkbox.configure(
                fg_color=accent["primary"],
                hover_color=accent["hover"],
                border_color=colors["border_color"],
                text_color=colors["text_color"],
            )
        except Exception:
            pass

class LabeledSwitch:
    """Reusable switch row with configurable size and font role."""

    def __init__(
        self,
        parent: Any,
        text: str,
        default: bool = False,
        font_config: FontConfig | None = None,
        enabled: bool = True,
        command: Callable[[], None] | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        *,
        height: int | None = None,
        width: int | None = None,
        font_role: str = "body",
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        control_height = resolve_control_dimension(
            height,
            self.layout_profile.toggle_height,
            field_name="height",
        )

        self.variable = ctk.BooleanVar(value=bool(default))
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        kwargs: dict[str, Any] = {
            "text": text,
            "variable": self.variable,
            "command": command,
            "font": self.font_config.tuple(self.font_role),
            "state": normalize_control_state(enabled),
            "height": control_height,
        }
        if width is not None:
            kwargs["width"] = resolve_control_dimension(
                width,
                width,
                field_name="width",
            )

        self.switch = ctk.CTkSwitch(self.frame, **kwargs)
        self.switch.grid(
            row=0,
            column=0,
            padx=2,
            pady=0,
            sticky="ew",
        )

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def get_value(self) -> bool:
        return bool(self.variable.get())

    def set_value(self, value: bool) -> None:
        self.variable.set(bool(value))

    def set_enabled(self, enabled: bool) -> None:
        self.switch.configure(
            state=normalize_control_state(enabled)
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
            self.switch.configure(
                font=self.font_config.tuple(self.font_role)
            )
        colors = get_control_colors(appearance_mode, surface_theme)
        accent = get_accent_colors(color_theme)
        try:
            self.switch.configure(
                progress_color=accent["primary"],
                button_color=colors["text_color"],
                button_hover_color=colors["label_text_color"],
                text_color=colors["text_color"],
            )
        except Exception:
            pass

class ActionButton:
    """Styled action button with reusable size and typography."""

    def __init__(
        self,
        parent: Any,
        text: str,
        command: Callable[[], None] | None = None,
        style: str = "primary",
        font_config: FontConfig | None = None,
        enabled: bool = True,
        height: int | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
        color_theme: str | None = "blue",
        surface_theme: str | None = "default",
        appearance_mode: str | None = "dark",
        *,
        width: int | None = None,
        font_role: str = "body",
        font_weight: str | None = None,
        anchor: str = "center",
        icon_text: str = "",
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.font_role = str(font_role or "body")
        self.font_weight = font_weight
        self.style = normalize_button_style(style)
        self.color_theme = str(color_theme or "blue")
        self.surface_theme = str(surface_theme or "default")
        self.appearance_mode = str(appearance_mode or "dark")
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)

        options = get_button_style_options(
            self.style,
            self.color_theme,
            self.surface_theme,
            self.appearance_mode,
        )
        button_kwargs: dict[str, Any] = {
            "text": f"{icon_text} {text}".strip(),
            "command": command,
            "font": self.font_config.tuple(
                self.font_role,
                self.font_weight,
            ),
            "state": normalize_control_state(enabled),
            "height": resolve_control_dimension(
                height,
                self.layout_profile.action_height,
                field_name="height",
            ),
            "anchor": anchor,
            **options,
        }
        if width is not None:
            button_kwargs["width"] = resolve_control_dimension(
                width,
                width,
                field_name="width",
            )

        self.button = ctk.CTkButton(
            self.frame,
            **button_kwargs,
        )
        self.button.grid(row=0, column=0, sticky="ew")

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def set_enabled(self, enabled: bool) -> None:
        self.button.configure(
            state=normalize_control_state(enabled)
        )

    def configure(self, **kwargs: Any) -> None:
        self.button.configure(**kwargs)

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
            self.button.configure(
                font=self.font_config.tuple(
                    self.font_role,
                    self.font_weight,
                )
            )
        if color_theme is not None:
            self.color_theme = str(color_theme)
        if surface_theme is not None:
            self.surface_theme = str(surface_theme)
        if appearance_mode is not None:
            self.appearance_mode = str(appearance_mode)
        options = get_button_style_options(
            self.style,
            self.color_theme,
            self.surface_theme,
            self.appearance_mode,
        )
        if options:
            self.button.configure(**options)

class ButtonRow:
    """Reusable row of styled buttons."""

    def __init__(
        self,
        parent: Any,
        buttons: Iterable[ButtonSpec | Mapping[str, Any]],
        commands: Mapping[str, Callable[[], None]] | None = None,
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.commands = dict(commands or {})
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.buttons: dict[str, ActionButton] = {}

        specs = self._coerce_button_specs(buttons)
        for index, button_spec in enumerate(specs):
            self.frame.grid_columnconfigure(index, weight=1)
            button = ActionButton(
                self.frame,
                button_spec.text,
                command=self.commands.get(button_spec.key),
                style=button_spec.style,
                font_config=self.font_config,
                enabled=button_spec.enabled,
                layout_profile=self.layout_profile,
            )
            button.grid(
                row=0,
                column=index,
                padx=(
                    0,
                    self.layout_profile.button_gap
                    if index < len(specs) - 1
                    else 0,
                ),
                sticky="ew",
            )
            self.buttons[button_spec.key] = button

    def _coerce_button_specs(self, buttons: Iterable[ButtonSpec | Mapping[str, Any]]) -> list[ButtonSpec]:
        specs: list[ButtonSpec] = []
        for item in buttons:
            if isinstance(item, ButtonSpec):
                specs.append(item)
            else:
                specs.append(
                    ButtonSpec(
                        text=str(item.get("text") or item.get("label") or "Acción"),
                        command_key=item.get("command_key"),
                        style=str(item.get("style") or "primary"),
                        enabled=bool(item.get("enabled", True)),
                    )
                )
        return specs

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def set_enabled(self, key: str, enabled: bool) -> None:
        button = self.buttons.get(key)
        if button is not None:
            button.set_enabled(enabled)

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
        for button in self.buttons.values():
            button.apply_visual_preferences(
                font_config=self.font_config,
                color_theme=color_theme,
                surface_theme=surface_theme,
                appearance_mode=appearance_mode,
            )
