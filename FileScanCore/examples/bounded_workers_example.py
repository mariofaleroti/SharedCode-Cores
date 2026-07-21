"""Minimal producer-consumer example for FileScanCore bounded workers."""

from __future__ import annotations

from pathlib import Path

from file_scan_core import process_with_bounded_workers


def read_candidate(path: Path) -> int:
    """Example worker: returns file size without adding tool-specific behavior."""

    return path.stat().st_size


def main() -> None:
    candidates = (path for path in Path.cwd().iterdir() if path.is_file())
    result = process_with_bounded_workers(
        candidates,
        read_candidate,
        max_workers=4,
        queue_capacity=40,
        preserve_input_order=True,
    )

    for task in result.succeeded_results:
        print(task.item, task.value)

    print(result.stats)


if __name__ == "__main__":
    main()
