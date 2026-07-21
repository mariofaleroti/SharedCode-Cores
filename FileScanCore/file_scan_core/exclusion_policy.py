"""Declarative directory exclusion policies for safe filesystem traversal.

DESIGN:
FileScanCore owns only the reusable matching and pruning mechanism. Consuming
applications provide the actual directory names, paths and group meanings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fnmatch import fnmatchcase
from pathlib import Path
from typing import Iterable


def _normalize_text(value: str) -> str:
    return str(value or "").strip().replace("\\", "/").strip("/").casefold()


def _normalize_name_set(values: Iterable[str] | None) -> frozenset[str]:
    if not values:
        return frozenset()
    return frozenset(_normalize_text(value) for value in values if _normalize_text(value))


def _normalize_patterns(values: Iterable[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    return tuple(_normalize_text(value) for value in values if _normalize_text(value))


def _normalize_absolute_paths(values: Iterable[str | Path] | None) -> tuple[Path, ...]:
    if not values:
        return ()
    normalized: list[Path] = []
    seen: set[str] = set()
    for value in values:
        path = Path(value).expanduser()
        try:
            path = path.resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            pass
        key = str(path).casefold()
        if key in seen:
            continue
        seen.add(key)
        normalized.append(path)
    return tuple(normalized)


def _segment_pattern_matches(path_parts: tuple[str, ...], pattern_parts: tuple[str, ...]) -> bool:
    """Matches slash-separated patterns where * is one segment and ** is recursive."""

    if not pattern_parts:
        return not path_parts

    head = pattern_parts[0]
    tail = pattern_parts[1:]

    if head == "**":
        return _segment_pattern_matches(path_parts, tail) or bool(
            path_parts and _segment_pattern_matches(path_parts[1:], pattern_parts)
        )

    if not path_parts:
        return False

    return fnmatchcase(path_parts[0], head) and _segment_pattern_matches(path_parts[1:], tail)


@dataclass(slots=True, frozen=True)
class DirectoryExclusionRule:
    """One reusable directory exclusion rule supplied by a consumer."""

    rule_id: str
    group_id: str
    reason: str
    directory_names: frozenset[str] = field(default_factory=frozenset)
    relative_path_patterns: tuple[str, ...] = ()
    absolute_paths: tuple[Path, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        rule_id: str,
        group_id: str,
        reason: str,
        directory_names: Iterable[str] | None = None,
        relative_path_patterns: Iterable[str] | None = None,
        absolute_paths: Iterable[str | Path] | None = None,
    ) -> "DirectoryExclusionRule":
        return cls(
            rule_id=str(rule_id).strip(),
            group_id=str(group_id).strip(),
            reason=str(reason).strip(),
            directory_names=_normalize_name_set(directory_names),
            relative_path_patterns=_normalize_patterns(relative_path_patterns),
            absolute_paths=_normalize_absolute_paths(absolute_paths),
        )


@dataclass(slots=True, frozen=True)
class DirectoryExclusionMatch:
    """Structured explanation for one pruned directory."""

    path: Path
    rule_id: str
    group_id: str
    reason: str
    matched_by: str
    matched_value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "path": str(self.path),
            "rule_id": self.rule_id,
            "group_id": self.group_id,
            "reason": self.reason,
            "matched_by": self.matched_by,
            "matched_value": self.matched_value,
        }


@dataclass(slots=True, frozen=True)
class DirectoryExclusionPolicy:
    """Ordered collection of directory exclusion rules."""

    rules: tuple[DirectoryExclusionRule, ...] = ()

    @classmethod
    def from_rules(cls, rules: Iterable[DirectoryExclusionRule] | None) -> "DirectoryExclusionPolicy":
        return cls(tuple(rules or ()))

    @property
    def enabled_group_ids(self) -> tuple[str, ...]:
        seen: list[str] = []
        for rule in self.rules:
            if rule.group_id not in seen:
                seen.append(rule.group_id)
        return tuple(seen)

    def match(self, directory_path: str | Path, *, root_path: str | Path) -> DirectoryExclusionMatch | None:
        path = Path(directory_path).expanduser()
        root = Path(root_path).expanduser()

        try:
            normalized_path = path.resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            normalized_path = path
        try:
            normalized_root = root.resolve(strict=False)
        except (OSError, RuntimeError, ValueError):
            normalized_root = root

        path_name = _normalize_text(normalized_path.name)
        try:
            relative = normalized_path.relative_to(normalized_root)
            relative_parts = tuple(_normalize_text(part) for part in relative.parts)
        except ValueError:
            relative_parts = ()

        normalized_path_text = str(normalized_path).casefold()

        for rule in self.rules:
            if path_name and path_name in rule.directory_names:
                return DirectoryExclusionMatch(
                    path=normalized_path,
                    rule_id=rule.rule_id,
                    group_id=rule.group_id,
                    reason=rule.reason,
                    matched_by="directory_name",
                    matched_value=normalized_path.name,
                )

            for absolute_path in rule.absolute_paths:
                if normalized_path_text == str(absolute_path).casefold():
                    return DirectoryExclusionMatch(
                        path=normalized_path,
                        rule_id=rule.rule_id,
                        group_id=rule.group_id,
                        reason=rule.reason,
                        matched_by="absolute_path",
                        matched_value=str(absolute_path),
                    )

            if relative_parts:
                for pattern in rule.relative_path_patterns:
                    pattern_parts = tuple(part for part in pattern.split("/") if part)
                    if _segment_pattern_matches(relative_parts, pattern_parts):
                        return DirectoryExclusionMatch(
                            path=normalized_path,
                            rule_id=rule.rule_id,
                            group_id=rule.group_id,
                            reason=rule.reason,
                            matched_by="relative_path_pattern",
                            matched_value=pattern,
                        )

        return None
