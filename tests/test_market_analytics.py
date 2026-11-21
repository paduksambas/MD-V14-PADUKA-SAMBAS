import unittest

from mdv14.market_analytics import build_market_analytics, render_market_analytics_html


class MarketAnalyticsTests(unittest.TestCase):
    def test_calculates_per_series_change_and_observed_step_volatility(self):
        result = build_market_analytics({
            "observations": [
                {"series_id": "USDIDR", "series": "USD to IDR", "category": "fx",
                 "date": "2026-11-18", "value": 16000, "unit": "IDR per USD", "source": "Frankfurter"},
                {"series_id": "USDIDR", "series": "USD to IDR", "category": "fx",
                 "date": "2026-11-19", "value": 16160, "unit": "IDR per USD", "source": "Frankfurter"},
                {"series_id": "USDIDR", "series": "USD to IDR", "category": "fx",
                 "date": "2026-11-20", "value": 16000, "unit": "IDR per USD", "source": "Frankfurter"},
            ]
        })
        self.assertEqual(result["build"], "3.5")
        self.assertEqual(result["series_analyzed"], 1)
        item = result["summaries"][0]
        self.assertEqual(item["direction"], "unchanged")
        self.assertEqual(item["absolute_change"], 0)
        self.assertEqual(item["percentage_change"], 0)
        self.assertIsNotNone(item["observed_step_volatility_pct"])
        self.assertEqual(item["volatility_observations"], 2)

    def test_keeps_series_independent_and_zero_start_percentage_missing(self):
        result = build_market_analytics(
            {"observations": [{"series_id": "A", "date": "2026-01-01", "value": 0},
                              {"series_id": "A", "date": "2026-01-02", "value": 3}]},
            {"observations": [{"series_id": "B", "date": "2026-01-01", "value": 100},
                              {"series_id": "B", "date": "2026-01-02", "value": 110}]},
        )
        self.assertEqual(result["series_analyzed"], 2)
        a = next(x for x in result["summaries"] if x["series_id"] == "A")
        b = next(x for x in result["summaries"] if x["series_id"] == "B")
        self.assertIsNone(a["percentage_change"])
        self.assertEqual(b["percentage_change"], 10)
        self.assertEqual(b["direction"], "rising")

    def test_ignores_invalid_rows_and_reports_insufficient_volatility(self):
        result = build_market_analytics({"observations": [
            {"series_id": "X", "date": "2026-01-01", "value": 2},
            {"series_id": "X", "date": "bad", "value": 4},
            {"series_id": "X", "date": "2026-01-02", "value": 3},
            {"series_id": "", "date": "2026-01-03", "value": 5},
        ]})
        item = result["summaries"][0]
        self.assertEqual(item["observation_count"], 2)
        self.assertIsNone(item["observed_step_volatility_pct"])
        self.assertEqual(item["status"], "evaluated")

    def test_empty_input_is_explicit(self):
        result = build_market_analytics({"observations": []})
        self.assertEqual(result["status"], "no_data")
        self.assertEqual(result["series_analyzed"], 0)

    def test_dashboard_escapes_untrusted_values(self):
        html = render_market_analytics_html({
            "status": "available", "series_analyzed": 1, "observations_analyzed": 2,
            "summaries": [{"series": "<script>", "series_id": "X", "category": "fx",
                "first_date": "2026-01-01", "latest_date": "2026-01-02",
                "first_value": 1, "latest_value": 2, "absolute_change": 1,
                "percentage_change": 100, "direction": "rising", "unit": "units",
                "observed_step_volatility_pct": None}],
            "limitations": ["safe"],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("Cross-Asset Market Analytics", html)


if __name__ == "__main__":
    unittest.main()
