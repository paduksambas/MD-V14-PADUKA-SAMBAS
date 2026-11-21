"""Tests for MD V14 JSON storage helpers."""
import json
import tempfile
import unittest
from pathlib import Path

from mdv14.storage import load_signals, save_json_atomic, save_signals


class StorageTests(unittest.TestCase):
    def test_save_and_load_signals(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested" / "signals.json"
            signals = [{"title": "Example", "score": 42}]
            save_signals(path, signals)
            self.assertEqual(load_signals(path), signals)

    def test_load_rejects_non_array(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "signals.json"
            path.write_text(json.dumps({"title": "not an array"}), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_signals(path)

    def test_load_rejects_non_object_items(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "signals.json"
            path.write_text(json.dumps(["not an object"]), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_signals(path)

    def test_atomic_json_report(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            save_json_atomic(path, {"ok": True})
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), {"ok": True})


if __name__ == "__main__":
    unittest.main()
