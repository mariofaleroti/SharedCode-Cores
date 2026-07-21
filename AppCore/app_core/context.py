"""Context helpers for AppCore."""

from __future__ import annotations

from typing import Any, Dict, Optional

from .models import AppContext, AppSettings


def create_app_context(
    *,
    tool_name: str,
    tool_version: str = "0.1.0",
    description: str = "",
    cli_options: Any = None,
    runtime: Any = None,
    logger: Any = None,
    config: Any = None,
    state: Optional[Dict[str, Any]] = None,
) -> AppContext:
    """Create a neutral application context for a concrete tool.

    DESIGN: The function accepts objects from other cores, but does not import or
    instantiate them. This keeps AppCore neutral and easy to test.
    """

    settings = AppSettings(
        tool_name=tool_name,
        tool_version=tool_version,
        description=description,
    )

    return AppContext(
        settings=settings,
        cli_options=cli_options,
        runtime=runtime,
        logger=logger,
        config=config,
        state=dict(state or {}),
    )
