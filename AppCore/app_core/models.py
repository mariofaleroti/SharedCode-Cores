"""Data models used by AppCore."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Optional

from .constants import (
    APP_STATUS_OK,
    DEFAULT_TOOL_VERSION,
    EXIT_CODE_OK,
)

ToolHandler = Callable[["AppContext"], Any]


@dataclass(frozen=True)
class AppSettings:
    """Static settings used to bootstrap a tool application."""

    tool_name: str
    tool_version: str = DEFAULT_TOOL_VERSION
    description: str = ""
    default_exit_code: int = EXIT_CODE_OK
    capture_unhandled_exceptions: bool = True


@dataclass
class AppContext:
    """Runtime objects shared with a concrete tool handler.

    DESIGN: AppCore does not create or validate these objects itself. Other cores
    can provide them and AppCore simply carries them through the lifecycle.
    """

    settings: AppSettings
    cli_options: Any = None
    runtime: Any = None
    logger: Any = None
    config: Any = None
    state: Dict[str, Any] = field(default_factory=dict)

    @property
    def tool_name(self) -> str:
        """Return the tool name configured for this application."""

        return self.settings.tool_name

    @property
    def tool_version(self) -> str:
        """Return the tool version configured for this application."""

        return self.settings.tool_version

    def set_state(self, key: str, value: Any) -> None:
        """Store a runtime value for later lifecycle steps."""

        self.state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Read a runtime value stored in the context."""

        return self.state.get(key, default)


@dataclass
class AppRunResult:
    """Structured result produced by the AppCore lifecycle."""

    status: str = APP_STATUS_OK
    exit_code: int = EXIT_CODE_OK
    duration_ms: int = 0
    error: Optional[Dict[str, Any]] = None
    context: Optional[AppContext] = None

    @property
    def succeeded(self) -> bool:
        """Return True when the lifecycle ended successfully."""

        return self.exit_code == EXIT_CODE_OK and self.error is None

    def to_dict(self) -> Dict[str, Any]:
        """Return a JSON-safe representation of the run result."""

        return {
            "status": self.status,
            "exit_code": self.exit_code,
            "duration_ms": self.duration_ms,
            "error": self.error,
            "tool": {
                "name": self.context.tool_name if self.context else None,
                "version": self.context.tool_version if self.context else None,
            },
        }
