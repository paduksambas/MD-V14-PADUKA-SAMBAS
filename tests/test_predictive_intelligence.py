"""Tests for Build 2.2 predictive outlook indicators."""
import unittest

from mdv14.predictive_intelligence import assess_predictive_outlook


class PredictiveIntelligenceTests(unittest.TestCase):
    def test_insufficient_history_does_not_project(self):
        result = assess_predictive_outlook({"score": 55})
        self.assertEqual(result["status"], "insufficient_history")
        self.assertIsNone(result["projected_score"])
        self.assertFalse(result["early_warning_triggered"])

    def test_rising_signal_projects_threshold_crossing(self):
        result = assess_predictive_outlook({
            "score": 58,
            "score_history": [{"score": 40}, {"score": 48}, {"score": 58}],
        })
        self.assertEqual(result["outlook"], "accelerating_rise")
        self.assertEqual(result["projected_score"], 85.0)
        self.assertTrue(result["early_warning_triggered"])
        self.assertEqual(result["projected_warning_level"], "critical")
        self.assertEqual(result["estimated_observations_to_elevated"], 1)

    def test_declining_signal_does_not_raise_crossing_alert(self):
        result = assess_predictive_outlook({
            "score": 75,
            "score_history": [{"score": 90}, {"score": 82}, {"score": 75}],
        })
        self.assertEqual(result["outlook"], "declining")
        self.assertFalse(result["early_warning_triggered"])

    def test_projection_is_bounded(self):
        result = assess_predictive_outlook({
            "score": 95,
            "score_history": [{"score": 70}, {"score": 80}, {"score": 95}],
        })
        self.assertEqual(result["projected_score"], 100.0)

    def test_invalid_horizon_is_rejected(self):
        with self.assertRaises(ValueError):
            assess_predictive_outlook({"score": 10}, horizon_observations=0)


if __name__ == "__main__":
    unittest.main()
