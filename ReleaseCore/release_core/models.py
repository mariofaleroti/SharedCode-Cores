from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass(frozen=True)
class ReleaseItem:
    source_path: Path
    target_path: Path
    relative_path: Path
    size_bytes: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_path": str(self.source_path),
            "target_path": str(self.target_path),
            "relative_path": str(self.relative_path),
            "size_bytes": self.size_bytes,
        }


@dataclass
class ReleaseResult:
    source_dir: Path
    release_dir: Path
    files_count: int = 0
    directories_count: int = 0
    total_size_bytes: int = 0
    copied_items: List[ReleaseItem] = field(default_factory=list)
    skipped_paths: List[str] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def succeeded(self) -> bool:
        return not self.errors

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source_dir": str(self.source_dir),
            "release_dir": str(self.release_dir),
            "succeeded": self.succeeded,
            "files_count": self.files_count,
            "directories_count": self.directories_count,
            "total_size_bytes": self.total_size_bytes,
            "copied_items": [item.to_dict() for item in self.copied_items],
            "skipped_paths": list(self.skipped_paths),
            "errors": list(self.errors),
        }
