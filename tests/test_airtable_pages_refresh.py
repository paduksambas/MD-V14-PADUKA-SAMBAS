import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AirtablePagesRefreshWorkflowTests(unittest.TestCase):
    def test_pages_rebuilds_after_successful_main_monitoring_run(self):
        workflow = (ROOT / ".github" / "workflows" / "pages-deploy.yml").read_text(encoding="utf-8")
        self.assertIn('workflow_run:', workflow)
        self.assertIn('workflows: ["Scheduled global intelligence monitoring"]', workflow)
        self.assertIn('types: [completed]', workflow)
        self.assertIn('branches: [main]', workflow)
        self.assertIn("github.event.workflow_run.conclusion == 'success'", workflow)

    def test_pages_refresh_still_uses_airtable_live_export_or_snapshot_fallback(self):
        script = (ROOT / "scripts" / "build_public_dashboard.sh").read_text(encoding="utf-8")
        self.assertIn("python scripts/airtable_bps.py --export-dashboard", script)
        self.assertIn("examples/airtable-bps-dashboard.json", script)
        self.assertIn("AIRTABLE_API_TOKEN", script)


if __name__ == "__main__":
    unittest.main()
