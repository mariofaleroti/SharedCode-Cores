"""Configuration writing helpers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from .constants import DEFAULT_CONFIG_FILE_TYPE, DEFAULT_JSON_INDENT, DEFAULT_MODULE_NAME, DEFAULT_SCHEMA_VERSION


def create_config_contract(
    *,
    config_data: Dict[str, Any],
    config_type: str,
    tool_name: str,
    module_name: str = DEFAULT_MODULE_NAME,
    schema_version: str = DEFAULT_SCHEMA_VERSION,
    report_brief: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """Create a standard JSON contract for configuration data."""
    return {
        "meta": {
            "schema_version": schema_version,
            "file_type": DEFAULT_CONFIG_FILE_TYPE,
            "config_type": config_type,
            "tool_name": tool_name,
            "module_name": module_name,
        },
        "summary": {
            "status": "active",
            "errors_count": 0,
            "diagnostics_count": 0,
        },
        "report_brief": report_brief or {},
        "data": config_data,
        "diagnostics": [],
        "errors": [],
    }


def write_json_file(data: Dict[str, Any], output_path: str | Path, *, indent: int = DEFAULT_JSON_INDENT) -> Path:
    """Write JSON data using UTF-8."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=indent)
        file.write("\n")

    return path


def write_config_contract(
    *,
    config_data: Dict[str, Any],
    output_path: str | Path,
    config_type: str,
    tool_name: str,
    module_name: str = DEFAULT_MODULE_NAME,
    report_brief: Dict[str, Any] | None = None,
) -> Path:
    """Create and write a standard configuration contract."""
    contract = create_config_contract(
        config_data=config_data,
        config_type=config_type,
        tool_name=tool_name,
        module_name=module_name,
        report_brief=report_brief,
    )
    return write_json_file(contract, output_path)
