from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, TemplateError, select_autoescape

from ..document import ReportDocument
from ..options import RenderOptions
from ..paths import ensure_parent, get_default_template_root
from ..registry import resolve_html_template
from ..result import RenderResult
from ..utils import default_output_path, render_value, status_class


def render_html(document: ReportDocument, options: RenderOptions) -> RenderResult:
    """Render a report document to HTML.

    The renderer prefers a profile-specific template when one is resolved.

    Template fallback is visual only: the JSON contract has already been strictly
    validated by JsonContractCore before this renderer runs.
    """

    output_path = options.output_path or default_output_path(options.input_path, "html", options.output_dir)
    output_path = output_path.expanduser().resolve()
    ensure_parent(output_path)

    environment = _build_environment(options.template_dir)
    template_name = resolve_html_template(document.report_type, options.profile)
    diagnostics: list[dict[str, Any]] = []

    content: str
    try:
        content = _render_template(environment, template_name, document, options)
    except Exception as exc:  # Profile templates are optional; generic is the visual safety net.
        diagnostics.append(
            {
                "level": "warning",
                "code": "html_template_fallback",
                "message": f"Template '{template_name}' failed; generic template was used.",
                "details": str(exc),
            }
        )
        template_name = "generic_report.html.j2"
        content = _render_template(environment, template_name, document, options)

    output_path.write_text(content, encoding="utf-8")

    return RenderResult(
        ok=True,
        format="html",
        output_path=output_path,
        message=f"HTML report generated with template: {template_name}",
        diagnostics=diagnostics,
    )


def _build_environment(template_dir: Path | None) -> Environment:
    template_root = get_default_template_root() / "html"
    profiles_root = template_root / "profiles"

    loaders = []
    if template_dir:
        loaders.append(FileSystemLoader(str(template_dir.expanduser().resolve())))

    loaders.extend(
        [
            FileSystemLoader(str(template_root)),
            FileSystemLoader(str(profiles_root)),
        ]
    )

    environment = Environment(
        loader=ChoiceLoader(loaders),
        autoescape=select_autoescape(["html", "xml", "j2"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    environment.filters["render_value"] = render_value
    environment.filters["status_class"] = status_class
    return environment


def _render_template(
    environment: Environment,
    template_name: str,
    document: ReportDocument,
    options: RenderOptions,
) -> str:
    try:
        template = environment.get_template(template_name)
        return template.render(
            document=document,
            meta=document.meta,
            summary=document.summary,
            report_brief=document.report_brief,
            data=document.data,
            diagnostics=document.diagnostics,
            errors=document.errors,
            theme=(options.theme or "dark").lower().strip(),
            render_value=render_value,
        )
    except TemplateError:
        raise
