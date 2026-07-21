from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from json_contract_core import (
    DEFAULT_SCHEMA_VERSION,
    REQUIRED_ROOT_KEYS,
    ValidationResult,
    create_contract,
    create_diagnostic_entry,
    create_error_entry,
    create_result_contract,
    load_json_file,
    validate_contract,
    write_json_file,
)
from json_contract_core.cli import (
    EXIT_RUNTIME_ERROR,
    EXIT_VALID,
    EXIT_VALIDATION_FAILED,
    main as cli_main,
)


class JsonContractCoreBehaviorTests(unittest.TestCase):
    def test_public_exports_are_available(self) -> None:
        self.assertEqual(DEFAULT_SCHEMA_VERSION, "1.0.0")
        self.assertIn("meta", REQUIRED_ROOT_KEYS)
        self.assertTrue(callable(validate_contract))
        self.assertTrue(callable(create_result_contract))

    def test_valid_result_contract_passes_validation(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={
                "status": "ok",
                "errors_count": 0,
                "diagnostics_count": 0,
            },
            report_brief={
                "title": "Unit test",
                "description": "Validation test.",
            },
            data={"items": []},
        )

        result = validate_contract(contract)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.status, "valid")
        self.assertEqual(len(result.errors), 0)
        self.assertEqual(len(result.warnings), 0)

    def test_root_must_be_object(self) -> None:
        result = validate_contract([])

        self.assertFalse(result.is_valid)
        self.assertEqual(result.status, "invalid")
        self.assertEqual(result.errors[0].code, "ROOT_NOT_OBJECT")

    def test_missing_required_root_keys_are_errors(self) -> None:
        result = validate_contract({})

        self.assertFalse(result.is_valid)
        error_codes = {issue.code for issue in result.errors}
        self.assertIn("ROOT_REQUIRED_KEY_MISSING", error_codes)
        self.assertEqual(len(result.errors), len(REQUIRED_ROOT_KEYS))

    def test_required_root_key_types_are_validated(self) -> None:
        contract = {
            "meta": [],
            "summary": [],
            "report_brief": [],
            "data": [],
            "diagnostics": {},
            "errors": {},
        }

        result = validate_contract(contract)

        self.assertFalse(result.is_valid)
        self.assertTrue(all(issue.code == "ROOT_KEY_INVALID_TYPE" for issue in result.errors))
        self.assertEqual(len(result.errors), 6)

    def test_extra_root_keys_create_warning_by_default(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )
        contract["unexpected"] = True

        result = validate_contract(contract)

        self.assertTrue(result.is_valid)
        self.assertEqual(result.status, "valid_with_warnings")
        self.assertIn("ROOT_EXTRA_KEYS", {issue.code for issue in result.warnings})

    def test_extra_root_keys_can_be_allowed(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )
        contract["unexpected"] = True

        result = validate_contract(contract, allow_extra_root_keys=True)

        self.assertTrue(result.is_valid)
        self.assertNotIn("ROOT_EXTRA_KEYS", {issue.code for issue in result.warnings})

    def test_schema_version_mismatch_is_warning_by_default(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            schema_version="9.9.9",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        result = validate_contract(contract)

        self.assertTrue(result.is_valid)
        self.assertIn("META_SCHEMA_VERSION_UNEXPECTED", {issue.code for issue in result.warnings})

    def test_schema_version_mismatch_can_be_strict_error(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            schema_version="9.9.9",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        result = validate_contract(contract, strict_schema_version=True)

        self.assertFalse(result.is_valid)
        self.assertIn("META_SCHEMA_VERSION_UNEXPECTED", {issue.code for issue in result.errors})

    def test_unknown_file_type_is_warning(self) -> None:
        contract = create_contract(
            file_type="custom_type",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        result = validate_contract(contract)

        self.assertTrue(result.is_valid)
        self.assertIn("META_FILE_TYPE_UNKNOWN", {issue.code for issue in result.warnings})

    def test_recommended_meta_keys_create_warnings(self) -> None:
        contract = create_contract(
            file_type="result",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        result = validate_contract(contract)

        warning_codes = {issue.code for issue in result.warnings}
        self.assertIn("META_RECOMMENDED_SUBTYPE_MISSING", warning_codes)
        self.assertIn("META_TOOL_NAME_MISSING", warning_codes)
        self.assertIn("META_MODULE_NAME_MISSING", warning_codes)

    def test_report_brief_can_be_empty(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            report_brief={},
            data={},
        )

        result = validate_contract(contract)

        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.warnings), 0)

    def test_diagnostics_and_errors_items_must_be_objects(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 1, "diagnostics_count": 1},
            data={},
            diagnostics=["not-object"],
            errors=["not-object"],
        )

        result = validate_contract(contract)

        self.assertFalse(result.is_valid)
        error_codes = {issue.code for issue in result.errors}
        self.assertIn("DIAGNOSTIC_ITEM_INVALID_TYPE", error_codes)
        self.assertIn("ERROR_ITEM_INVALID_TYPE", error_codes)

    def test_error_and_diagnostic_entry_builders(self) -> None:
        error_entry = create_error_entry("TEST_ERROR", "Something failed.")
        diagnostic_entry = create_diagnostic_entry("warning", "TEST_WARNING", "Something should be checked.")

        self.assertEqual(error_entry["code"], "TEST_ERROR")
        self.assertEqual(diagnostic_entry["level"], "warning")

    def test_validation_result_to_dict(self) -> None:
        result = ValidationResult(source="unit-test")
        result.add_warning("TEST_WARNING", "Warning message.", path="$.test")

        payload = result.to_dict()

        self.assertEqual(payload["source"], "unit-test")
        self.assertEqual(payload["status"], "valid_with_warnings")
        self.assertTrue(payload["is_valid"])
        self.assertEqual(payload["warnings_count"], 1)

    def test_write_and_load_json_file_use_utf8(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            report_brief={"title": "Prueba", "description": "Texto con acento."},
            data={"message": "Información"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "nested" / "contract.json"
            returned_path = write_json_file(contract, output_path)
            loaded = load_json_file(returned_path)

            self.assertEqual(returned_path, output_path)
            self.assertEqual(loaded["data"]["message"], "Información")

            raw_text = output_path.read_text(encoding="utf-8")
            self.assertIn("Información", raw_text)


    def test_load_json_file_accepts_utf8_bom(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "bom_contract.json"
            json_path.write_text('{"message": "Información"}', encoding="utf-8-sig")

            loaded = load_json_file(json_path)

            self.assertEqual(loaded["message"], "Información")

    def test_cli_valid_contract_returns_success(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "contract.json"
            write_json_file(contract, json_path)

            exit_code = cli_main([str(json_path), "--quiet"])

            self.assertEqual(exit_code, EXIT_VALID)

    def test_cli_can_write_validation_result_json(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "contract.json"
            output_path = Path(temp_dir) / "validation_result.json"
            write_json_file(contract, json_path)

            exit_code = cli_main([str(json_path), "--quiet", "--json-output", str(output_path)])
            payload = load_json_file(output_path)

            self.assertEqual(exit_code, EXIT_VALID)
            self.assertTrue(payload["is_valid"])
            self.assertEqual(payload["status"], "valid")

    def test_cli_invalid_contract_returns_validation_failure(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "invalid_contract.json"
            write_json_file({"meta": {}}, json_path)

            exit_code = cli_main([str(json_path), "--quiet"])

            self.assertEqual(exit_code, EXIT_VALIDATION_FAILED)

    def test_cli_warnings_do_not_fail_by_default(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )
        contract["unexpected"] = True

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "warning_contract.json"
            write_json_file(contract, json_path)

            exit_code = cli_main([str(json_path), "--quiet"])

            self.assertEqual(exit_code, EXIT_VALID)

    def test_cli_can_fail_on_warnings(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )
        contract["unexpected"] = True

        with tempfile.TemporaryDirectory() as temp_dir:
            json_path = Path(temp_dir) / "warning_contract.json"
            write_json_file(contract, json_path)

            exit_code = cli_main([str(json_path), "--quiet", "--fail-on-warnings"])

            self.assertEqual(exit_code, EXIT_VALIDATION_FAILED)

    def test_cli_missing_file_returns_runtime_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.json"

            exit_code = cli_main([str(missing_path), "--quiet"])

            self.assertEqual(exit_code, EXIT_RUNTIME_ERROR)

    def test_written_contract_is_valid_json(self) -> None:
        contract = create_result_contract(
            result_type="unit_test_result",
            tool_name="UnitTestTool",
            module_name="UnitTestModule",
            summary={"status": "ok", "errors_count": 0, "diagnostics_count": 0},
            data={},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "contract.json"
            write_json_file(contract, output_path)

            with output_path.open("r", encoding="utf-8") as file:
                loaded = json.load(file)

            self.assertEqual(loaded["meta"]["file_type"], "result")


if __name__ == "__main__":
    unittest.main()
