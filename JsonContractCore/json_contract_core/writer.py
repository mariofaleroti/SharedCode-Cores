"""JSON writing helpers for JsonContractCore."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import DEFAULT_JSON_INDENT


def write_json_file(
    payload: Any,
    output_path: str | Path,
    *,
    indent: int = DEFAULT_JSON_INDENT,
    ensure_ascii: bool = False,
    create_parent: bool = True,
) -> Path:
    """Write a JSON file using UTF-8 encoding and return the final path."""
    path = Path(output_path)

    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=ensure_ascii, indent=indent)
        file.write("\n")

    return path
