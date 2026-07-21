"""Shared constants for CliCore."""

from __future__ import annotations

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE_ERROR = 2

DEFAULT_VERBOSE_COUNT = 0

COMMON_ARGUMENT_DESTINATIONS = {
    "config_path",
    "output_dir",
    "logs_dir",
    "json_output",
    "quiet",
    "verbose",
    "debug",
    "no_pause",
    "validate_config",
}
