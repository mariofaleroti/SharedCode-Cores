"""ConfigCore public API."""

from .access import get_nested_value, has_nested_key, normalize_config_path
from .loader import load_config, load_json_file
from .merger import deep_merge
from .models import ConfigIssue, ConfigLoadResult, ConfigValidationResult
from .validator import validate_config_data
from .writer import create_config_contract, write_config_contract, write_json_file

__all__ = [
    "ConfigIssue",
    "ConfigLoadResult",
    "ConfigValidationResult",
    "create_config_contract",
    "deep_merge",
    "get_nested_value",
    "has_nested_key",
    "load_config",
    "load_json_file",
    "normalize_config_path",
    "validate_config_data",
    "write_config_contract",
    "write_json_file",
]
