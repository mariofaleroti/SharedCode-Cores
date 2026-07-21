from __future__ import annotations

import importlib
from types import ModuleType


class GuiDependencyError(RuntimeError):
    """Raised when CustomTkinter is required but not installed."""


def is_customtkinter_available() -> bool:
    """Return True when customtkinter can be imported."""
    return importlib.util.find_spec("customtkinter") is not None


def require_customtkinter() -> ModuleType:
    """Import and return customtkinter, or raise a clear dependency error."""
    try:
        return importlib.import_module("customtkinter")
    except ImportError as error:
        raise GuiDependencyError(
            "CustomTkinter is required to use GuiCore visual components. "
            "Install it with: pip install customtkinter"
        ) from error
