#!/usr/bin/env python3
"""Basic AppCore bootstrap example."""

from __future__ import annotations

from app_core import run_tool_app


class ConsoleLogger:
    """Tiny logger used only for the example."""

    def info(self, message: str, **_: object) -> None:
        print(f"INFO: {message}")

    def error(self, message: str, **_: object) -> None:
        print(f"ERROR: {message}")


def run_example_tool(context):
    """Run tool-specific logic."""

    context.logger.info(f"Running {context.tool_name} {context.tool_version}")
    context.set_state("items_processed", 3)
    return 0


def main() -> int:
    """Application entry point."""

    return run_tool_app(
        tool_name="ExampleTool",
        tool_version="0.1.0",
        description="Example tool using AppCore.",
        logger=ConsoleLogger(),
        run_handler=run_example_tool,
    )


if __name__ == "__main__":
    raise SystemExit(main())
