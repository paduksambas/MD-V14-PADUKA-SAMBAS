"""Integration tests for the MD V14 intelligence pipeline."""
import unittest

from mdv14.early_warning import WarningThresholds, classify_signal
from mdv14.fact_check import assess_evidence
from mdv14.pipeline import run_pipeline
from mdv14.trend_registry import TrendRegistry


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

    def test_registry_preserves_supplied_provenance_metadata(self):
        registry = TrendRegistry([{
            "title": "Topic", "url": "https://example.com/a",
            "author": "Reporter", "published_at": "2026-11-21T09:00:00Z",
            "source_profile": {"ownership_url": "https://example.com/about"},
        }])
        item = registry.all()[0]
        self.assertEqual(item["author"], "Reporter")
        self.assertIn("source_profile", item)

    def test_warning_boundaries(self):
        self.assertEqual(classify_signal({"score": 80})["level"], "critical")
        self.assertEqual(classify_signal({"score": 60})["level"], "elevated")
        self.assertEqual(classify_signal({"score": 40})["level"], "watch")
        self.assertEqual(classify_signal({"score": 39.9})["level"], "normal")

    def test_invalid_url_is_not_evidence_complete(self):
        result = assess_evidence({
            "title": "Claim", "source": "Example", "url": "javascript:alert(1)"
        })
        self.assertFalse(result["evidence_complete"])
        self.assertFalse(result["source_url_valid"])

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
        result = run_pipeline([{
            "title": "Major signal", "source": "Example Desk",
            "url": "https://example.com/story", "score": 85,
            "category": "Technology", "author": "Reporter",
            "published_at": "2026-11-21T09:00:00Z",
        }], brief_date="2026-11-21")
        self.assertEqual(result["registry_size"], 1)
        self.assertEqual(result["global_intelligence"]["build"], "2.0")
        self.assertEqual(result["strategic_impact"]["build"], "2.4")
        self.assertEqual(result["strategic_impact"]["signals_assessed"], 1)
        self.assertEqual(result["global_intelligence"]["signals_analyzed"], 1)
        self.assertEqual(result["data_schema_version"], "1.0")
        self.assertEqual(result["data_coverage"]["records_total"], 1)
        self.assertEqual(result["signals"][0]["data_schema_version"], "1.0")
        self.assertEqual(result["warning_summary"]["critical"], 1)
        self.assertEqual(result["daily_brief"]["signals_included"], 1)
        self.assertFalse(result["signals"][0]["evidence"]["truth_verified"])
        intelligence = result["signals"][0]["source_intelligence"]
        self.assertEqual(intelligence["reliability_verdict"], "not_assessed")
        self.assertEqual(intelligence["source_domain"], "example.com")
        self.assertTrue(intelligence["checks"]["author_attribution_present"])
        brief_signal = result["daily_brief"]["top_signals"][0]
        self.assertIn("evidence", brief_signal)
        self.assertIn("warning", brief_signal)
        self.assertIn("source_intelligence", brief_signal)
        self.assertEqual(brief_signal["warning"]["level"], "critical")
        self.assertEqual(result["source_intelligence_summary"]["reputation_verdicts_issued"], 0)


if __name__ == "__main__":
    unittest.main()
