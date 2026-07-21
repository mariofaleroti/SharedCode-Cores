#!/usr/bin/env python3
"""Basic CliCore usage example."""

from __future__ import annotations

from cli_core import create_base_parser, parse_cli_options


def main() -> int:
    parser = create_base_parser(
        tool_name="ExampleTool",
        description="Example tool using CliCore common arguments.",
        version="0.1.0",
    )
    parser.add_argument(
        "--scan-root",
        help="Example tool-specific option.",
    )

    options = parse_cli_options(parser)

    if options.should_print_human_output:
        print("Common CLI options:")
        for key, value in options.to_dict().items():
            print(f"- {key}: {value}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
