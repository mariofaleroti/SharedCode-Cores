from __future__ import annotations

import sys
from pathlib import Path


def get_runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        meipass_path = getattr(sys, "_MEIPASS", None)
        if meipass_path:
            return Path(meipass_path)
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parent


def get_package_root() -> Path:
    return Path(__file__).resolve().parent


def get_default_template_root() -> Path:
    return get_package_root() / "templates"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
