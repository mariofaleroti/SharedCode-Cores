from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any


def render_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    try:
        return json.dumps(value, ensure_ascii=False, default=str)
    except TypeError:
        return str(value)


def safe_filename(value: str, fallback: str = "report") -> str:
    chars: list[str] = []
    for char in value.strip().lower():
        if char.isalnum():
            chars.append(char)
        elif char in (" ", "_", "-", "."):
            chars.append("_")
    safe = "".join(chars).strip("_.")
    while "__" in safe:
        safe = safe.replace("__", "_")
    return safe or fallback


def default_output_path(input_path: Path, output_format: str, output_dir: Path | None = None) -> Path:
    base_dir = output_dir if output_dir else input_path.parent
    suffix = ".xlsx" if output_format == "xlsx" else f".{output_format}"
    return base_dir / f"{input_path.stem}{suffix}"


def status_class(status: str) -> str:
    value = (status or "").lower().strip()
    if value in {"ok", "healthy", "success", "passed", "normal"}:
        return "ok"
    if value in {"warning", "warn", "degraded", "attention", "medium"}:
        return "warning"
    if value in {"critical", "error", "failed", "fail", "high"}:
        return "critical"
    return "info"
