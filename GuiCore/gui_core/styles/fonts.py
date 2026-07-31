from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

APP_FONT_FAMILY_OPTIONS = [
    "Segoe UI",
    "Arial",
    "Calibri",
    "Verdana",
    "Tahoma",
    "Consolas",
]

APP_FONT_SIZE_OPTIONS = [
    "Pequeña",
    "Normal",
    "Grande",
    "Muy grande",
]

APP_FONT_ROLE_SIZES: Dict[str, Dict[str, int]] = {
    "Pequeña": {
        "small": 9,
        "body": 10,
        "list": 9,
        "table": 9,
        "table_heading": 9,
        "section": 13,
        "title": 20,
    },
    "Normal": {
        "small": 10,
        "body": 11,
        "list": 10,
        "table": 10,
        "table_heading": 10,
        "section": 15,
        "title": 22,
    },
    "Grande": {
        "small": 11,
        "body": 12,
        "list": 11,
        "table": 11,
        "table_heading": 11,
        "section": 16,
        "title": 24,
    },
    "Muy grande": {
        "small": 12,
        "body": 13,
        "list": 12,
        "table": 12,
        "table_heading": 12,
        "section": 17,
        "title": 26,
    },
}


@dataclass(frozen=True)
class FontConfig:
    """Shared font preferences for GuiCore applications."""

    family: str = "Segoe UI"
    size_option: str = "Normal"
    size_offset: int = 0

    def size(self, role: str = "body") -> int:
        base_size = get_font_role_size(self.size_option, role)
        return max(8, base_size + int(self.size_offset))

    def tuple(self, role: str = "body", weight: str | None = None) -> Tuple[str, int] | Tuple[str, int, str]:
        values: list[str | int] = [
            normalize_font_family(self.family),
            self.size(role),
        ]
        if weight:
            values.append(weight)
        return tuple(values)  # type: ignore[return-value]

    def with_size_offset(self, size_offset: int) -> "FontConfig":
        return FontConfig(
            family=self.family,
            size_option=self.size_option,
            size_offset=int(size_offset),
        )


def normalize_font_family(font_family: str | None) -> str:
    if font_family in APP_FONT_FAMILY_OPTIONS:
        return str(font_family)
    return "Segoe UI"


def normalize_font_size_option(size_option: str | None) -> str:
    if size_option in APP_FONT_SIZE_OPTIONS:
        return str(size_option)
    return "Normal"


def get_font_role_size(size_option: str | None, role: str = "body") -> int:
    option = normalize_font_size_option(size_option)
    role_sizes = APP_FONT_ROLE_SIZES[option]
    return role_sizes.get(role, role_sizes["body"])


def get_font_tuple(
    font_family: str | None = "Segoe UI",
    size_option: str | None = "Normal",
    role: str = "body",
    weight: str | None = None,
) -> Tuple[str, int] | Tuple[str, int, str]:
    values: list[str | int] = [
        normalize_font_family(font_family),
        get_font_role_size(size_option, role),
    ]
    if weight:
        values.append(weight)
    return tuple(values)  # type: ignore[return-value]
