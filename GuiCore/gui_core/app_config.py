from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .constants import DEFAULT_WINDOW_HEIGHT, DEFAULT_WINDOW_WIDTH
from .layout_profiles import GuiLayoutProfile, get_layout_profile
from .models import ThemeConfig, WindowConfig
from .preferences import GuiPreferences
from .visual_preferences import (
    VISUAL_PREFERENCES_NONE,
    normalize_visual_preferences_mode,
)


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
    icon_text: str = ""

    @property
    def key(self) -> str:
        return self.command_key or self.text.lower().strip().replace(" ", "_")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text": self.text,
            "command_key": self.key,
            "style": self.style,
            "enabled": self.enabled,
            "icon_text": self.icon_text,
        }


@dataclass(frozen=True)
class SidebarConfig:
    """Declarative structure for the reusable application sidebar."""

    header_visible: bool = True
    scrollable: bool = True
    footer_label_visible: bool = True
    footer_label: str = "MENÚ"
    footer_columns: int = 1
    footer_button_style: str = "secondary"
    primary_actions_visible: bool = True
    primary_actions_label_visible: bool = False
    primary_actions_label: str = "ACCIONES"
    primary_action_columns: int = 1
    scrollbar_width: int | None = None

    def __post_init__(self) -> None:
        for field_name in ("footer_columns", "primary_action_columns"):
            value = int(getattr(self, field_name))
            if value < 1 or value > 4:
                raise ValueError(f"{field_name} must be between 1 and 4.")
        if self.scrollbar_width is not None and int(self.scrollbar_width) <= 0:
            raise ValueError("scrollbar_width must be greater than zero.")
        if not str(self.footer_label).strip():
            raise ValueError("footer_label cannot be empty.")
        if not str(self.primary_actions_label).strip():
            raise ValueError("primary_actions_label cannot be empty.")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "header_visible": bool(self.header_visible),
            "scrollable": bool(self.scrollable),
            "footer_label_visible": bool(self.footer_label_visible),
            "footer_label": self.footer_label,
            "footer_columns": int(self.footer_columns),
            "footer_button_style": self.footer_button_style,
            "primary_actions_visible": bool(self.primary_actions_visible),
            "primary_actions_label_visible": bool(
                self.primary_actions_label_visible
            ),
            "primary_actions_label": self.primary_actions_label,
            "primary_action_columns": int(self.primary_action_columns),
            "scrollbar_width": self.scrollbar_width,
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
    sidebar_config: SidebarConfig = field(default_factory=SidebarConfig)
    primary_actions: Tuple[GuiActionButton, ...] = field(default_factory=tuple)
    maximize_on_start: bool = True
    restart_on_appearance_change: bool = True
    restart_delay_ms: int = 350
    icon_path: str | None = None
    icon_png_path: str | None = None
    theme_config: ThemeConfig = field(default_factory=ThemeConfig)
    preferences: GuiPreferences = field(default_factory=GuiPreferences)
    visual_preferences: str = "advanced"
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
    def resolved_visual_preferences(self) -> str:
        return normalize_visual_preferences_mode(self.visual_preferences)

    @property
    def resolved_footer_items(self) -> Tuple[GuiMenuItem, ...]:
        items = tuple(self.footer_items)
        if self.resolved_visual_preferences == VISUAL_PREFERENCES_NONE:
            return tuple(item for item in items if item.key != "settings")
        return items

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
            "sidebar_config": self.sidebar_config.to_dict(),
            "primary_actions": [item.to_dict() for item in self.primary_actions],
            "maximize_on_start": self.maximize_on_start,
            "restart_on_appearance_change": self.restart_on_appearance_change,
            "restart_delay_ms": self.restart_delay_ms,
            "icon_path": self.icon_path,
            "icon_png_path": self.icon_png_path,
            "theme_config": self.theme_config.to_dict(),
            "preferences": self.preferences.to_dict(),
            "visual_preferences": self.resolved_visual_preferences,
            "help_text": self.help_text,
            "about_text": self.about_text,
            "footer_items": [item.to_dict() for item in self.resolved_footer_items],
        }
