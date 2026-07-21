from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class ReportTable:
    name: str
    title: str
    columns: list[str]
    rows: list[dict[str, Any]]
    source_path: str = ""


@dataclass(slots=True)
class ReportSection:
    name: str
    title: str
    content: Any
    level: int = 1


@dataclass(slots=True)
class ReportDocument:
    report_type: str
    title: str
    subtitle: str
    status: str
    meta: dict[str, Any]
    summary: dict[str, Any]
    report_brief: dict[str, Any]
    data: dict[str, Any]
    diagnostics: list[Any]
    errors: list[Any]
    sections: list[ReportSection] = field(default_factory=list)
    tables: list[ReportTable] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)
