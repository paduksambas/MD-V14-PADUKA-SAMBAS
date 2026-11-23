import json
import tempfile
import unittest
from pathlib import Path

from mdv14.airtable_regional import load_airtable_regional_snapshot
from mdv14.regional_intelligence import build_regional_intelligence, render_regional_intelligence_html


ROOT = Path(__file__).resolve().parents[1]


class AirtableRegionalSnapshotTests(unittest.TestCase):
    def test_repository_snapshot_loads_as_pending_validation(self):
        result = load_airtable_regional_snapshot(ROOT / "examples" / "airtable-bps-regional.json")
        self.assertEqual(result["provider"], "Airtable")
        self.assertEqual(result["status"], "pending_validation")
        self.assertEqual(result["records_read"], 2)
        self.assertEqual(result["valid_count"], 0)
        self.assertEqual(result["pending_validation_count"], 2)
        self.assertEqual(result["rejected_count"], 0)
        self.assertEqual(result["pending_observations"][0]["region_code"], "6101")
        self.assertEqual(result["pending_observations"][0]["value"], 4.99)

    def test_only_explicitly_valid_rows_are_eligible_for_rankings(self):
        payload = {
            "base_name": "PADUKA — Data Regional BPS Sambas",
            "table_name": "Observasi Regional",
            "snapshot_date": "2026-11-23",
            "observations": [
                {
                    "region_code": "6101", "region_name": "Kabupaten Sambas",
                    "level": "regency_city", "indicator_code": "163",
                    "indicator_name": "TPT", "period": "2024", "value": 4.99,
                    "unit": "Persen", "validation_status": "Valid",
                },
                {
                    "region_code": "6101", "region_name": "Kabupaten Sambas",
                    "level": "regency_city", "indicator_code": "168",
                    "indicator_name": "EPR", "period": "2024", "value": 69.15,
                    "unit": "Persen", "validation_status": "Belum ditinjau",
                },
            ],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = load_airtable_regional_snapshot(path)

        self.assertEqual(result["status"], "partial")
        self.assertEqual(result["valid_count"], 1)
        self.assertEqual(result["pending_validation_count"], 1)
        regional = build_regional_intelligence({"observations": result["observations"]})
        self.assertEqual(regional["observation_count"], 1)
        self.assertEqual(len(regional["rankings"]), 1)
        self.assertEqual(regional["rankings"][0]["indicator_code"], "163")
        self.assertNotIn("168", [item["indicator_code"] for item in regional["rankings"]])

    def test_pending_values_render_in_review_table_not_rankings(self):
        airtable = load_airtable_regional_snapshot(ROOT / "examples" / "airtable-bps-regional.json")
        regional = build_regional_intelligence({"observations": airtable["observations"]})
        regional["status"] = "pending_validation"
        regional["airtable"] = airtable
        html = render_regional_intelligence_html(regional)

        self.assertIn("Observasi Airtable", html)
        self.assertIn("4.99 Persen", html)
        self.assertIn("69.15 Persen", html)
        self.assertIn("Belum ditinjau", html)
        self.assertIn("tidak dipakai dalam ranking", html.lower())
        self.assertIn("No comparable regional indicator observations loaded.", html)

    def test_unknown_validation_state_is_not_accepted(self):
        payload = {
            "observations": [{
                "region_code": "6101", "region_name": "Kabupaten Sambas",
                "level": "regency_city", "indicator_code": "163",
                "indicator_name": "TPT", "period": "2024", "value": 4.99,
                "validation_status": "Maybe",
            }],
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "snapshot.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = load_airtable_regional_snapshot(path)

        self.assertEqual(result["status"], "no_data")
        self.assertEqual(result["valid_count"], 0)
        self.assertEqual(result["pending_validation_count"], 0)
        self.assertEqual(result["rejected_count"], 1)


if __name__ == "__main__":
    unittest.main()
