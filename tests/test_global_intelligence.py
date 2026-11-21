"""Tests for Build 2.0 global trend intelligence."""
import unittest

from mdv14.global_intelligence import analyze_global_trends


class GlobalIntelligenceTests(unittest.TestCase):
    def test_country_and_topic_summaries_use_explicit_metadata(self):
        result = analyze_global_trends([
            {"title": "AI chip exports", "country": "Indonesia", "topics": ["Technology"], "score": 70},
            {"title": "AI chip investment", "country": "Japan", "topics": ["Technology"], "score": 80},
            {"title": "Flood response", "score": 40},
        ])
        self.assertEqual(result["signals_analyzed"], 3)
        self.assertEqual(result["country_analysis"][0]["name"], "Indonesia")
        self.assertEqual(result["topic_analysis"][0]["name"], "Technology")
        self.assertEqual(result["country_analysis"][-1]["name"], "unknown")

    def test_momentum_requires_supplied_history(self):
        result = analyze_global_trends([
            {"title": "Energy transition", "score": 60},
            {"title": "Battery investment", "score": 50,
             "score_history": [{"score": 30}, {"score": 40}, {"score": 50}]},
        ])
        self.assertEqual(result["signal_momentum"][0]["momentum"], None)
        self.assertEqual(result["signal_momentum"][1]["momentum"], 10.0)
        self.assertEqual(len(result["rising_signals"]), 1)

    def test_related_events_explain_shared_basis_without_causality(self):
        result = analyze_global_trends([
            {"title": "Semiconductor supply chain disruption", "country": "Taiwan",
             "topics": ["Technology"], "entities": ["Acme Corp"]},
            {"title": "Semiconductor investment outlook", "country": "Japan",
             "topics": ["Technology"], "entities": ["Acme Corp"]},
        ])
        relation = result["related_events"][0]
        self.assertTrue(relation["cross_country"])
        self.assertIn("shared_explicit_entities", relation["relationship_basis"])
        self.assertFalse(relation["causality_verified"])

    def test_invalid_limits_are_rejected(self):
        with self.assertRaises(ValueError):
            analyze_global_trends([], limit=0)
        with self.assertRaises(ValueError):
            analyze_global_trends([], relation_limit=-1)

    def test_empty_input_is_valid_and_transparent(self):
        result = analyze_global_trends([])
        self.assertEqual(result["signals_analyzed"], 0)
        self.assertEqual(result["country_analysis"], [])
        self.assertEqual(result["related_events"], [])


if __name__ == "__main__":
    unittest.main()
