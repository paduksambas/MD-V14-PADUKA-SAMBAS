"""Tests for Build 2.4 strategic-impact and geopolitical analysis."""
import unittest

from mdv14.strategic_impact import analyze_strategic_impact


class StrategicImpactTests(unittest.TestCase):
    def test_dimensions_are_explainable_keyword_matches(self):
        result = analyze_strategic_impact([{
            "title": "Trade tariff dispute affects semiconductor supply",
            "summary": "Technology export restrictions",
            "score": 75,
            "country": "Japan",
            "url": "https://example.com/story",
            "evidence": {"evidence_complete": True},
        }])
        item = result["assessments"][0]
        self.assertIn("economic", item["impact_dimensions"])
        self.assertIn("technology", item["impact_dimensions"])
        self.assertEqual(item["attention_level"], "high_attention")
        self.assertEqual(item["metadata_confidence"], "metadata_supported")

    def test_cross_border_candidate_requires_explicit_shared_metadata(self):
        result = analyze_strategic_impact([
            {"title": "Chip investment expands", "country": "Japan", "topics": ["Technology"], "entities": ["Acme"]},
            {"title": "Chip exports increase", "country": "Indonesia", "topics": ["Technology"], "entities": ["Acme"]},
        ])
        candidate = result["cross_border_review_candidates"][0]
        self.assertEqual(candidate["relationship_type"], "cross_border_review_candidate")
        self.assertEqual(candidate["shared_entities"], ["acme"])
        self.assertFalse(candidate["causality_verified"])

    def test_no_cross_border_claim_without_shared_entity_or_topic(self):
        result = analyze_strategic_impact([
            {"title": "Flood response", "country": "Indonesia"},
            {"title": "Election debate", "country": "Japan"},
        ])
        self.assertEqual(result["cross_border_review_candidates"], [])

    def test_unknown_metadata_is_not_inferred(self):
        result = analyze_strategic_impact([{"title": "A new development"}])
        item = result["assessments"][0]
        self.assertEqual(item["countries_explicitly_named"], [])
        self.assertEqual(item["metadata_confidence"], "insufficient_metadata")

    def test_invalid_limit_rejected_and_empty_input_supported(self):
        self.assertEqual(analyze_strategic_impact([])["signals_assessed"], 0)
        with self.assertRaises(ValueError):
            analyze_strategic_impact([], limit=0)


if __name__ == "__main__":
    unittest.main()
