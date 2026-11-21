"""Tests for the optional FRED market-data adapter."""
import unittest
from unittest.mock import patch

from mdv14.market_data import (fetch_fred_market_data, render_fred_html,
                                fetch_public_market_data, render_public_market_html)


class FredMarketDataTests(unittest.TestCase):
    @patch("mdv14.market_data._fetch_fred")
    def test_normalizes_official_observations(self, fetch):
        fetch.return_value = {"observations": [
            {"date": "2026-01-02", "value": "15600.5"},
            {"date": "2026-01-03", "value": "."},
        ]}
        result = fetch_fred_market_data("secret", start_date="2026-01-01",
                                        end_date="2026-01-31", series_ids=["DEXIDUS"])
        self.assertEqual(result["build"], "3.4")
        self.assertEqual(result["observation_count"], 1)
        item = result["observations"][0]
        self.assertEqual(item["unit"], "IDR per USD")
        self.assertEqual(item["value"], 15600.5)
        self.assertNotIn("secret", item["source_url"])

    def test_missing_key_is_explicit_and_does_not_fetch(self):
        result = fetch_fred_market_data(None, series_ids=["SP500"])
        self.assertEqual(result["status"], "not_configured")
        self.assertEqual(result["request_count"], 0)
        self.assertEqual(result["observation_count"], 0)

    def test_rejects_unknown_series_and_invalid_dates(self):
        with self.assertRaises(ValueError):
            fetch_fred_market_data("x", series_ids=["UNKNOWN"])
        with self.assertRaises(ValueError):
            fetch_fred_market_data("x", start_date="2026/01/01", series_ids=["SP500"])
        with self.assertRaises(ValueError):
            fetch_fred_market_data("x", start_date="2026-02-01",
                                   end_date="2026-01-01", series_ids=["SP500"])

    @patch("mdv14.market_data._fetch_fred")
    def test_isolates_provider_failures_and_redacts_key(self, fetch):
        fetch.side_effect = RuntimeError("bad key secret")
        result = fetch_fred_market_data("secret", series_ids=["SP500"])
        self.assertEqual(result["requests_failed"], 1)
        self.assertNotIn("secret", str(result))
        self.assertEqual(result["observations"], [])

    @patch("mdv14.market_data._fetch_frankfurter")
    def test_public_fx_fetches_without_key_and_normalizes_rates(self, fetch):
        fetch.return_value = [
            {"date": "2026-11-20", "base": "USD", "quote": "IDR", "rate": 16500.0},
            {"date": "2026-11-20", "base": "USD", "quote": "EUR", "rate": 0.87},
            {"date": "2026-11-20", "base": "USD", "quote": "XYZ", "rate": 1.0},
        ]
        result = fetch_public_market_data(start_date="2026-11-20", end_date="2026-11-21")
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["observation_count"], 2)
        self.assertEqual(result["observations"][0]["unit"], "IDR per USD")
        self.assertEqual(result["observations"][0]["value"], 16500.0)
        fetch.assert_called_once()

    def test_public_fx_validates_dates_and_range(self):
        with self.assertRaises(ValueError):
            fetch_public_market_data(start_date="2026/01/01", end_date="2026-01-02")
        with self.assertRaises(ValueError):
            fetch_public_market_data(start_date="2025-01-01", end_date="2026-11-21")

    @patch("mdv14.market_data._fetch_frankfurter")
    def test_public_fx_provider_failure_is_explicit(self, fetch):
        fetch.side_effect = RuntimeError("service unavailable")
        result = fetch_public_market_data(start_date="2026-11-20", end_date="2026-11-21")
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["observation_count"], 0)
        self.assertEqual(result["requests_failed"], 1)

    def test_public_fx_dashboard_escapes_provider_data(self):
        html = render_public_market_html({
            "status": "available", "observation_count": 1,
            "requests_succeeded": 1, "requests_failed": 0,
            "observations": [{"series": "<script>", "date": "2026-11-20",
                              "value": 1, "unit": "IDR per USD", "source": "x"}],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)

    def test_dashboard_escapes_provider_data(self):
        html = render_fred_html({
            "status": "available", "observation_count": 1,
            "requests_succeeded": 1, "requests_failed": 0,
            "observations": [{"series": "<script>", "date": "2026-01-01",
                              "value": 1, "unit": "x", "frequency": "daily"}],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("not endorsed or certified by the Federal Reserve Bank of St. Louis", html)
        self.assertIn("FRED API Terms of Use", html)


if __name__ == "__main__":
    unittest.main()
