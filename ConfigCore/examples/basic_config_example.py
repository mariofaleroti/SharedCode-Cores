from __future__ import annotations

from pathlib import Path

from config_core import load_config, write_config_contract


def main() -> int:
    config_path = Path("output/example_config.json")

    write_config_contract(
        output_path=config_path,
        tool_name="ExampleTool",
        config_type="example_tool",
        config_data={
            "scan": {
                "root_paths": ["C:/Projects"],
            },
            "git": {
                "auto_commit": True,
            },
        },
    )

    result = load_config(
        config_path,
        defaults={
            "scan": {
                "max_depth": 5,
                "scan_interval_minutes": 20,
            },
            "git": {
                "auto_commit": False,
                "commit_message": "Automatic backup",
            },
        },
        required_paths=[
            "scan.root_paths",
        ],
        type_rules={
            "scan.root_paths": list,
            "scan.max_depth": int,
            "git.auto_commit": bool,
        },
        validate_standard_contract=False,
    )

    if not result.is_valid:
        for error in result.errors:
            print(f"ERROR [{error.code}] {error.message}")
        return 1

    print("Configuration loaded successfully.")
    print(result.config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
