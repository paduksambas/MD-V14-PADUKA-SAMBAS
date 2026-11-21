import unittest
from unittest.mock import patch

from mdv14.public_assets import fetch_public_asset_data, render_public_asset_html


class PublicAssetDataTests(unittest.TestCase):
    @patch("mdv14.public_assets._fetch_stooq")
    def test_fetches_allowlisted_daily_close_data_without_key(self, fetch):
        fetch.return_value = (
            "Date,Open,High,Low,Close,Volume\n"
            "2026-11-20,6000,6100,5900,6050,1000\n"
            "2026-11-21,6050,6200,6000,6150,1100\n"
        )
        result = fetch_public_asset_data(
            start_date="2026-11-20", end_date="2026-11-21", symbols=["^spx"]
        )
        self.assertEqual(result["build"], "3.6")
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["observation_count"], 2)
        self.assertEqual(result["observations"][0]["series_id"], "STOOQ:^spx")
        self.assertEqual(result["observations"][1]["value"], 6150.0)
        self.assertEqual(result["observations"][0]["unit"], "index points")
        fetch.assert_called_once()

    def test_validates_symbol_dates_range_and_timeout(self):
        with self.assertRaises(ValueError):
            fetch_public_asset_data(symbols=["UNKNOWN"])
        with self.assertRaises(ValueError):
            fetch_public_asset_data(start_date="2026/01/01", end_date="2026-01-02")
        with self.assertRaises(ValueError):
            fetch_public_asset_data(start_date="2025-01-01", end_date="2026-11-21")
        with self.assertRaises(ValueError):
            fetch_public_asset_data(timeout=0)

    @patch("mdv14.public_assets._fetch_stooq")
    def test_isolates_symbol_failures(self, fetch):
        fetch.side_effect = [RuntimeError("provider down"), "Date,Open,High,Low,Close,Volume\n2026-11-20,1,2,1,2,10\n"]
        result = fetch_public_asset_data(
            start_date="2026-11-20", end_date="2026-11-20", symbols=["^spx", "^ndq"]
        )
        self.assertEqual(result["requests_failed"], 1)
        self.assertEqual(result["requests_succeeded"], 1)
        self.assertEqual(result["observation_count"], 1)
        self.assertEqual(result["status"], "available")

    @patch("mdv14.public_assets._fetch_stooq")
    def test_empty_or_unrecognized_csv_does_not_create_zero_values(self, fetch):
        fetch.return_value = "No data"
        result = fetch_public_asset_data(
            start_date="2026-11-20", end_date="2026-11-20", symbols=["^spx"]
        )
        self.assertEqual(result["status"], "unavailable")
        self.assertEqual(result["observations"], [])
        self.assertEqual(result["observation_count"], 0)

    def test_dashboard_escapes_provider_values_and_states_limits(self):
        html = render_public_asset_html({
            "status": "available", "observation_count": 1,
            "requests_succeeded": 1, "requests_failed": 0,
            "observations": [{"series": "<script>", "date": "2026-11-20",
                "value": 10, "unit": "points", "source": "Stooq"}],
            "errors": [],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("not live executable prices", html)
        self.assertIn("government-bond series", html)


if __name__ == "__main__":
    unittest.main()
