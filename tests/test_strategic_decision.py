"""Tests for Build 2.5 strategic decision fusion."""
import unittest

from mdv14.strategic_decision import build_strategic_decision_brief


class StrategicDecisionTests(unittest.TestCase):
    def test_priority_is_deterministic_and_preserves_traceability(self):
        signals = [{
            "id": "abc123", "title": "Semiconductor supply chain disruption",
            "source": "Example Desk", "url": "https://example.com/story",
            "country": "Indonesia", "score": 82,
            "warning": {"level": "critical"},
            "predictive_outlook": {"outlook": "rising", "momentum": 8},
            "evidence": {"evidence_complete": True},
        }]
        impact = {"assessments": [{
            "signal_id": "abc123", "impact_dimensions": ["economic", "technology"]
        }]}
        first = build_strategic_decision_brief(signals, strategic_impact=impact)
        second = build_strategic_decision_brief(signals, strategic_impact=impact)
        self.assertEqual(first, second)
        item = first["review_queue"][0]
        self.assertEqual(item["signal_id"], "abc123")
        self.assertEqual(item["source"], "Example Desk")
        self.assertEqual(item["url"], "https://example.com/story")
        self.assertEqual(item["impact_dimensions"], ["economic", "technology"])
        self.assertEqual(item["priority_band"], "medium")
        self.assertEqual(len(item["scoring_components"]), 4)

    def test_missing_components_are_renormalized_not_fabricated(self):
        result = build_strategic_decision_brief([{
            "title": "Sparse record", "score": 50,
            "evidence": {"evidence_complete": False},
        }])
        item = result["review_queue"][0]
        self.assertEqual(item["priority_score"], 57.69)
        self.assertEqual(item["momentum"], None)
        self.assertEqual(item["country"], "unknown")
        self.assertEqual(result["evidence_and_coverage_gaps"]["signals_missing_complete_evidence"], 1)

    def test_invalid_numeric_inputs_do_not_crash(self):
        result = build_strategic_decision_brief([{
            "title": "Invalid score", "score": float("nan"),
            "predictive_outlook": {"momentum": float("inf")},
        }])
        self.assertEqual(result["review_queue"][0]["priority_score"], 0.0)
        self.assertIsNone(result["review_queue"][0]["momentum"])

    def test_empty_input_returns_valid_empty_brief(self):
        result = build_strategic_decision_brief([])
        self.assertEqual(result["signals_fused"], 0)
        self.assertEqual(result["review_queue"], [])
        self.assertEqual(result["priority_band_counts"], {"high": 0, "medium": 0, "routine": 0})

    def test_limit_validation(self):
        with self.assertRaises(ValueError):
            build_strategic_decision_brief([], limit=0)

    def test_limit_and_context_fusion(self):
        result = build_strategic_decision_brief(
            [{"title": "A", "score": 90}, {"title": "B", "score": 20}],
            global_intelligence={"rising_signals": [{"title": "A"}]},
            predictive_summary={"early_warning_candidates": 2},
            research={"research_gaps": ["Limited source coverage"]},
            strategic_impact={"cross_border_review_candidates": [{}, {}]},
            limit=1,
        )
        self.assertEqual(len(result["review_queue"]), 1)
        self.assertEqual(result["fused_context"]["global_rising_signal_candidates"], 1)
        self.assertEqual(result["fused_context"]["predictive_early_warning_candidates"], 2)
        self.assertEqual(result["fused_context"]["strategic_cross_border_review_candidates"], 2)
        self.assertEqual(result["evidence_and_coverage_gaps"]["research_gaps"], ["Limited source coverage"])


if __name__ == "__main__":
    unittest.main()
