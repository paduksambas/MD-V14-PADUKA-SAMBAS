"""Tests for the Build 3.0 strategic intelligence command center."""
import unittest

from mdv14.command_center import build_command_center


class CommandCenterTests(unittest.TestCase):
    def test_unifies_collection_posture_coverage_and_review_queue(self):
        report = {
            "signals": [{"title": "Energy", "score": 80}],
            "monitoring": {
                "cycle_status": "degraded", "generated_at": "2026-11-21T10:00:00Z",
                "feeds_attempted": 4, "feeds_succeeded": 3, "feeds_failed": 1,
                "signals_collected": 12, "signals_published_within_window": 8,
                "signals_with_unknown_published_at": 2,
            },
            "strategic_decision": {
                "priority_band_counts": {"high": 1, "medium": 2, "routine": 4},
                "review_queue": [{"signal_id": "s1", "title": "Energy", "priority_band": "high",
                                  "priority_score": 88, "warning_level": "critical",
                                  "source": "Desk", "url": "https://example.org/a", "country": "Indonesia"}],
            },
            "warning_summary": {"critical": 1, "elevated": 2},
            "evidence_review_required": 3,
            "global_intelligence": {
                "country_analysis": [{"name": "Indonesia", "signal_count": 5}],
                "topic_analysis": [{"name": "Energy", "signal_count": 4}],
            },
            "analyst_report": {"key_findings": [{}], "uncertainties_and_gaps": ["gap"],
                               "recommended_human_actions": [{}]},
        }
        result = build_command_center(report)
        self.assertEqual(result["build"], "3.0")
        self.assertEqual(result["operational_state"], "degraded")
        self.assertEqual(result["strategic_posture"]["status"], "priority_review_required")
        self.assertEqual(result["coverage"]["country_leaders"][0]["name"], "Indonesia")
        self.assertEqual(result["priority_review_queue"][0]["signal_id"], "s1")
        self.assertEqual(result["analyst_report"]["human_actions"], 1)
        self.assertEqual(len(result["decision_gates"]), 4)

    def test_empty_report_does_not_claim_operational_or_strategic_readiness(self):
        result = build_command_center({"signals": []})
        self.assertEqual(result["operational_state"], "not_assessed")
        self.assertEqual(result["strategic_posture"]["status"], "insufficient_data")
        self.assertEqual(result["priority_review_queue"], [])

    def test_validation_and_queue_limit(self):
        with self.assertRaises(ValueError):
            build_command_center({}, limit=0)
        result = build_command_center({
            "signals": [{"title": "one"}],
            "strategic_decision": {"review_queue": [{"title": str(i)} for i in range(5)]},
        }, limit=2)
        self.assertEqual(len(result["priority_review_queue"]), 2)


if __name__ == "__main__":
    unittest.main()
