"""Tests for local private-data storage helpers."""
import json
import tempfile
import unittest
from pathlib import Path

from mdv14.private_data import ensure_private_dir, save_private_json


class PrivateDataTests(unittest.TestCase):
    def test_creates_private_directory_and_file(self):
        with tempfile.TemporaryDirectory() as root:
            directory = Path(root) / "private"
            target = save_private_json("snapshot.json", {"secret": "local"}, directory)
            self.assertEqual(json.loads(target.read_text(encoding="utf-8")), {"secret": "local"})
            self.assertEqual(target.parent, directory)

    def test_rejects_path_components_in_filename(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                save_private_json("../escape.json", {}, root)

    def test_rejects_symlink_private_dir(self):
        with tempfile.TemporaryDirectory() as root:
            base = Path(root)
            actual = base / "actual"
            actual.mkdir()
            link = base / "link"
            try:
                link.symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation not supported")
            with self.assertRaises(ValueError):
                ensure_private_dir(link)


if __name__ == "__main__":
    unittest.main()
