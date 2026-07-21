from __future__ import annotations

from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from render_core import render_report_data
from tests.smoke_test import install_fake_json_contract_core


def main() -> int:
    fake_root = install_fake_json_contract_core(PROJECT_ROOT)
    output_dir = PROJECT_ROOT / "output" / "document_highlight_test"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    output_path = output_dir / "document_highlight.html"

    payload = {
        "meta": {
            "schema_version": "1.0.0",
            "tool_name": "Smart Filter",
            "report_type": "document_highlight",
        },
        "summary": {"status": "ok", "match_occurrences_count": 2},
        "report_brief": {
            "title": "cv.pdf",
            "subtitle": "Vista HTML destacada · administracion",
            "status": "ok",
        },
        "data": {
            "document": {
                "title": "cv.pdf",
                "source_path": "C:/demo/cv.pdf",
                "source_uri": "file:///C:/demo/cv.pdf",
                "format": "pdf",
                "reader": "pdf_reader",
                "truncated": False,
                "sections": [
                    {
                        "id": "page-1",
                        "label": "Página 1",
                        "kind": "página PDF",
                        "blocks": [
                            {"type": "line", "line_number": 1, "location_label": "Página 1 · Línea 1", "text": "Atención al cliente"},
                            {"type": "line", "line_number": 2, "location_label": "Página 1 · Línea 2", "text": "Asistente administrativo"},
                        ],
                    }
                ],
            },
            "highlight": {
                "category_name": "administracion",
                "terms": [{"text": "atencion al cliente"}, {"text": "administrativo"}],
                "occurrence_count": 2,
                "locations": [],
            },
        },
        "diagnostics": [],
        "errors": [],
    }

    result = render_report_data(payload, output_path, profile="document_highlight", theme="dark")
    assert result.ok
    html = output_path.read_text(encoding="utf-8")
    assert "Visor destacado · RenderCore" in html
    assert "Anterior" in html and "Siguiente" in html
    assert "data-highlight-scope" in html
    assert "atencion al cliente" in html
    assert "document_highlight.html.j2" in result.message
    print("Document highlight profile OK")
    print(f"Temporary JsonContractCore fake: {fake_root}")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
