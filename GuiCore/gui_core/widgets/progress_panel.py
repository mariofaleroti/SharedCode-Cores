from __future__ import annotations

from typing import Any, Callable

from ..dependencies import require_customtkinter
from ..layout_profiles import GuiLayoutProfile, get_layout_profile
from ..styles.colors import get_accent_colors, get_surface_colors
from ..styles.fonts import FontConfig
from .form_controls import get_button_style_options


def calculate_progress_value(current: int | float, total: int | float) -> float:
    try:
        total_value = float(total)
        if total_value <= 0:
            return 0.0
        value = float(current) / total_value
    except (TypeError, ValueError, ZeroDivisionError):
        return 0.0
    return max(0.0, min(value, 1.0))


class ProgressPanel:
    """Reusable progress panel with optional cooperative cancellation."""

    def __init__(
        self,
        parent: Any,
        font_config: FontConfig | None = None,
        layout_profile: str | GuiLayoutProfile | None = None,
    ) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.layout_profile = get_layout_profile(layout_profile)
        self.font_config = font_config or FontConfig().with_size_offset(
            self.layout_profile.font_size_offset
        )
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(
            self.frame,
            text="Preparando...",
            font=self.font_config.tuple("small"),
            text_color="gray",
            anchor="w",
        )
        self.label.grid(
            row=0,
            column=0,
            padx=(15, self.layout_profile.inline_gap),
            pady=(12, 4),
            sticky="ew",
        )

        self.cancel_button = ctk.CTkButton(
            self.frame,
            text="Cancelar",
            width=92,
            height=self.layout_profile.control_height,
            state="disabled",
            font=self.font_config.tuple("small"),
            **get_button_style_options("secondary"),
        )
        self.cancel_button.grid(
            row=0,
            column=1,
            padx=(0, 15),
            pady=(8, 2),
            sticky="e",
        )
        self.cancel_button.grid_remove()

        self.progress_bar = ctk.CTkProgressBar(
            self.frame,
            mode="determinate",
            height=12,
        )
        self.progress_bar.grid(
            row=1,
            column=0,
            columnspan=2,
            padx=15,
            pady=(0, 12),
            sticky="ew",
        )
        self.progress_bar.set(0)
        self._indeterminate_active = False
        self._cancel_command: Callable[[], Any] | None = None

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

    def set_cancel_action(
        self,
        command: Callable[[], Any] | None,
        *,
        text: str = "Cancelar",
    ) -> None:
        self._cancel_command = command
        self.cancel_button.configure(
            text=text,
            command=command,
        )
        self.set_cancel_enabled(callable(command))

    def set_cancel_enabled(self, enabled: bool) -> None:
        self.cancel_button.configure(
            state="normal" if enabled and callable(self._cancel_command) else "disabled"
        )

    def show_cancel(self) -> None:
        self.cancel_button.grid()

    def hide_cancel(self) -> None:
        self.cancel_button.grid_remove()

    def _configure_cancel(self, cancelable: bool) -> None:
        if cancelable and callable(self._cancel_command):
            self.set_cancel_enabled(True)
            self.show_cancel()
        else:
            self.set_cancel_enabled(False)
            self.hide_cancel()

    def _stop_indeterminate(self) -> None:
        if not self._indeterminate_active:
            return
        try:
            self.progress_bar.stop()
        except Exception:
            pass
        self._indeterminate_active = False

    def _use_determinate_mode(self) -> None:
        self._stop_indeterminate()
        try:
            self.progress_bar.configure(mode="determinate")
        except Exception:
            pass

    def show(
        self,
        message: str = "Preparando...",
        value: float = 0.0,
        *,
        cancelable: bool = False,
    ) -> None:
        self._use_determinate_mode()
        self.label.configure(text=message)
        self.progress_bar.set(max(0.0, min(float(value), 1.0)))
        self._configure_cancel(cancelable)
        self.frame.grid()

    def show_indeterminate(
        self,
        message: str = "Procesando...",
        *,
        cancelable: bool = False,
    ) -> None:
        self.label.configure(text=message)
        try:
            self.progress_bar.configure(mode="indeterminate")
            if not self._indeterminate_active:
                self.progress_bar.start()
                self._indeterminate_active = True
        except Exception:
            self.progress_bar.set(0)
            self._indeterminate_active = False
        self._configure_cancel(cancelable)
        self.frame.grid()

    def update(
        self,
        current: int | float,
        total: int | float,
        unit: str = "elementos",
        message: str | None = None,
    ) -> None:
        self._use_determinate_mode()
        value = calculate_progress_value(current, total)
        percent = int(value * 100)
        if message is None:
            message = (
                f"Procesando {int(current)} de {int(total)} "
                f"{unit} ({percent}%)"
            )
        self.label.configure(text=message)
        self.progress_bar.set(value)
        self.frame.grid()

    def complete(self, message: str = "Finalizado correctamente") -> None:
        self._use_determinate_mode()
        self.label.configure(text=message)
        self.progress_bar.set(1)
        self.set_cancel_enabled(False)
        self.hide_cancel()
        self.frame.grid()

    def hide(self) -> None:
        self._stop_indeterminate()
        self.set_cancel_enabled(False)
        self.hide_cancel()
        self.frame.grid_remove()

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
            self.cancel_button.configure(
                font=self.font_config.tuple("small")
            )
        accent = get_accent_colors(color_theme)
        surface = get_surface_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color=surface["card"])
            self.progress_bar.configure(progress_color=accent["primary"])
            self.cancel_button.configure(
                **get_button_style_options(
                    "secondary",
                    color_theme,
                    surface_theme,
                    appearance_mode,
                )
            )
        except Exception:
            pass
