from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = PROJECT_ROOT / "tools" / "run_public_validation.py"

SPEC = importlib.util.spec_from_file_location(
    "sharedcode_public_validator_test",
    VALIDATOR_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load run_public_validation.py")

validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class PublicValidatorLocalRootTests(unittest.TestCase):
    def test_validate_tree_ignores_git_and_venv_roots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / ".git" / "objects").mkdir(parents=True)
            (root / ".git" / "objects" / "object").write_text("git")
            (
                root
                / ".venv"
                / "Lib"
                / "site-packages"
                / "build"
            ).mkdir(parents=True)
            (
                root
                / ".venv"
                / "Lib"
                / "site-packages"
                / "native.pyd"
            ).write_bytes(b"binary")
            (root / "AppCore").mkdir()
            (root / "AppCore" / "module.py").write_text("VALUE = 1")

            with patch.object(validator, "ROOT", root):
                validator.validate_tree()

    def test_cleanup_preserves_git_and_venv_files(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            git_file = root / ".git" / "config"
            venv_binary = (
                root
                / ".venv"
                / "Lib"
                / "site-packages"
                / "native.pyd"
            )
            git_file.parent.mkdir(parents=True)
            venv_binary.parent.mkdir(parents=True)
            git_file.write_text("[core]")
            venv_binary.write_bytes(b"binary")

            with patch.object(validator, "ROOT", root):
                validator.cleanup_generated()

            self.assertTrue(git_file.is_file())
            self.assertEqual(venv_binary.read_bytes(), b"binary")

    def test_cleanup_removes_generated_project_artifacts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            cache_file = root / "AppCore" / "__pycache__" / "module.pyc"
            compiled_file = root / "GuiCore" / "native.pyd"
            build_file = root / "build" / "artifact.txt"

            cache_file.parent.mkdir(parents=True)
            compiled_file.parent.mkdir(parents=True)
            build_file.parent.mkdir(parents=True)
            cache_file.write_bytes(b"cache")
            compiled_file.write_bytes(b"binary")
            build_file.write_text("artifact")

            with patch.object(validator, "ROOT", root):
                validator.cleanup_generated()

            self.assertFalse(cache_file.parent.exists())
            self.assertFalse(compiled_file.exists())
            self.assertFalse(build_file.parent.exists())

    def test_validate_tree_reports_only_generated_directory_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            nested = root / "dist" / "nested" / "artifact.whl"
            nested.parent.mkdir(parents=True)
            nested.write_bytes(b"wheel")

            with patch.object(validator, "ROOT", root):
                with self.assertRaises(RuntimeError) as context:
                    validator.validate_tree()

            message = str(context.exception)
            self.assertIn("dist", message)
            self.assertNotIn("artifact.whl", message)

    def test_validate_tree_rejects_compiled_project_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            compiled = root / "AppCore" / "module.pyc"
            compiled.parent.mkdir(parents=True)
            compiled.write_bytes(b"cache")

            with patch.object(validator, "ROOT", root):
                with self.assertRaises(RuntimeError) as context:
                    validator.validate_tree()

            self.assertIn(
                str(Path("AppCore") / "module.pyc"),
                str(context.exception),
            )


if __name__ == "__main__":
    unittest.main()
