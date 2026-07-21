from __future__ import annotations

import argparse
import json
import sys

from .api import render_many, render_report
from .exceptions import RenderCoreError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="RenderEngine",
        description="Render strict SharedCode JSON report contracts to HTML, TXT, CSV or XLSX.",
    )

    subparsers = parser.add_subparsers(dest="command")
    render_parser = subparsers.add_parser("render", help="Render a report JSON file.")
    _add_render_arguments(render_parser)

    # Convenience root arguments: RenderEngine.exe --input file.json --output file.html
    _add_render_arguments(parser, include_help=False)

    return parser


def _add_render_arguments(parser: argparse.ArgumentParser, *, include_help: bool = True) -> None:
    group = parser if include_help else parser
    group.add_argument("--input", required=False, help="Path to the input JSON report.")
    group.add_argument("--output", required=False, help="Path to the output file. Best for single-file formats.")
    group.add_argument("--output-dir", required=False, help="Output directory. Recommended for multi-format or CSV export.")
    group.add_argument("--format", default="html", choices=["html", "txt", "csv", "xlsx"], help="Single output format.")
    group.add_argument("--formats", required=False, help="Comma-separated formats, for example: html,txt,xlsx")
    group.add_argument("--template-dir", required=False, help="Optional custom template directory.")
    group.add_argument("--profile", required=False, help="Optional render profile/template key.")
    group.add_argument("--theme", default="dark", choices=["dark", "light"], help="Theme for generic HTML templates.")
    group.add_argument(
        "--contract-profile",
        default="auto",
        help="Contract profile passed to JsonContractCore. Use auto to select from meta.config_type/report_type.",
    )
    group.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.input:
        parser.error("--input is required")

    try:
        if args.formats:
            formats = [item.strip() for item in args.formats.split(",") if item.strip()]
            results = render_many(
                input_path=args.input,
                formats=formats,
                output_dir=args.output_dir,
                template_dir=args.template_dir,
                profile=args.profile,
                theme=args.theme,
                contract_profile=args.contract_profile,
            )
        else:
            results = [
                render_report(
                    input_path=args.input,
                    output_path=args.output,
                    output_dir=args.output_dir,
                    output_format=args.format,
                    template_dir=args.template_dir,
                    profile=args.profile,
                    theme=args.theme,
                    contract_profile=args.contract_profile,
                )
            ]
    except RenderCoreError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"Render failed: {exc}", file=sys.stderr)
        return 2
    except Exception as exc:  # Defensive boundary for CLI usage.
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"Unexpected render failure: {exc}", file=sys.stderr)
        return 1

    if args.json:
        payload = {
            "ok": all(result.ok for result in results),
            "results": [
                {
                    "format": result.format,
                    "output_path": str(result.output_path) if result.output_path else None,
                    "extra_paths": [str(path) for path in result.extra_paths],
                    "message": result.message,
                    "errors": result.errors,
                    "diagnostics": result.diagnostics,
                }
                for result in results
            ],
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
    else:
        for result in results:
            print(f"[{result.format}] {result.message}")
            for path in result.all_paths():
                print(f"  - {path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
