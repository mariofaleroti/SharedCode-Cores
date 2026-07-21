from __future__ import annotations

from typing import Any

from ..dependencies import require_customtkinter
from ..styles.colors import get_accent_colors, get_surface_colors
from ..styles.fonts import FontConfig


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
    """Reusable determinate progress panel."""

    def __init__(self, parent: Any, font_config: FontConfig | None = None) -> None:
        ctk = require_customtkinter()
        self.ctk = ctk
        self.font_config = font_config or FontConfig()
        self.frame = ctk.CTkFrame(parent)
        self.frame.grid_columnconfigure(0, weight=1)
        self.label = ctk.CTkLabel(
            self.frame,
            text="Preparando...",
            font=self.font_config.tuple("small"),
            text_color="gray",
            anchor="w",
        )
        self.label.grid(row=0, column=0, padx=15, pady=(12, 4), sticky="ew")
        self.progress_bar = ctk.CTkProgressBar(self.frame, mode="determinate", height=12)
        self.progress_bar.grid(row=1, column=0, padx=15, pady=(0, 12), sticky="ew")
        self.progress_bar.set(0)
        self._indeterminate_active = False

    def grid(self, *args: Any, **kwargs: Any) -> None:
        self.frame.grid(*args, **kwargs)

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

    def show(self, message: str = "Preparando...", value: float = 0.0) -> None:
        self._use_determinate_mode()
        self.label.configure(text=message)
        self.progress_bar.set(max(0.0, min(float(value), 1.0)))
        self.frame.grid()

    def show_indeterminate(self, message: str = "Procesando...") -> None:
        """Show an animated progress bar while the total work is unknown."""
        self.label.configure(text=message)
        try:
            self.progress_bar.configure(mode="indeterminate")
            if not self._indeterminate_active:
                self.progress_bar.start()
                self._indeterminate_active = True
        except Exception:
            self.progress_bar.set(0)
            self._indeterminate_active = False
        self.frame.grid()

    def update(self, current: int | float, total: int | float, unit: str = "elementos", message: str | None = None) -> None:
        self._use_determinate_mode()
        value = calculate_progress_value(current, total)
        percent = int(value * 100)
        if message is None:
            message = f"Procesando {int(current)} de {int(total)} {unit} ({percent}%)"
        self.label.configure(text=message)
        self.progress_bar.set(value)
        self.frame.grid()

    def complete(self, message: str = "Finalizado correctamente") -> None:
        self._use_determinate_mode()
        self.label.configure(text=message)
        self.progress_bar.set(1)
        self.frame.grid()

    def hide(self) -> None:
        self._stop_indeterminate()
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
        accent = get_accent_colors(color_theme)
        surface = get_surface_colors(appearance_mode, surface_theme)
        try:
            self.frame.configure(fg_color=surface["card"])
            self.progress_bar.configure(progress_color=accent["primary"])
        except Exception:
            pass
