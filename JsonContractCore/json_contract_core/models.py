"""Data models used by JsonContractCore."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    """Represents one validation issue detected in a JSON contract."""

    level: str
    code: str
    message: str
    path: str = ""
    context: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this issue."""
        payload: dict[str, Any] = {
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
class ValidationResult:
    """Structured result returned after validating a JSON contract."""

    source: str = "<memory>"
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        """Return True when no validation errors were found."""
        return not self.errors

    @property
    def status(self) -> str:
        """Return a stable status string for consumers."""
        if self.errors:
            return "invalid"
        if self.warnings:
            return "valid_with_warnings"
        return "valid"

    def add_error(
        self,
        code: str,
        message: str,
        *,
        path: str = "",
        context: dict[str, Any] | None = None,
    ) -> None:
        """Register a validation error."""
        self.errors.append(
            ValidationIssue(
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
        path: str = "",
        context: dict[str, Any] | None = None,
    ) -> None:
        """Register a validation warning."""
        self.warnings.append(
            ValidationIssue(
                level="warning",
                code=code,
                message=message,
                path=path,
                context=context or {},
            )
        )

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serializable representation of this validation result."""
        return {
            "source": self.source,
            "status": self.status,
            "is_valid": self.is_valid,
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "errors": [issue.to_dict() for issue in self.errors],
            "warnings": [issue.to_dict() for issue in self.warnings],
        }
