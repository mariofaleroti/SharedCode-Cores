from __future__ import annotations

import os
import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path

from platform_core import (
    PLATFORM_LINUX,
    PLATFORM_UNSUPPORTED,
    PLATFORM_WINDOWS,
    UnsupportedPlatformError,
    build_open_folder_command,
    build_open_path_command,
    build_reveal_in_folder_command,
    get_app_data_dir,
    get_cache_dir,
    get_config_dir,
    get_documents_dir,
    get_executable_suffix,
    get_logs_dir,
    get_platform_name,
    get_script_suffix,
    is_hidden,
    is_linux,
    is_supported_platform,
    is_symlink_or_reparse,
    is_windows,
    normalize_path,
    normalize_tool_name,
    open_path,
    path_to_display,
    resolve_portable_path,
    resolve_portable_paths,
)


class PlatformCoreBehaviorTests(unittest.TestCase):
    def test_platform_detection_normalizes_windows_and_linux(self) -> None:
        self.assertEqual(get_platform_name(system_name="Windows", sys_platform="win32"), PLATFORM_WINDOWS)
        self.assertEqual(get_platform_name(system_name="Linux", sys_platform="linux"), PLATFORM_LINUX)
        self.assertEqual(get_platform_name(system_name="Darwin", sys_platform="darwin"), PLATFORM_UNSUPPORTED)
        self.assertTrue(is_windows(PLATFORM_WINDOWS))
        self.assertTrue(is_linux(PLATFORM_LINUX))
        self.assertFalse(is_supported_platform(PLATFORM_UNSUPPORTED))

    def test_normalize_tool_name_rejects_empty_and_removes_path_chars(self) -> None:
        self.assertEqual(normalize_tool_name(" Smart/Filter:* "), "Smart_Filter")
        with self.assertRaises(ValueError):
            normalize_tool_name("  ")

    def test_normalize_path_and_display_keep_pathlike_values(self) -> None:
        path = normalize_path("~/Example", expand_user=False)
        self.assertIsInstance(path, Path)
        self.assertEqual(str(path), "~/Example")
        self.assertEqual(path_to_display(Path("folder") / "file.txt"), str(Path("folder") / "file.txt"))

    def test_windows_directories_use_local_app_data(self) -> None:
        env = {
            "LOCALAPPDATA": r"C:\Users\Tester\AppData\Local",
            "USERPROFILE": r"C:\Users\Tester",
        }
        home = Path("C:/Users/Tester")

        self.assertEqual(
            get_documents_dir(platform_name=PLATFORM_WINDOWS, env=env, home=home),
            Path(r"C:\Users\Tester") / "Documents",
        )
        self.assertEqual(
            get_app_data_dir("SmartFilter", platform_name=PLATFORM_WINDOWS, env=env, home=home),
            Path(r"C:\Users\Tester\AppData\Local") / "SmartFilter",
        )
        self.assertEqual(
            get_config_dir("SmartFilter", platform_name=PLATFORM_WINDOWS, env=env, home=home),
            Path(r"C:\Users\Tester\AppData\Local") / "SmartFilter" / "config",
        )
        self.assertEqual(
            get_logs_dir("SmartFilter", platform_name=PLATFORM_WINDOWS, env=env, home=home),
            Path(r"C:\Users\Tester\AppData\Local") / "SmartFilter" / "logs",
        )
        self.assertEqual(
            get_cache_dir("SmartFilter", platform_name=PLATFORM_WINDOWS, env=env, home=home),
            Path(r"C:\Users\Tester\AppData\Local") / "SmartFilter" / "cache",
        )

    def test_linux_directories_follow_xdg_when_present(self) -> None:
        env = {
            "XDG_CONFIG_HOME": "/tmp/xdg_config",
            "XDG_DATA_HOME": "/tmp/xdg_data",
            "XDG_STATE_HOME": "/tmp/xdg_state",
            "XDG_CACHE_HOME": "/tmp/xdg_cache",
        }
        home = Path("/home/tester")

        self.assertEqual(get_documents_dir(platform_name=PLATFORM_LINUX, env=env, home=home), home / "Documents")
        self.assertEqual(get_app_data_dir("SmartFilter", platform_name=PLATFORM_LINUX, env=env, home=home), Path("/tmp/xdg_data") / "SmartFilter")
        self.assertEqual(get_config_dir("SmartFilter", platform_name=PLATFORM_LINUX, env=env, home=home), Path("/tmp/xdg_config") / "SmartFilter")
        self.assertEqual(get_logs_dir("SmartFilter", platform_name=PLATFORM_LINUX, env=env, home=home), Path("/tmp/xdg_state") / "SmartFilter" / "logs")
        self.assertEqual(get_cache_dir("SmartFilter", platform_name=PLATFORM_LINUX, env=env, home=home), Path("/tmp/xdg_cache") / "SmartFilter")

    def test_linux_directories_use_xdg_fallbacks(self) -> None:
        home = Path("/home/tester")
        env: dict[str, str] = {}

        self.assertEqual(get_app_data_dir("Tool", platform_name=PLATFORM_LINUX, env=env, home=home), home / ".local" / "share" / "Tool")
        self.assertEqual(get_config_dir("Tool", platform_name=PLATFORM_LINUX, env=env, home=home), home / ".config" / "Tool")
        self.assertEqual(get_logs_dir("Tool", platform_name=PLATFORM_LINUX, env=env, home=home), home / ".local" / "state" / "Tool" / "logs")
        self.assertEqual(get_cache_dir("Tool", platform_name=PLATFORM_LINUX, env=env, home=home), home / ".cache" / "Tool")


    def test_resolve_portable_path_expands_shared_tokens(self) -> None:
        home = Path("/home/tester")
        base_dir = home / "Projects" / "ShadowBackup"
        config_dir = base_dir / "config"
        output_dir = base_dir / "output"

        self.assertEqual(
            resolve_portable_path(
                "${DOCUMENTS}/Proyectos",
                base_dir=base_dir,
                config_dir=config_dir,
                output_dir=output_dir,
                platform_name=PLATFORM_LINUX,
                env={},
                home=home,
            ),
            home / "Documents" / "Proyectos",
        )
        self.assertEqual(
            resolve_portable_path(
                "config/settings.json",
                base_dir=base_dir,
                platform_name=PLATFORM_LINUX,
                env={},
                home=home,
            ),
            base_dir / "config" / "settings.json",
        )
        self.assertEqual(
            resolve_portable_paths(
                ("${CONFIG_DIR}/a.json", "${OUTPUT_DIR}/b.json"),
                base_dir=base_dir,
                config_dir=config_dir,
                output_dir=output_dir,
                platform_name=PLATFORM_LINUX,
                env={},
                home=home,
            ),
            [config_dir / "a.json", output_dir / "b.json"],
        )

    def test_resolve_portable_path_rejects_unknown_token(self) -> None:
        with self.assertRaises(ValueError):
            resolve_portable_path("${UNKNOWN_TOKEN}/file.txt", base_dir="/tmp")

    def test_unsupported_platform_raises_for_platform_specific_paths(self) -> None:
        with self.assertRaises(UnsupportedPlatformError):
            get_config_dir("Tool", platform_name=PLATFORM_UNSUPPORTED, env={}, home="/tmp")

    def test_open_command_builders_are_platform_specific(self) -> None:
        target = Path("/tmp/report.html")

        linux_open = build_open_path_command(target, platform_name=PLATFORM_LINUX)
        self.assertEqual(linux_open.command, ("xdg-open", str(target)))

        linux_reveal = build_reveal_in_folder_command(target, platform_name=PLATFORM_LINUX)
        self.assertEqual(linux_reveal.command, ("xdg-open", str(target.parent)))

        windows_open = build_open_path_command(r"C:\Temp\report.html", platform_name=PLATFORM_WINDOWS)
        self.assertEqual(windows_open.command[0], "explorer")

        windows_reveal = build_reveal_in_folder_command(r"C:\Temp\report.html", platform_name=PLATFORM_WINDOWS)
        self.assertEqual(windows_reveal.command[0:2], ("explorer", "/select,"))


    def test_windows_pdf_open_prefers_explorer(self) -> None:
        target = Path(r"C:\\Docs\\report.pdf")

        with (
            patch("platform_core.opener.get_platform_name", return_value=PLATFORM_WINDOWS),
            patch("platform_core.opener._run_command") as run_command,
            patch("platform_core.opener.os.startfile", create=True) as startfile,
        ):
            open_path(target)

        run_command.assert_called_once()
        command = run_command.call_args.args[0]
        self.assertEqual(command.command[0], "explorer")
        self.assertEqual(command.target_path, target)
        startfile.assert_not_called()

    def test_windows_non_pdf_open_uses_startfile_open_verb(self) -> None:
        target = Path(r"C:\\Docs\\report.docx")

        with (
            patch("platform_core.opener.get_platform_name", return_value=PLATFORM_WINDOWS),
            patch("platform_core.opener._run_command") as run_command,
            patch("platform_core.opener.os.startfile", create=True) as startfile,
        ):
            open_path(target)

        startfile.assert_called_once_with(str(target), "open")
        run_command.assert_not_called()

    def test_open_folder_uses_parent_when_target_is_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "report.html"
            file_path.write_text("ok", encoding="utf-8")

            command = build_open_folder_command(file_path, platform_name=PLATFORM_LINUX)
            self.assertEqual(command.command, ("xdg-open", str(file_path.parent)))

    def test_filesystem_helpers_detect_hidden_and_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            hidden = root / ".hidden"
            hidden.write_text("hidden", encoding="utf-8")
            visible = root / "visible"
            visible.write_text("visible", encoding="utf-8")

            self.assertTrue(is_hidden(hidden))
            self.assertFalse(is_hidden(visible))

            link_path = root / "link"
            try:
                link_path.symlink_to(visible)
            except OSError:
                self.skipTest("Symlink creation is not available in this environment.")
            self.assertTrue(is_symlink_or_reparse(link_path))
            self.assertFalse(is_symlink_or_reparse(visible))

    def test_process_suffixes_are_platform_specific(self) -> None:
        self.assertEqual(get_executable_suffix(PLATFORM_WINDOWS), ".exe")
        self.assertEqual(get_executable_suffix(PLATFORM_LINUX), "")
        self.assertEqual(get_script_suffix(PLATFORM_WINDOWS), ".cmd")
        self.assertEqual(get_script_suffix(PLATFORM_LINUX), ".sh")


if __name__ == "__main__":
    unittest.main()
