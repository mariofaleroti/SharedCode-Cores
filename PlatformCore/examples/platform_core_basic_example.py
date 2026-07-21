from __future__ import annotations

from platform_core import get_config_dir, get_logs_dir, get_platform_name


def main() -> None:
    tool_name = "ExampleTool"
    print("platform:", get_platform_name())
    print("config:", get_config_dir(tool_name))
    print("logs:", get_logs_dir(tool_name))


if __name__ == "__main__":
    main()
