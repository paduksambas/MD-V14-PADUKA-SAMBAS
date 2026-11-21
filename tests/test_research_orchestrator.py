"""Tests for Build 2.3 auditable multi-source research orchestration."""
import unittest

from mdv14.research_orchestrator import build_research_report


class ResearchOrchestratorTests(unittest.TestCase):
    def test_question_ranks_literal_keyword_matches(self):
        report = build_research_report("AI semiconductor investment", [
            {"title": "Flood response", "source": "Desk A"},
            {"title": "AI semiconductor investment expands", "source": "Desk B",
             "country": "Japan", "summary": "New chip investment"},
        ])
        self.assertEqual(report["research_candidates"][0]["source"], "Desk B")
        self.assertEqual(report["records_with_keyword_match"], 1)

    def test_collection_failures_and_evidence_gaps_are_reported(self):
        report = build_research_report("energy", [
            {"title": "Energy transition", "source": "Desk A",
             "evidence": {"evidence_complete": False}},
        ], {"feeds_attempted": 2, "feeds_succeeded": 1, "feeds_failed": 1,
            "feed_results": [{"ok": True}, {"ok": False}], "items_collected": 1})
        self.assertEqual(report["collection_health"]["feeds_failed"], 1)
        self.assertTrue(any("feed" in gap for gap in report["research_gaps"]))
        self.assertTrue(any("evidence" in gap for gap in report["research_gaps"]))

    def test_empty_collection_is_transparent(self):
        report = build_research_report("climate risk", [], {"feeds_attempted": 1,
            "feeds_succeeded": 0, "feeds_failed": 1, "feed_results": [{"ok": False}]})
        self.assertEqual(report["records_reviewed"], 0)
        self.assertTrue(report["research_gaps"])

    def test_no_question_disables_relevance_scoring(self):
        report = build_research_report("", [{"title": "Story", "source": "Desk"}])
        self.assertIsNone(report["research_candidates"][0]["relevance_score"])

    def test_invalid_limit_rejected(self):
        with self.assertRaises(ValueError):
            build_research_report("topic", [], limit=0)


if __name__ == "__main__":
    unittest.main()
