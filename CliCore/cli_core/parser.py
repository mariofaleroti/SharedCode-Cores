"""Base argparse helpers for ecosystem tools."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

from .models import CliOptions


def add_common_arguments(
    parser: argparse.ArgumentParser,
    *,
    version: Optional[str] = None,
) -> argparse.ArgumentParser:
    """Add common ecosystem CLI arguments to an existing parser."""

    group = parser.add_argument_group("common options")

    group.add_argument(
        "--config",
        dest="config_path",
        type=Path,
        help="Path to a JSON configuration file.",
    )
    group.add_argument(
        "--output-dir",
        dest="output_dir",
        type=Path,
        help="Directory where the tool should write its output.",
    )
    group.add_argument(
        "--logs-dir",
        dest="logs_dir",
        type=Path,
        help="Directory where the tool should write log files.",
    )
    group.add_argument(
        "--json-output",
        dest="json_output",
        type=Path,
        help="Path where the tool should write a JSON result when supported.",
    )
    group.add_argument(
        "--quiet",
        action="store_true",
        help="Reduce human-readable output.",
    )
    group.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity. Use -vv for debug-level verbosity.",
    )
    group.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug-oriented output when the tool supports it.",
    )
    group.add_argument(
        "--no-pause",
        action="store_true",
        help="Do not wait for user input before exiting.",
    )
    group.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate configuration and exit when the tool supports it.",
    )

    if version:
        group.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {version}",
        )

    return parser


def create_base_parser(
    *,
    tool_name: str,
    description: Optional[str] = None,
    version: Optional[str] = None,
    add_help: bool = True,
) -> argparse.ArgumentParser:
    """Create a parser with common ecosystem arguments already attached."""

    parser = argparse.ArgumentParser(
        prog=tool_name,
        description=description,
        add_help=add_help,
    )
    add_common_arguments(parser, version=version)
    return parser


def validate_common_argument_combinations(
    parser: argparse.ArgumentParser,
    namespace: argparse.Namespace,
) -> None:
    """Reject contradictory common CLI options."""

    quiet = bool(getattr(namespace, "quiet", False))
    verbose = int(getattr(namespace, "verbose", 0) or 0)
    debug = bool(getattr(namespace, "debug", False))

    if quiet and verbose:
        parser.error("--quiet cannot be combined with --verbose.")

    if quiet and debug:
        parser.error("--quiet cannot be combined with --debug.")


def parse_cli_options(
    parser: argparse.ArgumentParser,
    argv: Optional[Sequence[str]] = None,
) -> CliOptions:
    """Parse common CLI options from a parser."""

    namespace = parser.parse_args(argv)
    validate_common_argument_combinations(parser, namespace)
    return CliOptions.from_namespace(namespace)


def parse_known_cli_options(
    parser: argparse.ArgumentParser,
    argv: Optional[Sequence[str]] = None,
) -> Tuple[CliOptions, List[str]]:
    """Parse common CLI options while preserving unknown arguments."""

    namespace, remaining = parser.parse_known_args(argv)
    validate_common_argument_combinations(parser, namespace)
    return CliOptions.from_namespace(namespace), list(remaining)
