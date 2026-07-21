"""
File writing helpers for LoggingCore.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from .formatters import format_log_line
from .models import LogEntry


class TextLogWriter:
    """Append LogEntry objects to a UTF-8 text log file."""

    def __init__(self, log_path: Path | str) -> None:
        self.log_path = Path(log_path)

    def write(self, entry: LogEntry) -> None:
        """Append a single entry to the log file."""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

        with self.log_path.open("a", encoding="utf-8", newline="\n") as file:
            file.write(format_log_line(entry))
            file.write("\n")


def create_writer(log_path: Optional[Path | str]) -> Optional[TextLogWriter]:
    """Create a TextLogWriter when a path is provided."""
    if log_path is None:
        return None

    return TextLogWriter(log_path)
