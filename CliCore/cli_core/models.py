"""Models used by CliCore."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class CliOptions:
    """Normalized common CLI options shared by ecosystem tools."""

    config_path: Optional[Path] = None
    output_dir: Optional[Path] = None
    logs_dir: Optional[Path] = None
    json_output: Optional[Path] = None
    quiet: bool = False
    verbose: int = 0
    debug: bool = False
    no_pause: bool = False
    validate_config: bool = False

    @classmethod
    def from_namespace(cls, namespace: argparse.Namespace) -> "CliOptions":
        """Build common CLI options from an argparse namespace."""

        return cls(
            config_path=getattr(namespace, "config_path", None),
            output_dir=getattr(namespace, "output_dir", None),
            logs_dir=getattr(namespace, "logs_dir", None),
            json_output=getattr(namespace, "json_output", None),
            quiet=bool(getattr(namespace, "quiet", False)),
            verbose=int(getattr(namespace, "verbose", 0) or 0),
            debug=bool(getattr(namespace, "debug", False)),
            no_pause=bool(getattr(namespace, "no_pause", False)),
            validate_config=bool(getattr(namespace, "validate_config", False)),
        )

    @property
    def log_level(self) -> str:
        """Return a practical log level derived from verbosity flags."""

        if self.debug or self.verbose >= 2:
            return "debug"
        if self.quiet:
            return "warning"
        return "info"

    @property
    def should_print_human_output(self) -> bool:
        """Return whether regular human-readable output should be printed."""

        return not self.quiet

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation of the common CLI options."""

        return {
            "config_path": str(self.config_path) if self.config_path is not None else None,
            "output_dir": str(self.output_dir) if self.output_dir is not None else None,
            "logs_dir": str(self.logs_dir) if self.logs_dir is not None else None,
            "json_output": str(self.json_output) if self.json_output is not None else None,
            "quiet": self.quiet,
            "verbose": self.verbose,
            "debug": self.debug,
            "no_pause": self.no_pause,
            "validate_config": self.validate_config,
            "log_level": self.log_level,
        }
