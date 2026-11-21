"""Tests for advanced trend intelligence indicators."""
import unittest

from mdv14.advanced_scoring import assess_advanced_trend


class AdvancedScoringTests(unittest.TestCase):
    def test_insufficient_history_does_not_invent_momentum(self):
        result = assess_advanced_trend([{"score": 40}])
        self.assertIsNone(result["momentum"])
        self.assertIsNone(result["acceleration"])
        self.assertIsNone(result["attention_potential_index"])
        self.assertEqual(result["confidence"], "insufficient")

    def test_momentum_acceleration_and_index(self):
        result = assess_advanced_trend(
            [{"score": 20}, {"score": 30}, {"score": 45}]
        )
        self.assertEqual(result["momentum"], 15.0)
        self.assertEqual(result["acceleration"], 5.0)
        self.assertEqual(result["attention_potential_index"], 52.5)
        self.assertEqual(result["momentum_direction"], "rising")
        self.assertEqual(result["confidence"], "moderate")

    def test_flat_history_is_stable(self):
        result = assess_advanced_trend([{"score": 50}, {"score": 50}])
        self.assertEqual(result["momentum"], 0.0)
        self.assertEqual(result["momentum_direction"], "stable")
        self.assertIsNone(result["acceleration"])

    def test_anomaly_requires_five_observations_and_flags_jump(self):
        short = assess_advanced_trend([{"score": x} for x in (10, 11, 10, 11)])
        self.assertEqual(short["anomaly"]["status"], "insufficient_history")
        long = assess_advanced_trend([{"score": x} for x in (10, 11, 10, 11, 12, 60)])
        self.assertEqual(long["anomaly"]["status"], "evaluated")
        self.assertTrue(long["anomaly"]["detected"])

    def test_scores_are_bounded_and_invalid_values_ignored(self):
        result = assess_advanced_trend(
            [{"score": -5}, {"score": 120}, {"score": "bad"}]
        )
        self.assertEqual(result["observation_count"], 2)
        self.assertEqual(result["momentum"], 0.0)


if __name__ == "__main__":
    unittest.main()
