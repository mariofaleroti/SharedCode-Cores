from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .document import ReportDocument
from .exceptions import UnsupportedFormatError
from .result import RenderResult

RendererCallable = Callable[[ReportDocument, object], RenderResult]


@dataclass(slots=True)
class TemplateProfile:
    report_type: str
    html_template: str
    description: str = ""


class FormatRegistry:
    def __init__(self) -> None:
        self._renderers: dict[str, RendererCallable] = {}

    def register(self, name: str, renderer: RendererCallable) -> None:
        self._renderers[name.lower().strip()] = renderer

    def get(self, name: str) -> RendererCallable:
        key = name.lower().strip()
        if key not in self._renderers:
            raise UnsupportedFormatError(f"Unsupported render format: {name}")
        return self._renderers[key]

    def names(self) -> list[str]:
        return sorted(self._renderers.keys())


HTML_TEMPLATE_PROFILES: dict[str, TemplateProfile] = {
    "hardware": TemplateProfile("hardware", "hardware_report.html.j2", "Hardware report profile"),
    "network": TemplateProfile("network", "network_report.html.j2", "Network report profile"),
    "software": TemplateProfile("software", "software_report.html.j2", "Software report profile"),
    "system_extras": TemplateProfile("system_extras", "extras_report.html.j2", "Extras report profile"),
    "full_report": TemplateProfile("full_report", "full_report.html.j2", "Full report profile"),
    "disk_smart": TemplateProfile("disk_smart", "disk_smart.html.j2", "Smart Disk professional profile"),
    "storage_analyzer": TemplateProfile("storage_analyzer", "storage_analyzer_report.html.j2", "Storage Analyzer profile"),
    "event_health": TemplateProfile("event_health", "event_health_report.html.j2", "Event Health profile"),
    "category_database": TemplateProfile("category_database", "category_database.html.j2", "Smart Filter category database profile"),
    "document_highlight": TemplateProfile("document_highlight", "document_highlight.html.j2", "Interactive highlighted document profile"),
    "document_highlight_pro": TemplateProfile("document_highlight_pro", "document_highlight_pro.html.j2", "Professional interactive highlighted document profile"),
    "config": TemplateProfile("config", "generic_report.html.j2", "Generic configuration profile"),
}


def resolve_html_template(report_type: str, explicit_profile: str | None = None) -> str:
    requested = (explicit_profile or report_type or "").lower().strip()
    if requested in HTML_TEMPLATE_PROFILES:
        return HTML_TEMPLATE_PROFILES[requested].html_template
    return "generic_report.html.j2"
