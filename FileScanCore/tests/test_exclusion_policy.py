from pathlib import Path

from file_scan_core import (
    DirectoryExclusionPolicy,
    DirectoryExclusionRule,
    walk_directories,
)


def test_policy_matches_exact_name_and_reports_group(tmp_path: Path) -> None:
    root = tmp_path / "root"
    target = root / "node_modules"
    target.mkdir(parents=True)

    policy = DirectoryExclusionPolicy.from_rules(
        [
            DirectoryExclusionRule.create(
                rule_id="dev",
                group_id="development",
                reason="dependency",
                directory_names=("node_modules",),
            )
        ]
    )

    match = policy.match(target, root_path=root)
    assert match is not None
    assert match.group_id == "development"
    assert match.matched_by == "directory_name"


def test_policy_matches_segment_aware_relative_pattern(tmp_path: Path) -> None:
    root = tmp_path / "root"
    target = root / "Users" / "Mario" / "AppData" / "Local" / "Temp"
    target.mkdir(parents=True)

    policy = DirectoryExclusionPolicy.from_rules(
        [
            DirectoryExclusionRule.create(
                rule_id="temp",
                group_id="temporary",
                reason="cache",
                relative_path_patterns=("Users/*/AppData/Local/Temp",),
            )
        ]
    )

    match = policy.match(target, root_path=root)
    assert match is not None
    assert match.matched_value == "users/*/appdata/local/temp"


def test_walker_prunes_policy_directory_before_descending(tmp_path: Path) -> None:
    root = tmp_path / "root"
    kept = root / "Documents"
    excluded = root / "Windows"
    nested = excluded / "System32" / "deep"
    kept.mkdir(parents=True)
    nested.mkdir(parents=True)

    matches = []
    policy = DirectoryExclusionPolicy.from_rules(
        [
            DirectoryExclusionRule.create(
                rule_id="system",
                group_id="system",
                reason="system tree",
                relative_path_patterns=("Windows",),
            )
        ]
    )

    result = walk_directories(
        root,
        use_default_skipped_directory_names=False,
        exclusion_policy=policy,
        directory_excluded_callback=matches.append,
    )

    assert kept in result.directories
    assert excluded not in result.directories
    assert nested not in result.directories
    assert result.policy_skipped_count == 1
    assert len(matches) == 1
    assert matches[0].path == excluded


def test_manual_absolute_path_rule_prunes_exact_folder(tmp_path: Path) -> None:
    root = tmp_path / "root"
    excluded = root / "custom" / "ignored"
    excluded.mkdir(parents=True)

    policy = DirectoryExclusionPolicy.from_rules(
        [
            DirectoryExclusionRule.create(
                rule_id="manual",
                group_id="manual_exact_paths",
                reason="manual",
                absolute_paths=(excluded,),
            )
        ]
    )

    result = walk_directories(
        root,
        use_default_skipped_directory_names=False,
        exclusion_policy=policy,
    )

    assert excluded not in result.directories
    assert result.policy_skipped_count == 1
