from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Tuple

from ..dependencies import require_customtkinter
from ..styles.colors import get_surface_colors
from ..styles.fonts import FontConfig
from ..widgets.form_controls import ActionButton
from .window_icon import apply_window_icon, get_window_icon_metadata, set_window_icon_metadata


@dataclass(frozen=True)
class SecondaryWindowConfig:
    """Visual contract for reusable child windows.

    This is for full secondary windows such as Categorías, Settings, Historial or
    Detalle. Small alerts and confirmations still belong to dialogs.
    """

    title: str
    subtitle: str = ""
    width: int = 720
    height: int = 520
    min_width: int = 520
    min_height: int = 360
    modal: bool = True
    resizable: Tuple[bool, bool] = (True, True)
    icon_path: str | None = None
    icon_png_path: str | None = None
    inherit_parent_icon: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "width": self.width,
            "height": self.height,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "modal": self.modal,
            "resizable": list(self.resizable),
            "icon_path": self.icon_path,
            "icon_png_path": self.icon_png_path,
            "inherit_parent_icon": self.inherit_parent_icon,
        }


def normalize_secondary_window_size(width: int, height: int, min_width: int = 520, min_height: int = 360) -> tuple[int, int]:
    """Clamp child window dimensions to a usable minimum."""

    return max(int(width), int(min_width)), max(int(height), int(min_height))


def calculate_child_geometry(
    parent_width: int,
    parent_height: int,
    parent_x: int,
    parent_y: int,
    child_width: int,
    child_height: int,
) -> str:
    """Return a geometry string centered over a parent window."""

    x = int(parent_x + max((parent_width - child_width) // 2, 0))
    y = int(parent_y + max((parent_height - child_height) // 2, 0))
    return f"{child_width}x{child_height}+{x}+{y}"


class SecondaryWindow:
    """Reusable CustomTkinter child window shell.

    It provides the common structure only: header, body, footer and modal behavior.
    The concrete tool decides what widgets live inside the content frame.
    """

    def __init__(
        self,
        parent: Any,
        config: SecondaryWindowConfig,
        font_config: FontConfig | None = None,
    ) -> None:
        self.parent = parent
        self.config = config
        self.font_config = font_config or FontConfig()
        self.ctk = require_customtkinter()
        width, height = normalize_secondary_window_size(config.width, config.height, config.min_width, config.min_height)

        self.window = self.ctk.CTkToplevel(parent)
        self.window.title(config.title)
        icon_path = config.icon_path
        icon_png_path = config.icon_png_path
        if config.inherit_parent_icon:
            parent_icon_path, parent_icon_png_path = get_window_icon_metadata(parent)
            icon_path = icon_path or parent_icon_path
            icon_png_path = icon_png_path or parent_icon_png_path
        set_window_icon_metadata(self.window, icon_path, icon_png_path)
        self.window_icon_result = apply_window_icon(self.window, icon_path, icon_png_path)
        self.window.geometry(f"{width}x{height}")
        self.window.minsize(config.min_width, config.min_height)
        self.window.resizable(*config.resizable)
        self.window.transient(parent)

        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)

        self.header_frame = self.ctk.CTkFrame(self.window, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(18, 10))
        self.header_frame.grid_columnconfigure(0, weight=1)

        self.title_label = self.ctk.CTkLabel(
            self.header_frame,
            text=config.title,
            font=self.font_config.tuple("section", "bold"),
            anchor="w",
        )
        self.title_label.grid(row=0, column=0, sticky="ew")

        self.subtitle_label = None
        if config.subtitle:
            self.subtitle_label = self.ctk.CTkLabel(
                self.header_frame,
                text=config.subtitle,
                font=self.font_config.tuple("body"),
                text_color="gray",
                anchor="w",
                justify="left",
                wraplength=max(width - 60, 320),
            )
            self.subtitle_label.grid(row=1, column=0, sticky="ew", pady=(6, 0))

        self.content_frame = self.ctk.CTkFrame(self.window, corner_radius=12)
        self.content_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 12))
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.footer_frame = self.ctk.CTkFrame(self.window, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 18))
        self.footer_frame.grid_columnconfigure(0, weight=1)
        self._footer_column = 1
        self._footer_buttons: list[ActionButton] = []

        self.center_over_parent()
        self.window.protocol("WM_DELETE_WINDOW", self.close)
        self.window.after(10, self.window.lift)

        if config.modal:
            self.window.grab_set()
            self.window.focus_force()

    def center_over_parent(self) -> None:
        try:
            self.parent.update_idletasks()
            self.window.update_idletasks()
            parent_width = int(self.parent.winfo_width())
            parent_height = int(self.parent.winfo_height())
            parent_x = int(self.parent.winfo_rootx())
            parent_y = int(self.parent.winfo_rooty())
            child_width = int(self.window.winfo_width()) or self.config.width
            child_height = int(self.window.winfo_height()) or self.config.height
            self.window.geometry(
                calculate_child_geometry(parent_width, parent_height, parent_x, parent_y, child_width, child_height)
            )
        except Exception:
            pass

    def add_footer_button(
        self,
        text: str,
        command: Callable[[], None] | None = None,
        style: str = "secondary",
    ) -> ActionButton:
        button = ActionButton(self.footer_frame, text, command=command, style=style, font_config=self.font_config)
        button.grid(row=0, column=self._footer_column, padx=(10, 0), sticky="e")
        self._footer_column += 1
        self._footer_buttons.append(button)
        return button

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
                self.subtitle_label.configure(font=self.font_config.tuple("body"))
        surface = get_surface_colors(appearance_mode, surface_theme)
        try:
            self.window.configure(fg_color=surface["root"])
            self.content_frame.configure(fg_color=surface["card"])
        except Exception:
            pass
        for button in list(self._footer_buttons):
            button.apply_visual_preferences(
                font_config=self.font_config,
                color_theme=color_theme,
                surface_theme=surface_theme,
                appearance_mode=appearance_mode,
            )

    def wait(self) -> None:
        if self.config.modal:
            self.parent.wait_window(self.window)

    def close(self) -> None:
        try:
            self.window.grab_release()
        except Exception:
            pass
        self.window.destroy()
