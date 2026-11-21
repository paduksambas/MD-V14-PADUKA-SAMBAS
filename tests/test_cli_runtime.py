"""End-to-end CLI runtime smoke test for Build 1.4."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLIRuntimeTests(unittest.TestCase):
    def test_cli_writes_report_and_persists_history_between_runs(self):
        root = Path(__file__).resolve().parents[1]
        sample = root / "examples" / "signals.sample.json"
        with tempfile.TemporaryDirectory() as directory:
            database = Path(directory) / "history.sqlite3"
            report_path = Path(directory) / "report.json"
            command = [
                sys.executable, "-m", "mdv14", str(sample),
                "--database", str(database), "--output", str(report_path),
            ]
            first = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(first.returncode, 0, msg=first.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["history"]["tracked_trends"], 2)
            self.assertTrue(database.exists())

            second = subprocess.run(command, cwd=root, capture_output=True, text=True)
            self.assertEqual(second.returncode, 0, msg=second.stderr)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            observations = [item["history"]["observation_count"] for item in report["signals"]]
            self.assertEqual(observations, [2, 2])


if __name__ == "__main__":
    unittest.main()
