from __future__ import annotations

from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from render_core import render_report_data
from tests.smoke_test import install_fake_json_contract_core


def build_payload() -> dict:
    return {
        "meta": {
            "schema_version": "1.0.0",
            "tool_name": "Smart Filter",
            "tool_version": "1.0.20-dev",
            "report_type": "document_highlight",
            "generated_at": "2026-07-16 14:30:00 -03:00",
        },
        "summary": {
            "status": "ok",
            "match_occurrences_count": 5,
            "matched_terms_count": 3,
            "sections_count": 2,
        },
        "report_brief": {
            "title": "1179361_romina_santana.pdf",
            "subtitle": "Vista HTML destacada · administracion",
            "status": "ok",
        },
        "data": {
            "document": {
                "title": "1179361_romina_santana.pdf",
                "source_path": "C:/documentos/1179361_romina_santana.pdf",
                "source_uri": "file:///C:/documentos/1179361_romina_santana.pdf",
                "source_directory_uri": "file:///C:/documentos",
                "source_size_label": "248.4 KB",
                "format": "pdf",
                "reader": "pdf_reader",
                "truncated": False,
                "sections": [
                    {
                        "id": "page-1",
                        "label": "Página 1",
                        "kind": "página PDF",
                        "blocks": [
                            {
                                "type": "line",
                                "line_number": 1,
                                "location_label": "Página 1 · Línea 1",
                                "text": "Romina Santana · Asistente administrativo",
                            },
                            {
                                "type": "line",
                                "line_number": 2,
                                "location_label": "Página 1 · Línea 2",
                                "text": "Experiencia en atención al cliente y recepción.",
                            },
                            {
                                "type": "line",
                                "line_number": 3,
                                "location_label": "Página 1 · Línea 3",
                                "text": "Microsoft Excel | Atención al cliente",
                            },
                        ],
                    },
                    {
                        "id": "page-2",
                        "label": "Página 2",
                        "kind": "página PDF",
                        "blocks": [
                            {
                                "type": "line",
                                "line_number": 4,
                                "location_label": "Página 2 · Línea 4",
                                "text": "Cajas registradoras | Servicio de atención al cliente",
                            },
                            {
                                "type": "line",
                                "line_number": 5,
                                "location_label": "Página 2 · Línea 5",
                                "text": "Tareas de recepción y gestión administrativa.",
                            },
                        ],
                    },
                ],
            },
            "highlight": {
                "category_name": "administracion",
                "terms": [
                    {"text": "atencion al cliente"},
                    {"text": "administrativo"},
                    {"text": "recepcion"},
                ],
                "occurrence_count": 5,
                "locations": [],
            },
        },
        "diagnostics": [],
        "errors": [],
    }


def main() -> int:
    fake_root = install_fake_json_contract_core(PROJECT_ROOT)
    output_dir = PROJECT_ROOT / "output" / "document_highlight_pro_test"
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)
    output_path = output_dir / "document_highlight_pro.html"

    result = render_report_data(
        build_payload(),
        output_path,
        profile="document_highlight_pro",
        theme="dark",
    )
    assert result.ok
    html = output_path.read_text(encoding="utf-8")
    assert "Smart Filter · Documento destacado" in html
    assert "document_highlight_pro.html.j2" in result.message
    assert "id=\"locationList\"" in html
    assert "id=\"matchProgress\"" in html
    assert "Abrir archivo original" in html
    assert "Expandir secciones" in html
    assert "Atención al cliente" in html
    assert "source_directory_uri" not in html
    print("Document highlight pro profile OK")
    print(f"Temporary JsonContractCore fake: {fake_root}")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
