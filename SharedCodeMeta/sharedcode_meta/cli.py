from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

from . import DISTRIBUTION_NAME, __version__


def main() -> int:
    try:
        installed_version = version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        installed_version = __version__

    print(f"SharedCode cores {installed_version}")
    print("Packages: app_core, cli_core, config_core, date_time_core, file_scan_core,")
    print("          file_system_info_core, gui_core, json_contract_core, logging_core,")
    print("          platform_core, process_runner_core, release_core, render_core,")
    print("          tool_runtime_core")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
