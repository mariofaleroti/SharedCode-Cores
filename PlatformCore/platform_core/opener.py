"""Open/reveal filesystem paths through the current operating system."""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .constants import PLATFORM_LINUX, PLATFORM_WINDOWS
from .detection import get_platform_name
from .exceptions import UnsupportedPlatformError
from .paths import normalize_path


@dataclass(frozen=True)
class OpenCommand:
    """Command description used to open or reveal a path."""

    command: tuple[str, ...]
    platform_name: str
    target_path: Path

    def to_list(self) -> list[str]:
        return list(self.command)


def build_open_path_command(path: str | os.PathLike[str], *, platform_name: str | None = None) -> OpenCommand:
    """Build the command used by non-Windows open operations.

    Windows normally uses ``os.startfile`` for native shell behavior. The command
    representation is still useful for dry-runs, tests and diagnostics.
    """

    current_platform = platform_name or get_platform_name()
    target = normalize_path(path, resolve=False)

    if current_platform == PLATFORM_WINDOWS:
        return OpenCommand(("explorer", str(target)), current_platform, target)
    if current_platform == PLATFORM_LINUX:
        return OpenCommand(("xdg-open", str(target)), current_platform, target)
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def build_open_folder_command(path: str | os.PathLike[str], *, platform_name: str | None = None) -> OpenCommand:
    """Build the command used to open a folder."""

    target = normalize_path(path, resolve=False)
    folder = target if target.is_dir() else target.parent
    return build_open_path_command(folder, platform_name=platform_name)


def build_reveal_in_folder_command(path: str | os.PathLike[str], *, platform_name: str | None = None) -> OpenCommand:
    """Build the best-effort command used to reveal a path in the file manager."""

    current_platform = platform_name or get_platform_name()
    target = normalize_path(path, resolve=False)

    if current_platform == PLATFORM_WINDOWS:
        return OpenCommand(("explorer", "/select,", str(target)), current_platform, target)
    if current_platform == PLATFORM_LINUX:
        folder = target if target.is_dir() else target.parent
        return OpenCommand(("xdg-open", str(folder)), current_platform, target)
    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def _run_command(command: OpenCommand) -> None:
    subprocess.Popen(command.to_list(), close_fds=True)  # noqa: S603 - command is controlled by PlatformCore


def _open_windows_path(target: Path) -> None:
    """Open a Windows path with a reliable native-shell strategy.

    PDF files are delegated to Explorer first. In some Windows setups,
    ``os.startfile`` returns without surfacing an association failure for PDFs,
    while Explorer correctly hands the file to the configured PDF application.
    Other file types keep the normal ``os.startfile(..., "open")`` behavior.
    """

    startfile = getattr(os, "startfile", None)

    if target.suffix.lower() == ".pdf":
        try:
            _run_command(build_open_path_command(target, platform_name=PLATFORM_WINDOWS))
            return
        except OSError:
            # Fall back to ShellExecute through os.startfile when Explorer
            # cannot be launched directly.
            pass

    if callable(startfile):
        startfile(str(target), "open")
        return

    _run_command(build_open_path_command(target, platform_name=PLATFORM_WINDOWS))


def open_path(path: str | os.PathLike[str]) -> None:
    """Open a file or directory with the native OS handler."""

    current_platform = get_platform_name()
    target = normalize_path(path, resolve=False)

    if current_platform == PLATFORM_WINDOWS:
        _open_windows_path(target)
        return

    if current_platform == PLATFORM_LINUX:
        _run_command(build_open_path_command(target, platform_name=current_platform))
        return

    raise UnsupportedPlatformError(f"Unsupported platform: {current_platform}")


def open_folder(path: str | os.PathLike[str]) -> None:
    """Open a folder, or the parent folder when a file path is provided."""

    _run_command(build_open_folder_command(path))


def reveal_in_folder(path: str | os.PathLike[str]) -> None:
    """Reveal a file in the system file manager when supported.

    Linux support is best-effort: it opens the parent directory because there is
    no universal freedesktop command for selecting one file across all desktops.
    """

    _run_command(build_reveal_in_folder_command(path))
