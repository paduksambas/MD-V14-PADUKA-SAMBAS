"""Integration tests for the MD V14 intelligence pipeline."""
import unittest

from mdv14.early_warning import WarningThresholds, classify_signal
from mdv14.fact_check import assess_evidence
from mdv14.pipeline import run_pipeline
from mdv14.trend_registry import TrendRegistry, signal_id


class PipelineTests(unittest.TestCase):
    def test_registry_deduplicates_same_title_and_url(self):
        registry = TrendRegistry([
            {"title": "Topic", "url": "https://example.com/a", "score": 20},
            {"title": "Topic", "url": "https://example.com/a", "score": 80},
        ])
        self.assertEqual(len(registry), 1)
        self.assertEqual(registry.all()[0]["score"], 80)

    def test_registry_rejects_missing_title(self):
        with self.assertRaises(ValueError):
            TrendRegistry([{"source": "Desk"}])

    def test_warning_boundaries(self):
        self.assertEqual(classify_signal({"score": 80})["level"], "critical")
        self.assertEqual(classify_signal({"score": 60})["level"], "elevated")
        self.assertEqual(classify_signal({"score": 40})["level"], "watch")
        self.assertEqual(classify_signal({"score": 39.9})["level"], "normal")

    def test_threshold_validation(self):
        with self.assertRaises(ValueError):
            WarningThresholds(watch=70, elevated=60, critical=80)

    def test_evidence_does_not_claim_truth(self):
        result = assess_evidence({
            "title": "Claim", "source": "Example", "url": "https://example.com"
        })
        self.assertTrue(result["evidence_complete"])
        self.assertFalse(result["truth_verified"])

    def test_pipeline_integrates_all_stages(self):
        result = run_pipeline([
            {"title": "Major signal", "source": "Example Desk",
             "url": "https://example.com/story", "score": 85,
             "category": "Technology"}
        ], brief_date="2026-11-21")
        self.assertEqual(result["registry_size"], 1)
        self.assertEqual(result["warning_summary"]["critical"], 1)
        self.assertEqual(result["daily_brief"]["signals_included"], 1)
        self.assertFalse(result["signals"][0]["evidence"]["truth_verified"])


if __name__ == "__main__":
    unittest.main()
