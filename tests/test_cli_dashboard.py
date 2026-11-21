"""End-to-end CLI tests for JSON and offline dashboard output."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CLIDashboardTests(unittest.TestCase):
    def test_dashboard_score_parser_handles_invalid_values(self):
        from mdv14.dashboard import _score
        self.assertEqual(_score("12.5"), 12.5)
        self.assertEqual(_score("invalid"), 0.0)
        self.assertEqual(_score(None), 0.0)

    def test_cli_generates_json_and_offline_dashboard(self):
        root = Path(__file__).resolve().parents[1]
        sample = root / "examples" / "signals.sample.json"
        with tempfile.TemporaryDirectory() as directory:
            report = Path(directory) / "report.json"
            dashboard = Path(directory) / "nested" / "dashboard.html"
            database = Path(directory) / "history.sqlite3"
            result = subprocess.run([
                sys.executable, "-m", "mdv14", str(sample),
                "--database", str(database), "--output", str(report),
                "--dashboard", str(dashboard),
            ], cwd=root, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertTrue(report.is_file())
            self.assertTrue(dashboard.is_file())
            payload = json.loads(report.read_text(encoding="utf-8"))
            self.assertTrue(payload["signals"])
            self.assertIn("advanced_intelligence", payload["signals"][0])
            self.assertIn("source_intelligence", payload["signals"][0])
            self.assertEqual(payload["source_intelligence_summary"]["reputation_verdicts_issued"], 0)
            self.assertEqual(
                payload["signals"][0]["advanced_intelligence"]["confidence"],
                "insufficient",
            )
            html = dashboard.read_text(encoding="utf-8")
            self.assertIn("Advanced trend intelligence", html)
            self.assertIn("Source intelligence &amp; provenance", html)
            self.assertIn("Reliability verdict", html)
            self.assertIn("Momentum", html)
            self.assertNotIn("https://fonts.googleapis.com", html)


if __name__ == "__main__":
    unittest.main()
