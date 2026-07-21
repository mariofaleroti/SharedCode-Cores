from __future__ import annotations

from pathlib import Path

from tool_runtime_core import create_runtime_context


def main() -> int:
    runtime = create_runtime_context(
        tool_name="ExampleTool",
        tool_version="0.1.0",
        base_dir=Path.cwd(),
    )

    print("Runtime context created")
    print(f"Tool: {runtime.tool_name} {runtime.tool_version}")
    print(f"Run ID: {runtime.run_id}")
    print(f"Output: {runtime.output_dir}")
    print(f"Logs: {runtime.logs_dir}")
    print(f"Default log path: {runtime.get_log_path()}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
