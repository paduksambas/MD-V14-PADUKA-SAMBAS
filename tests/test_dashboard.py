"""Tests for the offline HTML dashboard renderer."""
import unittest

from mdv14.dashboard import build_dashboard_html


class DashboardTests(unittest.TestCase):
    def test_dashboard_contains_report_metrics_history_and_advanced_indicators(self):
        report = {
            "daily_brief": {"date": "2026-11-21"},
            "language_intelligence": {"records_with_declared_language": 2, "records_with_unknown_language": 1, "language_counts": {"English": 1, "Indonesian": 1}},
            "monitoring": {"cycle_status": "healthy", "generated_at": "2026-11-21T10:00:00Z", "feeds_succeeded": 2, "feeds_attempted": 2, "signals_collected": 3, "signals_published_within_window": 2, "signals_with_unknown_published_at": 1},
            "strategic_decision": {"review_queue": [{"priority_band": "high", "title": "Priority event", "priority_score": 82.5, "warning_level": "elevated", "source": "Desk", "url": "https://example.com/event"}]},
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
        self.assertIn("Live monitoring", html)
        self.assertIn("healthy", html)
        self.assertIn("Multilingual source coverage", html)
        self.assertIn("Indonesian", html)
        self.assertIn("Strategic decision review queue", html)
        self.assertIn("Priority event", html)
        self.assertIn("https://example.com/event", html)

    def test_dashboard_escapes_untrusted_titles_and_source_text(self):
        report = {"signals": [{
            "title": "<script>alert(1)</script>", "source": '" onclick="bad',
            "category": "Test", "score": 1,
        }]}
        html = build_dashboard_html(report)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn("&quot; onclick=&quot;bad", html)

    def test_dashboard_renders_global_country_topic_momentum_and_relations(self):
        report = {
            "signals": [],
            "global_intelligence": {
                "signals_analyzed": 2,
                "country_analysis": [{"name": "Japan", "signal_count": 2, "average_score": 72.5}],
                "topic_analysis": [{"name": "Energy", "signal_count": 2, "average_score": 72.5}],
                "rising_signals": [{
                    "title": "Battery investment", "country": "Japan",
                    "topics": ["Energy"], "score": 80, "momentum": 12,
                }],
                "related_events": [{
                    "left_title": "Battery supply update", "left_country": "Japan",
                    "right_title": "Battery investment outlook", "right_country": "Korea",
                    "relationship_basis": ["shared_explicit_topics"],
                }],
            },
        }
        html = build_dashboard_html(report)
        self.assertIn("Global intelligence overview", html)
        self.assertIn("Country activity", html)
        self.assertIn("Topic activity", html)
        self.assertIn("Japan", html)
        self.assertIn("Energy", html)
        self.assertIn("Battery investment", html)
        self.assertIn("Related-event discovery", html)
        self.assertIn("shared_explicit_topics", html)
        self.assertIn("not evidence of causality", html)

    def test_global_dashboard_escapes_untrusted_labels(self):
        report = {
            "signals": [],
            "global_intelligence": {
                "country_analysis": [{"name": "<img src=x onerror=alert(1)>", "signal_count": 1, "average_score": 90}],
                "topic_analysis": [],
                "rising_signals": [],
                "related_events": [],
            },
        }
        html = build_dashboard_html(report)
        self.assertNotIn("<img src=x onerror=alert(1)>", html)
        self.assertIn("&lt;img", html)

    def test_empty_report_renders(self):
        html = build_dashboard_html({"signals": [], "daily_brief": {}})
        self.assertIn("No trend signals", html)


if __name__ == "__main__":
    unittest.main()
