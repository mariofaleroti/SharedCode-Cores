"""CliCore public API."""

from __future__ import annotations

from .constants import EXIT_ERROR, EXIT_OK, EXIT_USAGE_ERROR
from .exit_codes import exit_code_from_success, exit_code_from_validation
from .models import CliOptions
from .parser import (
    add_common_arguments,
    create_base_parser,
    parse_cli_options,
    parse_known_cli_options,
    validate_common_argument_combinations,
)

__all__ = [
    "EXIT_ERROR",
    "EXIT_OK",
    "EXIT_USAGE_ERROR",
    "CliOptions",
    "add_common_arguments",
    "create_base_parser",
    "exit_code_from_success",
    "exit_code_from_validation",
    "parse_cli_options",
    "parse_known_cli_options",
    "validate_common_argument_combinations",
]
