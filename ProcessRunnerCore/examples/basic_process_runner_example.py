"""Basic ProcessRunnerCore usage example."""

from __future__ import annotations

import sys
from pathlib import Path

CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from process_runner_core import run_process  # noqa: E402


def main() -> int:
    result = run_process(
        [sys.executable, "--version"],
        timeout_seconds=10,
        trim_output=True,
    )

    print(f"Status: {result.status}")
    print(f"Exit code: {result.exit_code}")
    print(f"STDOUT: {result.stdout}")
    print(f"STDERR: {result.stderr}")
    print(f"Duration: {result.duration_ms} ms")

    return 0 if result.succeeded else 1


if __name__ == "__main__":
    raise SystemExit(main())
