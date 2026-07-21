from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Callable


WINDOW_ICON_PATH_ATTR = "_gui_core_window_icon_path"
WINDOW_ICON_FALLBACK_PATH_ATTR = "_gui_core_window_icon_fallback_path"
WINDOW_ICON_IMAGE_ATTR = "_gui_core_window_icon_image"


@dataclass(frozen=True)
class WindowIconResult:
    """Result of an attempt to apply a window icon."""

    applied: bool
    path: str | None = None
    method: str | None = None
    reason: str = ""

    def to_dict(self) -> dict[str, str | bool | None]:
        return {
            "applied": self.applied,
            "path": self.path,
            "method": self.method,
            "reason": self.reason,
        }


def get_platform_name(platform: str | None = None) -> str:
    """Return the GUI platform bucket used by the icon helper."""

    value = (platform or sys.platform or "").lower()
    if value.startswith("win"):
        return "windows"
    if value.startswith("linux"):
        return "linux"
    return "unsupported"


def coerce_icon_path(path: str | Path | None) -> Path | None:
    """Return a Path for non-empty icon input, otherwise None."""

    if path is None:
        return None
    text = str(path).strip()
    if not text:
        return None
    return Path(text)


def set_window_icon_metadata(
    window: Any,
    icon_path: str | Path | None = None,
    fallback_icon_path: str | Path | None = None,
) -> None:
    """Attach icon metadata to a Tk window so child windows can inherit it."""

    primary = coerce_icon_path(icon_path)
    fallback = coerce_icon_path(fallback_icon_path)
    try:
        setattr(window, WINDOW_ICON_PATH_ATTR, str(primary) if primary is not None else None)
        setattr(window, WINDOW_ICON_FALLBACK_PATH_ATTR, str(fallback) if fallback is not None else None)
    except Exception:
        pass


def get_window_icon_metadata(window: Any) -> tuple[str | None, str | None]:
    """Return icon metadata previously attached to a parent window."""

    primary = getattr(window, WINDOW_ICON_PATH_ATTR, None)
    fallback = getattr(window, WINDOW_ICON_FALLBACK_PATH_ATTR, None)
    return primary, fallback


def resolve_window_icon_path(
    icon_path: str | Path | None = None,
    fallback_icon_path: str | Path | None = None,
    platform: str | None = None,
) -> Path | None:
    """Resolve the best existing icon file for the current GUI platform.

    Windows normally prefers ``.ico``. Linux normally works better with ``.png``
    through Tk's ``iconphoto``. The caller can provide both paths and this helper
    chooses the safest existing candidate without raising if neither exists.
    """

    primary = coerce_icon_path(icon_path)
    fallback = coerce_icon_path(fallback_icon_path)
    candidates: list[Path] = []
    platform_name = get_platform_name(platform)

    if platform_name == "linux" and primary is not None and primary.suffix.lower() == ".ico" and fallback is not None:
        candidates = [fallback, primary]
    elif platform_name == "windows" and primary is not None and primary.suffix.lower() != ".ico" and fallback is not None and fallback.suffix.lower() == ".ico":
        candidates = [fallback, primary]
    else:
        candidates = [candidate for candidate in (primary, fallback) if candidate is not None]

    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        try:
            if candidate.exists() and candidate.is_file():
                return candidate
        except OSError:
            continue
    return None


def _default_photo_image_factory(path: Path) -> Any:
    import tkinter as tk

    return tk.PhotoImage(file=str(path))


def apply_window_icon(
    window: Any,
    icon_path: str | Path | None = None,
    fallback_icon_path: str | Path | None = None,
    platform: str | None = None,
    photo_image_factory: Callable[[Path], Any] | None = None,
) -> WindowIconResult:
    """Apply a Windows/Linux friendly icon to a Tk/CustomTkinter window.

    The helper is intentionally defensive: icon failures should never stop a GUI
    from opening. It returns a small result object for diagnostics and tests.
    """

    set_window_icon_metadata(window, icon_path, fallback_icon_path)
    resolved = resolve_window_icon_path(icon_path, fallback_icon_path, platform=platform)
    if resolved is None:
        return WindowIconResult(False, reason="icon_not_found")

    suffix = resolved.suffix.lower()
    platform_name = get_platform_name(platform)

    if suffix == ".ico" and platform_name == "windows":
        try:
            window.iconbitmap(str(resolved))
            return WindowIconResult(True, str(resolved), "iconbitmap")
        except Exception as exc:
            return WindowIconResult(False, str(resolved), "iconbitmap", f"iconbitmap_failed: {exc}")

    if suffix in {".png", ".gif"}:
        factory = photo_image_factory or _default_photo_image_factory
        try:
            image = factory(resolved)
            window.iconphoto(True, image)
            try:
                setattr(window, WINDOW_ICON_IMAGE_ATTR, image)
            except Exception:
                pass
            return WindowIconResult(True, str(resolved), "iconphoto")
        except Exception as exc:
            return WindowIconResult(False, str(resolved), "iconphoto", f"iconphoto_failed: {exc}")

    # Last-resort fallback for uncommon Tk setups. This keeps .ico useful on
    # platforms where iconbitmap accepts it, without making Linux depend on it.
    try:
        window.iconbitmap(str(resolved))
        return WindowIconResult(True, str(resolved), "iconbitmap")
    except Exception as exc:
        return WindowIconResult(False, str(resolved), "iconbitmap", f"unsupported_icon_format: {exc}")
