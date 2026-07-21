from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class PathInfo:
    path: Path
    exists: bool
    is_file: bool = False
    is_dir: bool = False
    is_symlink: bool = False
    name: str = ""
    suffix: str = ""
    parent: Optional[Path] = None
    size_bytes: Optional[int] = None
    created_at_utc: Optional[str] = None
    modified_at_utc: Optional[str] = None
    accessed_at_utc: Optional[str] = None
    created_at_epoch_seconds: Optional[float] = None
    modified_at_epoch_seconds: Optional[float] = None
    accessed_at_epoch_seconds: Optional[float] = None
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "is_file": self.is_file,
            "is_dir": self.is_dir,
            "is_symlink": self.is_symlink,
            "name": self.name,
            "suffix": self.suffix,
            "parent": str(self.parent) if self.parent else None,
            "size_bytes": self.size_bytes,
            "created_at_utc": self.created_at_utc,
            "modified_at_utc": self.modified_at_utc,
            "accessed_at_utc": self.accessed_at_utc,
            "created_at_epoch_seconds": self.created_at_epoch_seconds,
            "modified_at_epoch_seconds": self.modified_at_epoch_seconds,
            "accessed_at_epoch_seconds": self.accessed_at_epoch_seconds,
            "error": self.error,
        }


@dataclass(frozen=True)
class DirectorySummary:
    path: Path
    exists: bool
    files_count: int = 0
    directories_count: int = 0
    symlinks_count: int = 0
    total_file_size_bytes: int = 0
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": str(self.path),
            "exists": self.exists,
            "files_count": self.files_count,
            "directories_count": self.directories_count,
            "symlinks_count": self.symlinks_count,
            "total_file_size_bytes": self.total_file_size_bytes,
            "error": self.error,
        }
