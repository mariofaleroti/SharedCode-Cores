from __future__ import annotations

VISUAL_PREFERENCES_NONE = "none"
VISUAL_PREFERENCES_BASIC = "basic"
VISUAL_PREFERENCES_ADVANCED = "advanced"

VISUAL_PREFERENCE_MODES = (
    VISUAL_PREFERENCES_NONE,
    VISUAL_PREFERENCES_BASIC,
    VISUAL_PREFERENCES_ADVANCED,
)

_VISUAL_PREFERENCE_ALIASES = {
    "none": VISUAL_PREFERENCES_NONE,
    "ninguna": VISUAL_PREFERENCES_NONE,
    "ninguno": VISUAL_PREFERENCES_NONE,
    "disabled": VISUAL_PREFERENCES_NONE,
    "off": VISUAL_PREFERENCES_NONE,
    "basic": VISUAL_PREFERENCES_BASIC,
    "basica": VISUAL_PREFERENCES_BASIC,
    "básica": VISUAL_PREFERENCES_BASIC,
    "simple": VISUAL_PREFERENCES_BASIC,
    "advanced": VISUAL_PREFERENCES_ADVANCED,
    "avanzada": VISUAL_PREFERENCES_ADVANCED,
    "full": VISUAL_PREFERENCES_ADVANCED,
}


def normalize_visual_preferences_mode(value: str | None) -> str:
    """Normalize one visual-preferences mode for the GuiCore 1.1 contract."""

    normalized = str(value or VISUAL_PREFERENCES_ADVANCED).strip().lower()
    return _VISUAL_PREFERENCE_ALIASES.get(
        normalized,
        VISUAL_PREFERENCES_ADVANCED,
    )
