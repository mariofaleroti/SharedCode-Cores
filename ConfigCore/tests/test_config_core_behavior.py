from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from typing import Any

from config_core import (
    create_config_contract,
    deep_merge,
    get_nested_value,
    has_nested_key,
    load_config,
    validate_config_data,
    write_config_contract,
    write_json_file,
)
from config_core.models import ConfigIssue, ConfigValidationResult


class FakeContractValidationResult:
    def __init__(self, *, is_valid: bool, errors: list[ConfigIssue] | None = None, diagnostics: list[ConfigIssue] | None = None) -> None:
        self.is_valid = is_valid
        self.errors = errors or []
        self.diagnostics = diagnostics or []


class ConfigCoreBehaviorTests(unittest.TestCase):
    def test_create_config_contract_uses_standard_root_keys(self) -> None:
        contract = create_config_contract(
            config_data={"scan": {"max_depth": 5}},
            config_type="example",
            tool_name="ExampleTool",
        )

        self.assertEqual(
            set(contract.keys()),
            {"meta", "summary", "report_brief", "data", "diagnostics", "errors"},
        )
        self.assertEqual(contract["meta"]["file_type"], "config")
        self.assertEqual(contract["meta"]["config_type"], "example")
        self.assertEqual(contract["data"]["scan"]["max_depth"], 5)

    def test_deep_merge_preserves_defaults_and_applies_overrides(self) -> None:
        defaults = {
            "scan": {
                "max_depth": 5,
                "scan_interval_minutes": 20,
            },
            "git": {
                "auto_commit": False,
            },
        }
        overrides = {
            "scan": {
                "max_depth": 3,
            }
        }

        merged = deep_merge(defaults, overrides)

        self.assertEqual(merged["scan"]["max_depth"], 3)
        self.assertEqual(merged["scan"]["scan_interval_minutes"], 20)
        self.assertFalse(merged["git"]["auto_commit"])
        self.assertEqual(defaults["scan"]["max_depth"], 5)

    def test_deep_merge_replaces_lists(self) -> None:
        merged = deep_merge(
            {"scan": {"root_paths": ["C:/Default"]}},
            {"scan": {"root_paths": ["D:/Projects"]}},
        )

        self.assertEqual(merged["scan"]["root_paths"], ["D:/Projects"])

    def test_get_nested_value_and_has_nested_key(self) -> None:
        config = {"scan": {"max_depth": 5}}

        self.assertEqual(get_nested_value(config, "scan.max_depth"), 5)
        self.assertTrue(has_nested_key(config, "scan.max_depth"))
        self.assertFalse(has_nested_key(config, "scan.root_paths"))
        self.assertEqual(get_nested_value(config, "scan.root_paths", default=[]), [])

    def test_validate_config_data_accepts_valid_rules(self) -> None:
        result = validate_config_data(
            {
                "scan": {
                    "root_paths": ["C:/Projects"],
                    "max_depth": 5,
                },
                "git": {
                    "auto_commit": True,
                },
            },
            required_paths=["scan.root_paths"],
            type_rules={
                "scan.root_paths": list,
                "scan.max_depth": int,
                "git.auto_commit": bool,
            },
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.errors, [])

    def test_validate_config_data_reports_missing_required_path(self) -> None:
        result = validate_config_data(
            {"scan": {"max_depth": 5}},
            required_paths=["scan.root_paths"],
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "CONFIG_REQUIRED_PATH_MISSING")
        self.assertEqual(result.errors[0].path, "scan.root_paths")

    def test_validate_config_data_reports_invalid_type(self) -> None:
        result = validate_config_data(
            {"scan": {"max_depth": "5"}},
            type_rules={"scan.max_depth": int},
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "CONFIG_INVALID_TYPE")

    def test_validate_config_data_rejects_bool_for_int(self) -> None:
        result = validate_config_data(
            {"scan": {"max_depth": True}},
            type_rules={"scan.max_depth": int},
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "CONFIG_INVALID_TYPE")

    def test_validate_config_data_reports_disallowed_value(self) -> None:
        result = validate_config_data(
            {"mode": "danger"},
            allowed_values={"mode": ["safe", "normal"]},
        )

        self.assertFalse(result.is_valid)
        self.assertEqual(result.errors[0].code, "CONFIG_VALUE_NOT_ALLOWED")

    def test_write_and_load_contract_config(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            write_config_contract(
                config_data={"scan": {"root_paths": ["C:/Projects"]}},
                output_path=config_path,
                config_type="example",
                tool_name="ExampleTool",
            )

            result = load_config(
                config_path,
                defaults={"scan": {"max_depth": 5}},
                required_paths=["scan.root_paths"],
                type_rules={"scan.root_paths": list, "scan.max_depth": int},
                validate_standard_contract=False,
            )

            self.assertTrue(result.is_valid)
            self.assertEqual(result.config["scan"]["max_depth"], 5)
            self.assertEqual(result.config["scan"]["root_paths"], ["C:/Projects"])

    def test_load_raw_config_without_contract_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "raw_config.json"
            write_json_file({"scan": {"max_depth": 5}}, config_path)

            result = load_config(
                config_path,
                contract_mode=False,
                type_rules={"scan.max_depth": int},
            )

            self.assertTrue(result.is_valid)
            self.assertEqual(result.config["scan"]["max_depth"], 5)

    def test_load_config_reports_missing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            result = load_config(Path(temp_dir) / "missing.json", validate_standard_contract=False)

            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "CONFIG_FILE_NOT_FOUND")

    def test_load_config_reports_invalid_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "broken.json"
            config_path.write_text("{ broken", encoding="utf-8")

            result = load_config(config_path, validate_standard_contract=False)

            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "CONFIG_JSON_LOAD_ERROR")

    def test_load_config_reports_missing_data_object_in_contract_mode(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            write_json_file({"data": []}, config_path)

            result = load_config(config_path, validate_standard_contract=False)

            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "CONFIG_DATA_NOT_OBJECT")

    def test_contract_validator_can_be_injected_successfully(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            write_config_contract(
                config_data={"scan": {"max_depth": 5}},
                output_path=config_path,
                config_type="example",
                tool_name="ExampleTool",
            )

            def fake_validator(raw_content: Any) -> FakeContractValidationResult:
                return FakeContractValidationResult(is_valid=True)

            result = load_config(
                config_path,
                contract_validator=fake_validator,
            )

            self.assertTrue(result.is_valid)

    def test_contract_validator_errors_are_mapped(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            write_config_contract(
                config_data={},
                output_path=config_path,
                config_type="example",
                tool_name="ExampleTool",
            )

            def fake_validator(raw_content: Any) -> FakeContractValidationResult:
                return FakeContractValidationResult(
                    is_valid=False,
                    errors=[ConfigIssue("error", "ROOT_KEY_MISSING", "Root key missing.", path="meta")],
                )

            result = load_config(
                config_path,
                contract_validator=fake_validator,
            )

            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "ROOT_KEY_MISSING")

    def test_missing_contract_validator_is_warning_by_default(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            write_config_contract(
                config_data={},
                output_path=config_path,
                config_type="example",
                tool_name="ExampleTool",
            )

            with patch("config_core.loader._import_json_contract_validator", return_value=None):
                result = load_config(config_path)

            self.assertTrue(result.is_valid)
            self.assertEqual(result.diagnostics[0].code, "JSON_CONTRACT_CORE_UNAVAILABLE")

    def test_require_contract_validator_makes_missing_dependency_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            write_config_contract(
                config_data={},
                output_path=config_path,
                config_type="example",
                tool_name="ExampleTool",
            )

            with patch("config_core.loader._import_json_contract_validator", return_value=None):
                result = load_config(
                    config_path,
                    require_contract_validator=True,
                    contract_validator=None,
                )

            self.assertFalse(result.is_valid)
            self.assertEqual(result.errors[0].code, "JSON_CONTRACT_CORE_UNAVAILABLE")

    def test_public_result_to_dict_is_json_safe(self) -> None:
        validation = ConfigValidationResult()
        validation.add_error("E", "Error message", path="scan.max_depth")

        payload = validation.to_dict()
        encoded = json.dumps(payload)

        self.assertIn("scan.max_depth", encoded)


if __name__ == "__main__":
    unittest.main()
