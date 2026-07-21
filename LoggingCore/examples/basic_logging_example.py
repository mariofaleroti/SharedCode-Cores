#!/usr/bin/env python3
"""
Basic LoggingCore usage example.
"""

from __future__ import annotations

from pathlib import Path
import sys

CURRENT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = CURRENT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

from logging_core import create_logger  # noqa: E402


def main() -> int:
    logger = create_logger(
        name="ExampleTool",
        log_path=PROJECT_ROOT / "output" / "logs" / "example_tool.log",
    )

    logger.info("Scan started", code="SCAN_STARTED")
    logger.warning(
        "Directory skipped",
        code="DIRECTORY_SKIPPED",
        context={"path": "C:/Temp/node_modules"},
    )
    logger.error(
        "Permission denied",
        code="PERMISSION_DENIED",
        context={"path": "C:/Protected"},
    )

    print("Diagnostics:")
    for item in logger.get_diagnostics():
        print(item)

    print()
    print("Errors:")
    for item in logger.get_errors():
        print(item)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
