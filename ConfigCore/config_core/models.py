"""Data models used by ConfigCore."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class ConfigIssue:
    """Structured configuration issue."""

    level: str
    code: str
    message: str
    path: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "level": self.level,
            "code": self.code,
            "message": self.message,
        }
        if self.path:
            payload["path"] = self.path
        if self.context:
            payload["context"] = self.context
        return payload


@dataclass
class ConfigValidationResult:
    """Result returned by standalone configuration validation."""

    is_valid: bool = True
    errors: List[ConfigIssue] = field(default_factory=list)
    diagnostics: List[ConfigIssue] = field(default_factory=list)

    def add_error(
        self,
        code: str,
        message: str,
        *,
        path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.is_valid = False
        self.errors.append(
            ConfigIssue(
                level="error",
                code=code,
                message=message,
                path=path,
                context=context or {},
            )
        )

    def add_warning(
        self,
        code: str,
        message: str,
        *,
        path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.diagnostics.append(
            ConfigIssue(
                level="warning",
                code=code,
                message=message,
                path=path,
                context=context or {},
            )
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "errors": [item.to_dict() for item in self.errors],
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }


@dataclass
class ConfigLoadResult:
    """Result returned when loading and validating a configuration file."""

    source: str
    is_valid: bool = True
    config: Dict[str, Any] = field(default_factory=dict)
    raw_content: Optional[Any] = None
    errors: List[ConfigIssue] = field(default_factory=list)
    diagnostics: List[ConfigIssue] = field(default_factory=list)

    def add_error(
        self,
        code: str,
        message: str,
        *,
        path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.is_valid = False
        self.errors.append(
            ConfigIssue(
                level="error",
                code=code,
                message=message,
                path=path,
                context=context or {},
            )
        )

    def add_warning(
        self,
        code: str,
        message: str,
        *,
        path: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.diagnostics.append(
            ConfigIssue(
                level="warning",
                code=code,
                message=message,
                path=path,
                context=context or {},
            )
        )

    def extend_validation(self, validation: ConfigValidationResult) -> None:
        if not validation.is_valid:
            self.is_valid = False
        self.errors.extend(validation.errors)
        self.diagnostics.extend(validation.diagnostics)

    @property
    def has_warnings(self) -> bool:
        return bool(self.diagnostics)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "is_valid": self.is_valid,
            "config": self.config,
            "errors": [item.to_dict() for item in self.errors],
            "diagnostics": [item.to_dict() for item in self.diagnostics],
        }

    @classmethod
    def from_path(cls, path: Path) -> "ConfigLoadResult":
        return cls(source=str(path))
