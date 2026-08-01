from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import venv
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PACKAGE_DIRS = [
    "SharedCodeMeta",
    "AppCore",
    "CliCore",
    "ConfigCore",
    "DateTimeCore",
    "FileScanCore",
    "FileSystemInfoCore",
    "GuiCore",
    "JsonContractCore",
    "LoggingCore",
    "PlatformCore",
    "ProcessRunnerCore",
    "ReleaseCore",
    "RenderCore",
    "ToolRuntimeCore",
]
CORE_IMPORTS = [
    "sharedcode_meta",
    "app_core",
    "cli_core",
    "config_core",
    "date_time_core",
    "file_scan_core",
    "file_system_info_core",
    "gui_core",
    "json_contract_core",
    "logging_core",
    "platform_core",
    "process_runner_core",
    "release_core",
    "render_core",
    "tool_runtime_core",
]


def run(command: list[str], *, cwd: Path = ROOT, env: dict[str, str] | None = None) -> None:
    print("+", " ".join(command), flush=True)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def python_path_env() -> dict[str, str]:
    env = os.environ.copy()
    package_paths = [str(ROOT / name) for name in PACKAGE_DIRS]
    existing = env.get("PYTHONPATH")
    env["PYTHONPATH"] = os.pathsep.join(package_paths + ([existing] if existing else []))
    return env


LOCAL_ROOT_DIR_NAMES = {".git", ".venv"}
GENERATED_DIR_NAMES = {
    "__pycache__",
    "build",
    "dist",
    "output",
    ".pytest_cache",
    "sharedcode_cores.egg-info",
}
GENERATED_SUFFIXES = {".pyc", ".pyo", ".pyd"}


def _walk_public_tree() -> object:
    """Walk the public source tree without entering local infrastructure.

    `.git` and `.venv` are valid local roots when validation runs from a real
    clone. They are not release payload, so neither cleanup nor validation may
    inspect or mutate them.
    """

    for current_root, dir_names, file_names in os.walk(ROOT, topdown=True):
        current = Path(current_root)

        if current == ROOT:
            dir_names[:] = [
                name
                for name in dir_names
                if name not in LOCAL_ROOT_DIR_NAMES
            ]

        yield current, dir_names, file_names


def cleanup_generated() -> None:
    """Remove generated project artifacts without touching `.git` or `.venv`."""

    for current, dir_names, file_names in _walk_public_tree():
        for name in tuple(dir_names):
            if name not in GENERATED_DIR_NAMES:
                continue

            path = current / name
            if path.is_dir():
                shutil.rmtree(path)
            elif path.exists():
                path.unlink()

            dir_names.remove(name)

        for name in file_names:
            path = current / name
            if path.suffix.lower() in GENERATED_SUFFIXES:
                path.unlink(missing_ok=True)


def validate_tree() -> None:
    """Reject generated artifacts in the public tree.

    Only the offending directory itself is reported; descendants are pruned so
    one stale directory cannot produce thousands of redundant error lines.
    """

    problems: list[str] = []

    for current, dir_names, file_names in _walk_public_tree():
        for name in tuple(dir_names):
            if name not in GENERATED_DIR_NAMES:
                continue

            relative = (current / name).relative_to(ROOT)
            problems.append(str(relative))
            dir_names.remove(name)

        for name in file_names:
            path = current / name
            if path.suffix.lower() not in GENERATED_SUFFIXES:
                continue

            problems.append(str(path.relative_to(ROOT)))

    if problems:
        raise RuntimeError(
            "Forbidden generated files found:\n"
            + "\n".join(sorted(set(problems)))
        )


def run_tests() -> None:
    targets = [
        "AppCore/tests",
        "CliCore/tests",
        "ConfigCore/tests",
        "DateTimeCore/tests",
        "FileScanCore/tests",
        "FileSystemInfoCore/tests",
        "GuiCore/tests",
        "JsonContractCore/tests",
        "LoggingCore/tests",
        "PlatformCore/tests",
        "ProcessRunnerCore/tests",
        "ReleaseCore/tests",
        "ToolRuntimeCore/tests",
        "RenderCore/tests/document_highlight_test.py",
        "RenderCore/tests/document_highlight_pro_test.py",
        "tools/tests",
    ]
    run([sys.executable, "-m", "pytest", "-q", *targets], env=python_path_env())


def build_wheel(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    run([
        sys.executable,
        "-m",
        "pip",
        "wheel",
        ".",
        "--no-deps",
        "--wheel-dir",
        str(output_dir),
    ])
    wheels = sorted(output_dir.glob("sharedcode_cores-*.whl"))
    if len(wheels) != 1:
        raise RuntimeError(f"Expected one SharedCode wheel, found: {wheels}")
    return wheels[0]


def validate_wheel_contents(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())

    for package in CORE_IMPORTS:
        init_name = f"{package}/__init__.py"
        if init_name not in names:
            raise RuntimeError(f"Wheel is missing {init_name}")

    template_names = [name for name in names if name.startswith("render_core/templates/")]
    if not template_names:
        raise RuntimeError("Wheel does not contain RenderCore templates")


def validate_isolated_install(wheel: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="sharedcode-wheel-test-") as tmp:
        env_dir = Path(tmp) / "venv"
        venv.EnvBuilder(with_pip=True).create(env_dir)
        python_exe = env_dir / ("Scripts/python.exe" if os.name == "nt" else "bin/python")

        requirement = f"sharedcode-cores[all] @ {wheel.resolve().as_uri()}"
        run([str(python_exe), "-m", "pip", "install", requirement])

        import_code = "; ".join(f"import {name}" for name in CORE_IMPORTS)
        run([str(python_exe), "-c", import_code + "; print('isolated imports OK')"])
        run([str(python_exe), "-m", "sharedcode_meta.cli"])

        template_code = (
            "from importlib.resources import files; "
            "p=files('render_core').joinpath('templates/html/document_highlight_pro.html.j2'); "
            "assert p.is_file(), p; print(p)"
        )
        run([str(python_exe), "-c", template_code])

        render_code = """
from pathlib import Path
import tempfile
from render_core import render_report_data

payload = {
    "meta": {
        "schema_version": "1.0.0",
        "report_type": "sharedcode_smoke",
        "tool_name": "SharedCode validation",
        "version": "1.0.0",
        "generated_at": "2026-07-21T12:00:00Z",
    },
    "summary": {"status": "ok", "items": 1},
    "report_brief": {
        "title": "SharedCode wheel validation",
        "subtitle": "Installed RenderCore smoke test",
        "status": "ok",
        "description": "Generated from the installed wheel.",
    },
    "data": {"items": [{"name": "example", "status": "ok"}]},
    "diagnostics": [],
    "errors": [],
}

with tempfile.TemporaryDirectory(prefix="sharedcode-render-") as tmp:
    output = Path(tmp) / "report.html"
    result = render_report_data(payload, output, output_format="html")
    assert result.ok, result
    assert output.is_file(), output
    assert "SharedCode wheel validation" in output.read_text(encoding="utf-8")
    print("installed RenderCore smoke OK")
"""
        run([str(python_exe), "-c", render_code])


def main() -> int:
    cleanup_generated()
    validate_tree()
    try:
        run_tests()
        with tempfile.TemporaryDirectory(prefix="sharedcode-build-") as tmp:
            wheel = build_wheel(Path(tmp))
            validate_wheel_contents(wheel)
            validate_isolated_install(wheel)
    finally:
        cleanup_generated()

    validate_tree()
    print("SharedCode public validation OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
