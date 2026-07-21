from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class RenderResult:
    """Resultado estandar de una operacion de render."""

    ok: bool
    format: str
    output_path: Path | None = None
    extra_paths: list[Path] = field(default_factory=list)
    message: str = ""
    errors: list[str] = field(default_factory=list)
    diagnostics: list[dict[str, Any]] = field(default_factory=list)

    def all_paths(self) -> list[Path]:
        paths: list[Path] = []
        if self.output_path is not None:
            paths.append(self.output_path)
        paths.extend(self.extra_paths)
        return paths
