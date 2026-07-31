from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .constants import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from .layout_profiles import GuiLayoutProfile, get_layout_profile
from .models import ThemeConfig, WindowConfig
from .preferences import GuiPreferences


@dataclass(frozen=True)
class GuiMenuItem:
    """Declarative sidebar/footer action shown by a GuiCore application."""

    text: str
    command_key: str | None = None
    icon_text: str = ""
    enabled: bool = True

    @property
    def key(self) -> str:
        return self.command_key or self.text.lower().strip().replace(" ", "_")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "command_key": self.key,
            "icon_text": self.icon_text,
            "enabled": self.enabled,
        }


@dataclass(frozen=True)
class GuiActionButton:
    """Declarative action button configuration for reusable button bars."""

    text: str
    command_key: str | None = None
    style: str = "primary"
    enabled: bool = True

    @property
    def key(self) -> str:
        return self.command_key or self.text.lower().strip().replace(" ", "_")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "command_key": self.key,
            "style": self.style,
            "enabled": self.enabled,
        }


@dataclass(frozen=True)
class GuiAppConfig:
    """High-level visual contract for a CustomTkinter ecosystem app.

    This object intentionally contains visual/app shell data only. Business logic,
    scanning, processing, reports, and project-specific settings stay in each tool.
    """

    app_name: str
    app_subtitle: str = ""
    app_version: str = ""
    width: int = DEFAULT_WINDOW_WIDTH
    height: int = DEFAULT_WINDOW_HEIGHT
    min_width: int = 1000
    min_height: int = 640
    sidebar_width: int = 270
    layout_profile: str | GuiLayoutProfile = "standard"
    maximize_on_start: bool = True
    restart_on_appearance_change: bool = True
    restart_delay_ms: int = 350
    icon_path: str | None = None
    icon_png_path: str | None = None
    theme_config: ThemeConfig = field(default_factory=ThemeConfig)
    preferences: GuiPreferences = field(default_factory=GuiPreferences)
    help_text: str = ""
    about_text: str = ""
    footer_items: Tuple[GuiMenuItem, ...] = field(
        default_factory=lambda: (
            GuiMenuItem("Configuración", "settings"),
            GuiMenuItem("Ayuda", "help"),
            GuiMenuItem("Acerca de", "about"),
            GuiMenuItem("Salir", "exit"),
        )
    )

    @property
    def resolved_layout_profile(self) -> GuiLayoutProfile:
        return get_layout_profile(self.layout_profile)

    @property
    def window_title(self) -> str:
        if self.app_version:
            return f"{self.app_name} {self.app_version}"
        return self.app_name

    def to_window_config(self) -> WindowConfig:
        return WindowConfig(
            title=self.window_title,
            width=self.width,
            height=self.height,
            min_width=self.min_width,
            min_height=self.min_height,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "app_name": self.app_name,
            "app_subtitle": self.app_subtitle,
            "app_version": self.app_version,
            "width": self.width,
            "height": self.height,
            "min_width": self.min_width,
            "min_height": self.min_height,
            "sidebar_width": self.sidebar_width,
            "layout_profile": self.resolved_layout_profile.to_dict(),
            "maximize_on_start": self.maximize_on_start,
            "restart_on_appearance_change": self.restart_on_appearance_change,
            "restart_delay_ms": self.restart_delay_ms,
            "icon_path": self.icon_path,
            "icon_png_path": self.icon_png_path,
            "theme_config": self.theme_config.to_dict(),
            "preferences": self.preferences.to_dict(),
            "help_text": self.help_text,
            "about_text": self.about_text,
            "footer_items": [item.to_dict() for item in self.footer_items],
        }
