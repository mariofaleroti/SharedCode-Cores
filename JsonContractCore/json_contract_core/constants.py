"""Shared constants for JsonContractCore."""

from __future__ import annotations

DEFAULT_SCHEMA_VERSION = "1.0.0"

REQUIRED_ROOT_OBJECT_KEYS = frozenset(
    {
        "meta",
        "summary",
        "report_brief",
        "data",
    }
)

REQUIRED_ROOT_LIST_KEYS = frozenset(
    {
        "diagnostics",
        "errors",
    }
)

REQUIRED_ROOT_KEYS = REQUIRED_ROOT_OBJECT_KEYS | REQUIRED_ROOT_LIST_KEYS

ALLOWED_FILE_TYPES = frozenset(
    {
        "manifest",
        "config",
        "report",
        "result",
        "state",
        "profile",
    }
)

RECOMMENDED_SUBTYPE_KEY_BY_FILE_TYPE = {
    "manifest": "manifest_type",
    "config": "config_type",
    "report": "report_type",
    "result": "result_type",
    "state": "state_type",
    "profile": "profile_type",
}

DEFAULT_JSON_INDENT = 2
