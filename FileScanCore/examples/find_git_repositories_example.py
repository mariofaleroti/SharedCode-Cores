"""
Example: detect directories containing a .git marker.

DESIGN:
This example does not validate Git repositories or execute Git commands.
It only demonstrates generic marker detection.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from file_scan_core import find_marker_directories  # noqa: E402


def main() -> int:
    root_path = Path(sys.argv[1]).expanduser() if len(sys.argv) > 1 else Path.cwd()

    result = find_marker_directories(
        root_paths=[root_path],
        marker_name=".git",
        max_depth=6,
        stop_descending_on_match=True,
    )

    print(f"Scanned directories: {result.scanned_count}")
    print(f"Skipped directories: {result.skipped_count}")
    print(f"Matches found: {len(result.matches)}")

    for match in result.matches:
        print(f"- {match.directory_path}")

    if result.errors:
        print("\nNon-fatal scan errors:")
        for error in result.errors:
            print(f"- [{error.error_type}] {error.path}: {error.message}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
