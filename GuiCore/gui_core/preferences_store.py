from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .preferences import GuiPreferences


def load_preferences_from_json(path: str | Path) -> GuiPreferences:
    """Load GuiCore visual preferences from a JSON file.

    Missing or invalid files fall back to default preferences. This helper is
    intentionally small: concrete tools can use ConfigCore instead and only pass
    a GuiPreferences object into GuiAppConfig.
    """

    file_path = Path(path)
    if not file_path.exists():
        return GuiPreferences()
    try:
        raw_data: Any = json.loads(file_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return GuiPreferences()
    if not isinstance(raw_data, dict):
        return GuiPreferences()
    return GuiPreferences.from_mapping(raw_data)


def save_preferences_to_json(path: str | Path, preferences: GuiPreferences) -> None:
    """Persist GuiCore visual preferences to a JSON file.

    The stored values are normalized raw values, so they can be passed directly
    to GuiPreferences.from_mapping on the next app start.
    """

    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    normalized = preferences.normalized()
    data = {
        "appearance_mode": normalized.appearance_mode,
        "color_theme": normalized.color_theme,
        "font_family": normalized.font_family,
        "font_size": normalized.font_size,
        "table_density": normalized.table_density,
        "surface_theme": normalized.surface_theme,
    }
    file_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
