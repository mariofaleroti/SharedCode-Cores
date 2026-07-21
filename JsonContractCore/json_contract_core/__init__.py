"""Public API for JsonContractCore."""

from __future__ import annotations

from .builder import (
    create_contract,
    create_diagnostic_entry,
    create_error_entry,
    create_result_contract,
)
from .constants import (
    ALLOWED_FILE_TYPES,
    DEFAULT_SCHEMA_VERSION,
    REQUIRED_ROOT_KEYS,
)
from .loader import load_json_file
from .models import ValidationIssue, ValidationResult
from .validator import validate_contract
from .writer import write_json_file

__all__ = [
    "ALLOWED_FILE_TYPES",
    "DEFAULT_SCHEMA_VERSION",
    "REQUIRED_ROOT_KEYS",
    "ValidationIssue",
    "ValidationResult",
    "create_contract",
    "create_diagnostic_entry",
    "create_error_entry",
    "create_result_contract",
    "load_json_file",
    "validate_contract",
    "write_json_file",
]
