"""Tests for the offline HTML dashboard renderer."""
import unittest

from mdv14.dashboard import build_dashboard_html


class DashboardTests(unittest.TestCase):
    def test_dashboard_contains_report_metrics_history_and_advanced_indicators(self):
        report = {
            "daily_brief": {"date": "2026-11-21"},
            "language_intelligence": {"records_with_declared_language": 2, "records_with_unknown_language": 1, "language_counts": {"English": 1, "Indonesian": 1}},
            "knowledge_graph": {"nodes_total": 2, "edges_total": 1, "records_with_recognized_entities": 1, "nodes": [{"label": "Indonesia", "type": "country", "evidence_sources": ["title_or_summary_alias"]}], "edges": [{"relation": "mentions_entity", "source": "event:1", "target": "entity:indonesia", "supporting_record_ids": ["1"]}]},
            "analyst_report": {"executive_summary": "Analyst summary for review", "key_findings": [{"review_priority": "high", "title": "Indonesia energy review", "source": "Desk", "country": "Indonesia", "signal_id": "s-1"}], "metadata_coverage": {"records_with_incomplete_evidence_metadata": 1}, "uncertainties_and_gaps": ["Primary source not reviewed"], "recommended_human_actions": [{"priority": "high", "action": "Verify original source"}]},
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
        self.assertIn("Cross-language knowledge graph", html)
        self.assertIn("Indonesia", html)
        self.assertIn("mentions_entity", html)
        self.assertIn("Analyst strategic report", html)
        self.assertIn("Analyst summary for review", html)
        self.assertIn("Verify original source", html)
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

    def test_dashboard_renders_build_3_command_center(self):
        report = {
            "signals": [{"title": "Signal A", "score": 80}],
            "command_center": {
                "build": "3.0", "generated_at": "2026-11-21T10:00:00Z",
                "operational_state": "degraded",
                "collection_cycle": {"status": "degraded", "feeds_attempted": 4, "feeds_succeeded": 3},
                "strategic_posture": {"status": "priority_review_required",
                    "note": "Review required", "high_review_priority": 1, "evidence_review_required": 1},
                "coverage": {"signals_analyzed": 1},
                "priority_review_queue": [{"priority_band": "high", "title": "Signal A",
                    "country": "Indonesia", "source": "Desk", "signal_id": "s1"}],
                "decision_gates": ["Verify primary sources", "<script>must escape</script>"],
            },
        }
        html = build_dashboard_html(report)
        self.assertIn("Global Strategic Intelligence Command Center", html)
        self.assertIn("priority_review_required", html)
        self.assertIn("Signal A", html)
        self.assertIn("Verify primary sources", html)
        self.assertNotIn("<script>must escape</script>", html)
        self.assertIn("&lt;script&gt;", html)

    def test_dashboard_renders_interactive_country_explorer_and_escapes_labels(self):
        report = {
            "signals": [],
            "economic_data": {"build": "3.3", "provider": "World Bank Indicators API",
                "countries_requested": ["ID"], "year_range": {"start": 2023, "end": 2024},
                "observation_count": 1, "requests_succeeded": 1, "requests_failed": 0,
                "observations": [{"country": "Indonesia", "country_code": "ID", "indicator": "GDP growth",
                    "year": "2023", "value": 5.05, "unit": "%", "source": "World Bank"}], "errors": []},
            "economic_intelligence": {"build": "3.2", "signals_assessed": 1, "sector_count": 1,
                "coverage": {"input_records": 1, "records_classified": 1, "records_without_sector_match": 0},
                "sector_summaries": [{"sector": "energy", "label": "Energy", "signal_count": 1,
                "average_signal_score": 80, "high_attention_count": 1, "countries_named": ["Indonesia"],
                "potential_review_channels": ["Energy supply and infrastructure"], "signals": []}],
                "country_mentions": [{"country": "Indonesia", "signal_mentions": 1}],
                "priority_review_queue": [{"title": "Oil supply update", "sectors": ["energy"],
                    "countries_explicitly_named": ["Indonesia"], "source": "Desk", "score": 80,
                    "warning_level": "elevated", "signal_id": "e1", "url": "https://example.org/oil"}]},
            "country_explorer": {
                "countries_total": 2, "countries_mapped": 1, "countries_unmapped": 1,
                "signals_with_country": 3,
                "mapped_countries": [{
                    "name": "Indonesia", "canonical_name": "indonesia",
                    "latitude": -0.79, "longitude": 113.92, "signal_count": 2,
                    "average_score": 60, "review_priority_counts": {"high": 1, "medium": 0, "routine": 1},
                    "records": [{"signal_id": "s1", "title": "<script>bad</script>", "source": "Desk",
                                 "priority_band": "high", "warning_level": "elevated",
                                 "url": "https://example.org/story"}],
                }],
                "unmapped_countries": [{
                    "name": "Unknownland", "signal_count": 1, "average_score": 20,
                    "review_priority_counts": {"high": 0, "medium": 0, "routine": 0},
                }],
            },
        }
        html = build_dashboard_html(report)
        self.assertIn("Global Economic Intelligence &amp; Strategic Market Impact", html)
        self.assertIn("Official Economic Indicators", html)
        self.assertIn("World Bank Indicators API", html)
        self.assertIn("Indonesia", html)
        self.assertIn("Traceable economic signal review queue", html)
        self.assertIn("Energy supply and infrastructure", html)
        self.assertIn("No asset prices", html)
        self.assertIn("Global Geopolitical Intelligence Map", html)
        self.assertIn('data-country-key="indonesia"', html)
        self.assertIn("country-marker", html)
        self.assertIn("Unknownland", html)
        self.assertIn("Open source", html)
        self.assertNotIn("<script>bad</script>", html)
        self.assertIn("&lt;script&gt;bad&lt;/script&gt;", html)
        self.assertIn("review-order cues", html)

    def test_dashboard_renders_build_3_5_market_analytics(self):
        report = {
            "signals": [],
            "market_analytics": {
                "build": "3.5", "status": "available",
                "series_analyzed": 1, "observations_analyzed": 3,
                "summaries": [{
                    "series_id": "USDIDR", "series": "U.S. Dollar to Indonesian Rupiah",
                    "category": "foreign_exchange", "first_date": "2026-11-18",
                    "latest_date": "2026-11-20", "first_value": 16000,
                    "latest_value": 16100, "absolute_change": 100,
                    "percentage_change": 0.625, "direction": "rising",
                    "unit": "IDR per USD", "observed_step_volatility_pct": 0.2,
                }],
                "limitations": ["Descriptive only."],
            },
        }
        html = build_dashboard_html(report)
        self.assertIn("Cross-Asset Market Analytics", html)
        self.assertIn("USDIDR", html)
        self.assertIn("0.625%", html)
        self.assertIn("Observed-step volatility", html)

    def test_dashboard_renders_build_3_6_public_assets(self):
        report = {
            "signals": [],
            "public_asset_data": {
                "build": "3.6", "status": "available", "observation_count": 1,
                "requests_succeeded": 1, "requests_failed": 0,
                "observations": [{
                    "series": "S&P 500 Index", "date": "2026-11-20",
                    "value": 6000, "unit": "index points", "source": "Stooq",
                }],
                "errors": [],
            },
        }
        html = build_dashboard_html(report)
        self.assertIn("Public Equity &amp; Commodity Data", html)
        self.assertIn("S&amp;P 500 Index", html)
        self.assertIn("not live executable prices", html)


    def test_dashboard_renders_indonesia_strategic_economic_intelligence(self):
        report = {
            "signals": [],
            "indonesia_economic_intelligence": {
                "build": "3.8", "status": "available", "indicator_count": 1,
                "commodity_channel_count": 1,
                "coverage": {"recognized_indicator_observations": 2},
                "indicators": [{
                    "indicator": "GDP growth", "domain": "macroeconomy",
                    "first_year": 2022, "latest_year": 2023, "first_value": 5.0,
                    "latest_value": 5.1, "change": 0.1, "unit": "%",
                    "direction": "rising",
                }],
                "commodity_channels": [{
                    "label": "Energi dan biaya produksi",
                    "channels": ["Biaya impor energi dan subsidi"],
                    "benchmark_series": [{"series": "Brent", "value": 80,
                        "unit": "USD per barrel", "date": "2026-09-01"}],
                    "interpretation": "Qualitative monitoring channel only.",
                }],
            },
        }
        html = build_dashboard_html(report)
        self.assertIn("Indonesia Strategic Economic Intelligence", html)
        self.assertIn("GDP growth", html)
        self.assertIn("Energi dan biaya produksi", html)
        self.assertIn("Qualitative monitoring channel", html)

    def test_empty_report_renders(self):
        html = build_dashboard_html({"signals": [], "daily_brief": {}})
        self.assertIn("No trend signals", html)


if __name__ == "__main__":
    unittest.main()
