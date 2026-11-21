"""Tests for Build 2.9 deterministic analyst report composition."""
import unittest

from mdv14.analyst_report import build_analyst_report


class AnalystReportTests(unittest.TestCase):
    def test_report_composes_traceable_findings_and_actions(self):
        report = build_analyst_report({
            "signals": [
                {"id": "s1", "title": "Energy security review", "source": "Desk",
                 "url": "https://example.com/a", "country": "Indonesia",
                 "evidence": {"evidence_complete": True}},
                {"id": "s2", "title": "Trade policy update", "source": "Desk",
                 "url": "", "country": "unknown",
                 "evidence": {"evidence_complete": False}},
            ],
            "strategic_decision": {
                "priority_band_counts": {"high": 1, "medium": 0, "routine": 1},
                "review_queue": [{
                    "signal_id": "s2", "title": "Trade policy update", "source": "Desk",
                    "url": "", "country": "unknown", "priority_band": "high",
                    "priority_score": 75, "warning_level": "elevated",
                    "impact_dimensions": ["economic"], "evidence_complete": False,
                }],
            },
            "knowledge_graph": {"nodes_total": 3, "edges_total": 2},
            "strategic_impact": {"cross_border_review_candidates": [{}]},
            "language_intelligence": {"records_with_unknown_language": 1},
        })
        self.assertEqual(report["build"], "2.9")
        self.assertEqual(report["records_analyzed"], 2)
        self.assertEqual(report["key_findings"][0]["signal_id"], "s2")
        self.assertEqual(report["metadata_coverage"]["records_with_incomplete_evidence_metadata"], 1)
        self.assertEqual(report["strategic_context"]["knowledge_graph_edges"], 2)
        self.assertTrue(all(item["human_approval_required"] for item in report["recommended_human_actions"]))

    def test_empty_input_reports_no_evidence_without_inventing_findings(self):
        report = build_analyst_report({"signals": [], "strategic_decision": {"review_queue": []}})
        self.assertEqual(report["records_analyzed"], 0)
        self.assertEqual(report["key_findings"], [])
        self.assertIn("Belum ada rekaman", report["executive_summary"])

    def test_report_does_not_call_metadata_truth_confidence(self):
        report = build_analyst_report({"signals": [{"title": "Claim", "evidence": {"evidence_complete": True}}]})
        self.assertIn("not confidence", report["metadata_coverage"]["interpretation"])
        self.assertIn("not a connected large-language model", " ".join(report["limitations"]))

    def test_limit_validation(self):
        with self.assertRaises(ValueError):
            build_analyst_report({}, limit=0)


if __name__ == "__main__":
    unittest.main()
