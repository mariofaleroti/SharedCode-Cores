import tempfile
import unittest
from pathlib import Path

from release_core import build_release_package, collect_release_files, should_skip_path


class ReleaseCoreTests(unittest.TestCase):
    def test_should_skip_development_directories(self):
        self.assertTrue(should_skip_path(Path("__pycache__/module.pyc")))
        self.assertTrue(should_skip_path(Path(".git/config")))
        self.assertTrue(should_skip_path(Path("build/app.exe")))

    def test_should_not_skip_normal_files(self):
        self.assertFalse(should_skip_path(Path("app/main.py")))
        self.assertFalse(should_skip_path(Path("README.md")))

    def test_collect_release_files_skips_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "app").mkdir()
            (root / "app" / "main.py").write_text("print('ok')", encoding="utf-8")
            (root / "__pycache__").mkdir()
            (root / "__pycache__" / "main.pyc").write_bytes(b"x")

            files, skipped = collect_release_files(root)

            self.assertEqual([path.name for path in files], ["main.py"])
            self.assertTrue(any("__pycache__" in item for item in skipped))

    def test_build_release_package_copies_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "src"
            release = base / "release"
            (source / "app").mkdir(parents=True)
            (source / "app" / "main.py").write_text("value = 1", encoding="utf-8")

            result = build_release_package(source, release)

            self.assertTrue(result.succeeded)
            self.assertEqual(result.files_count, 1)
            self.assertTrue((release / "app" / "main.py").exists())

    def test_build_release_package_cleans_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            source = base / "src"
            release = base / "release"
            source.mkdir()
            (source / "main.py").write_text("ok", encoding="utf-8")
            release.mkdir()
            (release / "old.txt").write_text("old", encoding="utf-8")

            build_release_package(source, release)

            self.assertFalse((release / "old.txt").exists())
            self.assertTrue((release / "main.py").exists())

    def test_collect_release_files_rejects_missing_source(self):
        with self.assertRaises(FileNotFoundError):
            collect_release_files(Path("missing-source-for-test"))


if __name__ == "__main__":
    unittest.main()
