"""Tests for the offline HTML dashboard renderer."""
import unittest

from mdv14.dashboard import build_dashboard_html


class DashboardTests(unittest.TestCase):
    def test_dashboard_contains_report_metrics_history_and_advanced_indicators(self):
        report = {
            "daily_brief": {"date": "2026-11-21"},
            "warning_summary": {"normal": 0, "watch": 0, "elevated": 1, "critical": 0},
            "signals": [{
                "title": "Trend A", "category": "Technology", "score": 74,
                "source": "Research Desk",
                "warning": {"level": "elevated"},
                "evidence": {"evidence_complete": True},
                "history": {"direction": "rising", "score_delta": 12},
                "advanced_intelligence": {
                    "momentum": 8, "acceleration": 3, "confidence": "moderate",
                    "anomaly": {"detected": False, "status": "evaluated"},
                },
            }],
        }
        html = build_dashboard_html(report)
        self.assertIn("Trend Intelligence Dashboard", html)
        self.assertIn("Trend A", html)
        self.assertIn("Technology", html)
        self.assertIn("rising", html)
        self.assertIn("Momentum", html)
        self.assertIn("Acceleration", html)
        self.assertIn("moderate", html)
        self.assertIn("Needs source review", html)

    def test_dashboard_escapes_untrusted_titles_and_source_text(self):
        report = {"signals": [{
            "title": "<script>alert(1)</script>", "source": '" onclick="bad',
            "category": "Test", "score": 1,
        }]}
        html = build_dashboard_html(report)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&quot; onclick=&quot;bad", html)

    def test_empty_report_renders(self):
        html = build_dashboard_html({"signals": [], "daily_brief": {}})
        self.assertIn("No trend signals", html)


if __name__ == "__main__":
    unittest.main()
