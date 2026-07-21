from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class RenderOptions:
    input_path: Path
    output_path: Path | None = None
    output_dir: Path | None = None
    output_format: str = "html"
    template_dir: Path | None = None
    profile: str | None = None
    theme: str = "dark"
    strict: bool = False
    overwrite: bool = True

    @property
    def normalized_format(self) -> str:
        return self.output_format.lower().strip()
