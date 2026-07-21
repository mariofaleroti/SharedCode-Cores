from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from file_scan_core import (
    DEFAULT_SKIPPED_DIRECTORY_NAMES,
    validate_marker_name as exported_validate_marker_name,
    walk_directories,
)
from file_scan_core.markers import (
    directory_contains_marker,
    find_marker_directories,
    validate_marker_name,
)


def _touch(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _relative_paths(paths: list[Path], root_path: Path) -> set[str]:
    return {
        str(path.relative_to(root_path)).replace("\\", "/")
        for path in paths
    }


class FileScanCoreBehaviorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = TemporaryDirectory()
        self.root_path = Path(self.temp_dir.name) / "scan_root"
        self.root_path.mkdir()

        # Marker as a directory. Its internal content must not be traversed by default.
        (self.root_path / "ProjectA" / ".git" / "objects" / "aa").mkdir(parents=True)
        (self.root_path / "ProjectA" / "src").mkdir(parents=True)

        # Marker as a file. This is valid for Git worktrees and some submodule layouts.
        (self.root_path / "ProjectB").mkdir()
        _touch(self.root_path / "ProjectB" / ".git", "gitdir: ../real_git_dir")
        (self.root_path / "ProjectB" / "nested").mkdir()

        # DESIGN: release must remain traversable by default because manifests may live there.
        _touch(self.root_path / "release" / "SmartDisk" / "tool_manifest.json", "{}")
        _touch(
            self.root_path
            / "release"
            / "SmartDisk"
            / "output"
            / "nested_manifest"
            / "tool_manifest.json",
            "{}",
        )

        # Default skipped directory.
        _touch(self.root_path / "node_modules" / "PackageA" / "pyproject.toml", "[project]")

        # Deep marker for max_depth checks.
        (self.root_path / "Deep" / "Level1" / "Level2" / "RepoC" / ".git").mkdir(
            parents=True
        )

        # Directory skipped by custom keyword.
        (self.root_path / "VendorCache" / "RepoD" / ".git").mkdir(parents=True)

        self.external_target = Path(self.temp_dir.name) / "external_target"
        (self.external_target / "ExternalRepo" / ".git").mkdir(parents=True)
        self.symlink_created = False
        try:
            (self.root_path / "link_to_external").symlink_to(
                self.external_target,
                target_is_directory=True,
            )
            self.symlink_created = True
        except OSError:
            # NOTE: Windows may require Developer Mode or elevated privileges for symlinks.
            self.symlink_created = False

        self.loop_symlink_created = False
        try:
            (self.root_path / "Loop").mkdir()
            (self.root_path / "Loop" / "back_to_root").symlink_to(
                self.root_path,
                target_is_directory=True,
            )
            self.loop_symlink_created = True
        except OSError:
            # NOTE: Windows may require Developer Mode or elevated privileges for symlinks.
            self.loop_symlink_created = False

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_safe_walk_skips_default_internal_directories(self) -> None:
        result = walk_directories(self.root_path)
        walked = _relative_paths(result.directories, self.root_path)

        self.assertIn(".", walked)
        self.assertIn("ProjectA/src", walked)
        self.assertNotIn("ProjectA/.git", walked)
        self.assertNotIn("ProjectA/.git/objects", walked)
        self.assertNotIn("node_modules", walked)
        self.assertNotIn("node_modules/PackageA", walked)
        self.assertGreaterEqual(result.name_skipped_count, 2)
        self.assertEqual(
            result.skipped_count,
            result.policy_skipped_count
            + result.link_or_reparse_skipped_count
            + result.name_skipped_count
            + result.keyword_skipped_count
            + result.revisited_skipped_count,
        )

    def test_release_is_not_skipped_by_default(self) -> None:
        result = walk_directories(self.root_path)
        walked = _relative_paths(result.directories, self.root_path)

        self.assertIn("release", walked)
        self.assertIn("release/SmartDisk", walked)

    def test_git_marker_is_detected_without_traversing_git_internals(self) -> None:
        result = find_marker_directories([self.root_path], ".git")
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertIn("ProjectA", matches)
        self.assertIn("ProjectB", matches)
        self.assertNotIn("node_modules/PackageA", matches)
        self.assertTrue(result.has_matches)

    def test_tool_manifest_inside_release_is_detected(self) -> None:
        result = find_marker_directories(
            [self.root_path],
            "tool_manifest.json",
            stop_descending_on_match=True,
        )
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertIn("release/SmartDisk", matches)
        self.assertNotIn("release/SmartDisk/output/nested_manifest", matches)

    def test_stop_descending_on_match_can_be_disabled(self) -> None:
        result = find_marker_directories(
            [self.root_path],
            "tool_manifest.json",
            stop_descending_on_match=False,
        )
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertIn("release/SmartDisk", matches)
        self.assertIn("release/SmartDisk/output/nested_manifest", matches)

    def test_max_depth_limits_marker_detection(self) -> None:
        too_shallow = find_marker_directories(
            [self.root_path],
            ".git",
            max_depth=3,
            stop_descending_on_match=False,
        )
        too_shallow_matches = _relative_paths(
            [match.directory_path for match in too_shallow.matches],
            self.root_path,
        )

        enough_depth = find_marker_directories(
            [self.root_path],
            ".git",
            max_depth=4,
            stop_descending_on_match=False,
        )
        enough_depth_matches = _relative_paths(
            [match.directory_path for match in enough_depth.matches],
            self.root_path,
        )

        self.assertNotIn("Deep/Level1/Level2/RepoC", too_shallow_matches)
        self.assertIn("Deep/Level1/Level2/RepoC", enough_depth_matches)

    def test_custom_keyword_skip_blocks_branch(self) -> None:
        result = find_marker_directories(
            [self.root_path],
            ".git",
            skipped_directory_keywords=["vendor"],
            stop_descending_on_match=False,
        )
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertNotIn("VendorCache/RepoD", matches)
        self.assertGreaterEqual(result.keyword_skipped_count, 1)

    def test_validation_errors_are_structured(self) -> None:
        invalid_marker = find_marker_directories([self.root_path], "../.git")
        invalid_depth = walk_directories(self.root_path, max_depth=-1)
        missing_root = walk_directories(self.root_path / "missing")

        plain_file = self.root_path / "plain_file.txt"
        _touch(plain_file, "hello")
        file_root = walk_directories(plain_file)

        self.assertEqual(invalid_marker.errors[0].error_type, "invalid_marker_name")
        self.assertEqual(invalid_depth.errors[0].error_type, "invalid_max_depth")
        self.assertEqual(missing_root.errors[0].error_type, "path_not_found")
        self.assertEqual(file_root.errors[0].error_type, "not_a_directory")
        serialized = missing_root.errors[0].to_dict()
        self.assertEqual(serialized["path"], str(self.root_path / "missing"))
        self.assertEqual(serialized["stage"], "validation")
        self.assertEqual(serialized["error_type"], "path_not_found")

    def test_marker_helpers_validate_and_detect(self) -> None:
        self.assertTrue(directory_contains_marker(self.root_path / "ProjectA", ".git"))
        self.assertEqual(validate_marker_name("pyproject.toml"), "pyproject.toml")

        with self.assertRaises(ValueError):
            validate_marker_name("../.git")

    def test_single_root_path_is_accepted_for_marker_scan(self) -> None:
        result = find_marker_directories(self.root_path, ".git")
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertIn("ProjectA", matches)
        self.assertIn("ProjectB", matches)

    def test_none_marker_name_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            validate_marker_name(None)  # type: ignore[arg-type]

    def test_symlink_branch_is_not_followed_by_default(self) -> None:
        if not self.symlink_created:
            self.skipTest("Symlink creation is not available in this environment.")

        result = find_marker_directories(
            [self.root_path],
            ".git",
            stop_descending_on_match=False,
        )
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertNotIn("link_to_external/ExternalRepo", matches)
        self.assertGreaterEqual(result.skipped_count, 1)
        self.assertGreaterEqual(result.link_or_reparse_skipped_count, 1)

    def test_follow_symlinks_can_discover_directory_symlink_targets(self) -> None:
        if not self.symlink_created:
            self.skipTest("Symlink creation is not available in this environment.")

        result = find_marker_directories(
            self.root_path,
            ".git",
            follow_symlinks=True,
            stop_descending_on_match=False,
        )
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertIn("link_to_external/ExternalRepo", matches)

    def test_follow_symlinks_avoids_recursive_directory_loops(self) -> None:
        if not self.loop_symlink_created:
            self.skipTest("Symlink creation is not available in this environment.")

        result = walk_directories(
            self.root_path,
            follow_symlinks=True,
            max_depth=8,
            use_default_skipped_directory_names=False,
        )
        walked = _relative_paths(result.directories, self.root_path)

        self.assertIn("Loop", walked)
        self.assertNotIn("Loop/back_to_root", walked)
        self.assertGreaterEqual(result.skipped_count, 1)

    def test_public_package_exports_expected_symbols(self) -> None:
        self.assertIn(".git", DEFAULT_SKIPPED_DIRECTORY_NAMES)
        self.assertEqual(exported_validate_marker_name(".git"), ".git")

    def test_include_root_false_excludes_root_directory(self) -> None:
        result = walk_directories(self.root_path, include_root=False)
        walked = _relative_paths(result.directories, self.root_path)

        self.assertNotIn(".", walked)
        self.assertIn("ProjectA", walked)

    def test_multiple_root_paths_are_aggregated(self) -> None:
        second_root = Path(self.temp_dir.name) / "second_scan_root"
        (second_root / "SecondProject" / ".git").mkdir(parents=True)

        result = find_marker_directories(
            [self.root_path, second_root],
            ".git",
            stop_descending_on_match=True,
        )

        self.assertEqual(result.root_paths, [self.root_path, second_root])
        self.assertTrue(
            any(
                match.directory_path == second_root / "SecondProject"
                for match in result.matches
            )
        )

    def test_custom_exact_skip_name_is_case_insensitive(self) -> None:
        (self.root_path / "BuildOutput" / "RepoE" / ".git").mkdir(parents=True)

        result = find_marker_directories(
            self.root_path,
            ".git",
            skipped_directory_names=["buildoutput"],
            stop_descending_on_match=False,
        )
        matches = _relative_paths(
            [match.directory_path for match in result.matches],
            self.root_path,
        )

        self.assertNotIn("BuildOutput/RepoE", matches)

    def test_progress_callback_receives_scan_events(self) -> None:
        events: list[dict[str, object]] = []

        def collect_event(event: object) -> None:
            events.append(dict(event))  # type: ignore[arg-type]

        result = walk_directories(
            self.root_path,
            max_depth=1,
            progress_callback=collect_event,
        )

        self.assertGreater(result.scanned_count, 0)
        self.assertGreater(len(events), 0)
        self.assertEqual(events[0]["stage"], "scanning")
        self.assertIn("path", events[0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
