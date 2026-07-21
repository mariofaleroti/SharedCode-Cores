"""Command line interface for JsonContractCore validation."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TextIO

from .loader import load_json_file
from .models import ValidationResult
from .validator import validate_contract
from .writer import write_json_file

EXIT_VALID = 0
EXIT_VALIDATION_FAILED = 1
EXIT_RUNTIME_ERROR = 2


def build_parser() -> argparse.ArgumentParser:
    """Build the JsonContractCore CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="json-contract-validator",
        description="Validate one JSON file against the ecosystem contract standard.",
    )
    parser.add_argument(
        "path",
        help="JSON file to validate.",
    )
    parser.add_argument(
        "--strict-schema-version",
        action="store_true",
        help="Treat schema version mismatches as validation errors.",
    )
    parser.add_argument(
        "--allow-extra-root-keys",
        action="store_true",
        help="Allow non-standard root keys without generating warnings.",
    )
    parser.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="Return a failure exit code when warnings are present.",
    )
    parser.add_argument(
        "--json-output",
        help="Write the validation result as JSON to this path.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Only print errors needed for runtime failures.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command line validator and return a stable exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)

    target_path = Path(args.path)
    result = _validate_file_from_args(args, target_path)

    if args.json_output:
        write_json_file(result.to_dict(), args.json_output)

    if not args.quiet:
        print_human_result(result)

    if _has_runtime_error(result):
        return EXIT_RUNTIME_ERROR

    if not result.is_valid:
        return EXIT_VALIDATION_FAILED

    if args.fail_on_warnings and result.warnings:
        return EXIT_VALIDATION_FAILED

    return EXIT_VALID


def _validate_file_from_args(args: argparse.Namespace, target_path: Path) -> ValidationResult:
    if not target_path.exists():
        return _create_runtime_error_result(
            target_path,
            "INPUT_PATH_NOT_FOUND",
            f"Input path does not exist: {target_path}",
        )

    if not target_path.is_file():
        return _create_runtime_error_result(
            target_path,
            "INPUT_PATH_NOT_FILE",
            f"Input path is not a file: {target_path}",
        )

    try:
        payload = load_json_file(target_path)
    except json.JSONDecodeError as error:
        return _create_runtime_error_result(
            target_path,
            "JSON_DECODE_ERROR",
            f"Invalid JSON: {error}",
        )
    except OSError as error:
        return _create_runtime_error_result(
            target_path,
            "JSON_READ_ERROR",
            f"Could not read JSON file: {error}",
        )

    return validate_contract(
        payload,
        source=str(target_path),
        strict_schema_version=args.strict_schema_version,
        allow_extra_root_keys=args.allow_extra_root_keys,
    )


def _create_runtime_error_result(path: Path, code: str, message: str) -> ValidationResult:
    result = ValidationResult(source=str(path))
    result.add_error(code, message, path="$")
    return result


def _has_runtime_error(result: ValidationResult) -> bool:
    runtime_error_codes = {
        "INPUT_PATH_NOT_FOUND",
        "INPUT_PATH_NOT_FILE",
        "JSON_DECODE_ERROR",
        "JSON_READ_ERROR",
    }
    return any(issue.code in runtime_error_codes for issue in result.errors)


def print_human_result(result: ValidationResult, *, stream: TextIO | None = None) -> None:
    """Print a compact human-readable validation summary."""
    output = stream or sys.stdout

    print("=" * 72, file=output)
    print(f"Source: {result.source}", file=output)
    print(f"Status: {result.status}", file=output)
    print(f"Errors: {len(result.errors)}", file=output)
    print(f"Warnings: {len(result.warnings)}", file=output)

    if result.errors:
        print("", file=output)
        print("Errors:", file=output)
        for issue in result.errors:
            location = f" {issue.path}" if issue.path else ""
            print(f"  X [{issue.code}]{location} - {issue.message}", file=output)

    if result.warnings:
        print("", file=output)
        print("Warnings:", file=output)
        for issue in result.warnings:
            location = f" {issue.path}" if issue.path else ""
            print(f"  ! [{issue.code}]{location} - {issue.message}", file=output)


if __name__ == "__main__":
    raise SystemExit(main())
