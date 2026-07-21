import tempfile
import unittest
from pathlib import Path

from file_system_info_core import get_directory_summary, get_path_info


class FileSystemInfoCoreTests(unittest.TestCase):
    def test_get_path_info_for_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "data.txt"
            file_path.write_text("hello", encoding="utf-8")

            info = get_path_info(file_path)

            self.assertTrue(info.exists)
            self.assertTrue(info.is_file)
            self.assertEqual(info.suffix, ".txt")
            self.assertEqual(info.size_bytes, 5)
            self.assertIsNotNone(info.modified_at_utc)
            self.assertTrue(info.modified_at_utc.endswith("Z"))
            self.assertIsInstance(info.modified_at_epoch_seconds, float)

    def test_get_path_info_for_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            info = get_path_info(tmp)

            self.assertTrue(info.exists)
            self.assertTrue(info.is_dir)
            self.assertIsNone(info.size_bytes)

    def test_get_path_info_for_missing_path(self):
        info = get_path_info("missing-file-system-info-test")
        self.assertFalse(info.exists)
        self.assertEqual(info.name, "missing-file-system-info-test")

    def test_get_directory_summary_counts_direct_children_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.txt").write_text("a", encoding="utf-8")
            (root / "b.txt").write_text("bb", encoding="utf-8")
            (root / "sub").mkdir()
            (root / "sub" / "nested.txt").write_text("nested", encoding="utf-8")

            summary = get_directory_summary(root)

            self.assertTrue(summary.exists)
            self.assertEqual(summary.files_count, 2)
            self.assertEqual(summary.directories_count, 1)
            self.assertEqual(summary.total_file_size_bytes, 3)

    def test_get_directory_summary_for_file_returns_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            file_path = Path(tmp) / "file.txt"
            file_path.write_text("x", encoding="utf-8")

            summary = get_directory_summary(file_path)

            self.assertTrue(summary.exists)
            self.assertEqual(summary.error["code"], "PATH_NOT_DIRECTORY")

    def test_to_dict_is_json_safe(self):
        info = get_path_info("missing-json-safe-test")
        data = info.to_dict()
        self.assertIsInstance(data["path"], str)
        self.assertIn("modified_at_utc", data)
        self.assertIn("modified_at_epoch_seconds", data)


if __name__ == "__main__":
    unittest.main()
