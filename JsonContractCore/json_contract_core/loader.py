"""JSON loading helpers for JsonContractCore."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_file(file_path: str | Path) -> Any:
    """Load a JSON file using UTF-8 compatible encoding.

    NOTE: utf-8-sig accepts regular UTF-8 and UTF-8 with BOM, which helps when
    JSON files are produced by older PowerShell environments.
    """
    path = Path(file_path)
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)
