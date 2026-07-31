from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from ..dependencies import require_customtkinter
from ..styles.colors import get_control_colors, get_surface_colors
from ..styles.fonts import FontConfig


@dataclass(frozen=True)
class TooltipSpec:
    """Serializable configuration for one reusable widget tooltip."""

    text: str
    title: str = ""
    delay_ms: int = 800
    visible_ms: int = 4000
    wraplength: int = 320
    offset_x: int = 16
    offset_y: int = 18
    enabled: bool = True

    def __post_init__(self) -> None:
        if int(self.delay_ms) < 0:
            raise ValueError("delay_ms cannot be negative.")
        if int(self.visible_ms) < 0:
            raise ValueError("visible_ms cannot be negative.")
        if int(self.wraplength) <= 0:
            raise ValueError("wraplength must be greater than zero.")

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": str(self.text),
            "title": str(self.title),
            "delay_ms": int(self.delay_ms),
            "visible_ms": int(self.visible_ms),
            "wraplength": int(self.wraplength),
            "offset_x": int(self.offset_x),
            "offset_y": int(self.offset_y),
            "enabled": bool(self.enabled),
        }


def iter_widget_tree(widget: Any) -> tuple[Any, ...]:
    """Return one widget and its current descendants defensively."""

    collected: list[Any] = []
    pending = [widget]
    seen: set[int] = set()

    while pending:
        current = pending.pop(0)
        identity = id(current)
        if identity in seen:
            continue
        seen.add(identity)
        collected.append(current)

        try:
            children = list(current.winfo_children())
        except Exception:
            children = []
        pending.extend(children)

    return tuple(collected)


class WidgetTooltip:
    """Theme-aware tooltip for Tkinter and CustomTkinter widgets."""

    def __init__(
        self,
        widget: Any,
        text: str,
        *,
        title: str = "",
        delay_ms: int = 800,
        visible_ms: int = 4000,
        wraplength: int = 320,
        offset_x: int = 16,
        offset_y: int = 18,
        enabled: bool = True,
        bind_descendants: bool = True,
        font_config: FontConfig | None = None,
        color_theme: str | None = "blue",
        surface_theme: str | None = "default",
        appearance_mode: str | None = "dark",
    ) -> None:
        self.ctk = require_customtkinter()
        self.widget = widget
        self.spec = TooltipSpec(
            text=text,
            title=title,
            delay_ms=delay_ms,
            visible_ms=visible_ms,
            wraplength=wraplength,
            offset_x=offset_x,
            offset_y=offset_y,
            enabled=enabled,
        )
        self.bind_descendants = bool(bind_descendants)
        self.font_config = font_config or FontConfig()
        self.color_theme = str(color_theme or "blue")
        self.surface_theme = str(surface_theme or "default")
        self.appearance_mode = str(appearance_mode or "dark")

        self.window = None
        self.container = None
        self.title_label = None
        self.text_label = None
        self._show_after_id: str | None = None
        self._hide_after_id: str | None = None
        self._bindings: list[tuple[Any, str, str | None]] = []
        self._destroyed = False

        self.refresh_bindings()

    @property
    def is_visible(self) -> bool:
        if self.window is None:
            return False
        try:
            return bool(self.window.winfo_exists())
        except Exception:
            return False

    def refresh_bindings(self) -> None:
        """Rebind the current widget tree after descendants change."""

        self._unbind_all()
        targets: Iterable[Any]
        if self.bind_descendants:
            targets = iter_widget_tree(self.widget)
        else:
            targets = (self.widget,)

        for target in targets:
            self._bind(target, "<Enter>", self._on_enter)
            self._bind(target, "<Leave>", self._on_leave)
            self._bind(target, "<Motion>", self._on_motion)
            self._bind(target, "<ButtonPress>", self._on_hide_event)
            self._bind(target, "<MouseWheel>", self._on_hide_event)
            self._bind(target, "<Button-4>", self._on_hide_event)
            self._bind(target, "<Button-5>", self._on_hide_event)

        self._bind(self.widget, "<Destroy>", self._on_destroy)

    def _bind(self, target: Any, sequence: str, callback: Any) -> None:
        try:
            binding_id = target.bind(sequence, callback, add="+")
        except Exception:
            binding_id = None
        self._bindings.append((target, sequence, binding_id))

    def _unbind_all(self) -> None:
        for target, sequence, binding_id in self._bindings:
            try:
                if binding_id:
                    target.unbind(sequence, binding_id)
            except Exception:
                pass
        self._bindings.clear()

    def _on_enter(self, _event: Any = None) -> None:
        self.schedule()

    def _on_leave(self, _event: Any = None) -> None:
        self.hide()

    def _on_motion(self, _event: Any = None) -> None:
        self.hide()
        self.schedule()

    def _on_hide_event(self, _event: Any = None) -> None:
        self.hide()

    def _on_destroy(self, event: Any = None) -> None:
        try:
            is_primary = event is None or event.widget is self.widget
        except Exception:
            is_primary = True
        if is_primary:
            self.destroy()

    def schedule(self) -> None:
        if (
            self._destroyed
            or not self.spec.enabled
            or not str(self.spec.text).strip()
        ):
            return

        self.cancel_pending()
        try:
            self._show_after_id = self.widget.after(
                int(self.spec.delay_ms),
                self.show_now,
            )
        except Exception:
            self._show_after_id = None

    def cancel_pending(self) -> None:
        for attribute in ("_show_after_id", "_hide_after_id"):
            callback_id = getattr(self, attribute)
            if callback_id:
                try:
                    self.widget.after_cancel(callback_id)
                except Exception:
                    pass
                setattr(self, attribute, None)

    def _pointer_position(self) -> tuple[int, int]:
        try:
            return (
                int(self.widget.winfo_pointerx()),
                int(self.widget.winfo_pointery()),
            )
        except Exception:
            try:
                return (
                    int(self.widget.winfo_rootx()),
                    int(self.widget.winfo_rooty()),
                )
            except Exception:
                return (0, 0)

    def _bounded_position(
        self,
        requested_width: int,
        requested_height: int,
    ) -> tuple[int, int]:
        pointer_x, pointer_y = self._pointer_position()
        x = pointer_x + int(self.spec.offset_x)
        y = pointer_y + int(self.spec.offset_y)

        try:
            screen_width = int(self.widget.winfo_screenwidth())
            screen_height = int(self.widget.winfo_screenheight())
        except Exception:
            screen_width = 1920
            screen_height = 1080

        if x + requested_width > screen_width:
            x = max(
                0,
                pointer_x - requested_width - int(self.spec.offset_x),
            )
        if y + requested_height > screen_height:
            y = max(
                0,
                pointer_y - requested_height - int(self.spec.offset_y),
            )
        return (x, y)

    def show_now(self) -> bool:
        self._show_after_id = None
        if (
            self._destroyed
            or not self.spec.enabled
            or not str(self.spec.text).strip()
        ):
            return False

        self.hide_window()
        try:
            master = self.widget.winfo_toplevel()
            self.window = self.ctk.CTkToplevel(master)
            self.window.withdraw()
            self.window.overrideredirect(True)
            try:
                self.window.attributes("-topmost", True)
            except Exception:
                pass

            self.container = self.ctk.CTkFrame(
                self.window,
                corner_radius=8,
                border_width=1,
            )
            self.container.pack(fill="both", expand=True)

            row = 0
            self.title_label = None
            if str(self.spec.title).strip():
                self.title_label = self.ctk.CTkLabel(
                    self.container,
                    text=str(self.spec.title),
                    font=self.font_config.tuple("small", "bold"),
                    anchor="w",
                    justify="left",
                )
                self.title_label.grid(
                    row=row,
                    column=0,
                    padx=10,
                    pady=(8, 2),
                    sticky="ew",
                )
                row += 1

            self.text_label = self.ctk.CTkLabel(
                self.container,
                text=str(self.spec.text),
                font=self.font_config.tuple("small"),
                anchor="w",
                justify="left",
                wraplength=int(self.spec.wraplength),
            )
            self.text_label.grid(
                row=row,
                column=0,
                padx=10,
                pady=(4 if row == 0 else 2, 8),
                sticky="ew",
            )

            self.apply_visual_preferences(
                self.font_config,
                self.color_theme,
                self.surface_theme,
                self.appearance_mode,
            )

            self.window.update_idletasks()
            width = max(1, int(self.window.winfo_reqwidth()))
            height = max(1, int(self.window.winfo_reqheight()))
            x, y = self._bounded_position(width, height)
            self.window.geometry(f"+{x}+{y}")
            self.window.deiconify()
            self.window.lift()

            if int(self.spec.visible_ms) > 0:
                self._hide_after_id = self.widget.after(
                    int(self.spec.visible_ms),
                    self.hide,
                )
            return True
        except Exception:
            self.hide_window()
            return False

    def hide_window(self) -> None:
        if self.window is not None:
            try:
                self.window.destroy()
            except Exception:
                pass
        self.window = None
        self.container = None
        self.title_label = None
        self.text_label = None

    def hide(self) -> None:
        self.cancel_pending()
        self.hide_window()

    def set_text(
        self,
        text: str,
        *,
        title: str | None = None,
    ) -> None:
        values = self.spec.to_dict()
        values["text"] = str(text)
        if title is not None:
            values["title"] = str(title)
        self.spec = TooltipSpec(**values)
        self.hide()

    def set_enabled(self, enabled: bool) -> None:
        values = self.spec.to_dict()
        values["enabled"] = bool(enabled)
        self.spec = TooltipSpec(**values)
        if not enabled:
            self.hide()

    def apply_visual_preferences(
        self,
        font_config: FontConfig | None = None,
        color_theme: str | None = None,
        surface_theme: str | None = None,
        appearance_mode: str | None = None,
    ) -> None:
        if font_config is not None:
            self.font_config = font_config
        if color_theme is not None:
            self.color_theme = str(color_theme)
        if surface_theme is not None:
            self.surface_theme = str(surface_theme)
        if appearance_mode is not None:
            self.appearance_mode = str(appearance_mode)

        if self.window is None or self.container is None:
            return

        surface = get_surface_colors(
            self.appearance_mode,
            self.surface_theme,
        )
        controls = get_control_colors(
            self.appearance_mode,
            self.surface_theme,
        )
        try:
            self.window.configure(fg_color=surface["card_alt"])
            self.container.configure(
                fg_color=surface["card_alt"],
                border_color=surface["border"],
            )
            if self.title_label is not None:
                self.title_label.configure(
                    font=self.font_config.tuple("small", "bold"),
                    text_color=controls["text_color"],
                )
            if self.text_label is not None:
                self.text_label.configure(
                    font=self.font_config.tuple("small"),
                    text_color=controls["label_text_color"],
                )
        except Exception:
            pass

    def destroy(self) -> None:
        if self._destroyed:
            return
        self._destroyed = True
        self.cancel_pending()
        self.hide_window()
        self._unbind_all()
