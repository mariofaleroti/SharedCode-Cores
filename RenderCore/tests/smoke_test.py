from __future__ import annotations

from pathlib import Path
import shutil
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from render_core import render_many


REQUIRED_KEYS = ("meta", "summary", "report_brief", "data", "diagnostics", "errors")
REQUIRED_META_KEYS = ("schema_version", "tool_name")


def install_fake_json_contract_core(project_root: Path) -> Path:
    """Create a temporary JsonContractCore-compatible package for isolated tests.

    Production RenderCore must use the real SharedCode JsonContractCore. This fake
    exists only so the smoke test can verify the strict integration mechanics.
    """

    fake_root = project_root / ".tmp_smoke_json_contract_core"
    package_root = fake_root / "json_contract_core"
    if fake_root.exists():
        shutil.rmtree(fake_root)
    package_root.mkdir(parents=True)

    validator_code = '''
from __future__ import annotations

REQUIRED_KEYS = ("meta", "summary", "report_brief", "data", "diagnostics", "errors")
REQUIRED_META_KEYS = ("schema_version", "tool_name")


def validate_contract(data: dict, *, strict: bool = True, contract_profile: str = "tool_report") -> dict:
    missing = [key for key in REQUIRED_KEYS if key not in data]
    if missing:
        return {"ok": False, "errors": ["Missing required keys: " + ", ".join(missing)]}

    meta = data.get("meta")
    if not isinstance(meta, dict):
        return {"ok": False, "errors": ["meta must be an object"]}

    missing_meta = [key for key in REQUIRED_META_KEYS if not meta.get(key)]
    if missing_meta:
        return {"ok": False, "errors": ["Missing required meta values: " + ", ".join(missing_meta)]}

    document_kind = meta.get("report_type") or meta.get("config_type") or meta.get("file_type")
    if not document_kind:
        return {"ok": False, "errors": ["meta must define report_type, config_type or file_type"]}

    if not isinstance(data.get("summary"), dict):
        return {"ok": False, "errors": ["summary must be an object"]}
    if not isinstance(data.get("report_brief"), dict):
        return {"ok": False, "errors": ["report_brief must be an object"]}
    if not isinstance(data.get("data"), dict):
        return {"ok": False, "errors": ["data must be an object"]}
    if not isinstance(data.get("diagnostics"), list):
        return {"ok": False, "errors": ["diagnostics must be a list"]}
    if not isinstance(data.get("errors"), list):
        return {"ok": False, "errors": ["errors must be a list"]}

    return {
        "ok": True,
        "normalized_data": data,
        "warnings": [],
        "errors": [],
        "diagnostics": [{"level": "info", "code": "fake_json_contract_core", "message": "Smoke validator used."}],
    }
'''

    (package_root / "__init__.py").write_text(validator_code, encoding="utf-8")
    (package_root / "api.py").write_text(validator_code, encoding="utf-8")

    if str(fake_root) not in sys.path:
        sys.path.insert(0, str(fake_root))
    return fake_root


def main() -> int:
    project_root = PROJECT_ROOT
    fake_root = install_fake_json_contract_core(project_root)

    input_path = project_root / "examples" / "event_health_sample.json"
    output_dir = project_root / "output" / "smoke_test"
    results = render_many(input_path, ["html", "txt", "csv", "xlsx"], output_dir=output_dir)

    for result in results:
        assert result.ok, result
        assert result.output_path is not None, result
        assert result.output_path.exists(), result.output_path
        assert any("Contract validator: json_contract_core" in item.get("message", "") for item in result.diagnostics), result.diagnostics

    print("Smoke test OK")
    print(f"Temporary JsonContractCore fake: {fake_root}")
    for result in results:
        for path in result.all_paths():
            print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
