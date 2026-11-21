"""Tests for World Bank economic data integration."""
import json
import unittest
from unittest.mock import patch

from mdv14.economic_data import fetch_world_bank_indicators, _parse_countries, _parse_year_range


class EconomicDataTests(unittest.TestCase):
    @patch("mdv14.economic_data._fetch_json")
    def test_fetches_and_normalizes_official_observations(self, fetch):
        fetch.return_value = [
            {"total": 1},
            [{"country": {"value": "Indonesia"}, "indicator": {"value": "GDP growth"},
              "date": "2023", "value": 5.05}],
        ]
        result = fetch_world_bank_indicators("ID", start_year=2023, end_year=2023,
                                             indicators=["NY.GDP.MKTP.KD.ZG"])
        self.assertEqual(result["build"], "3.3")
        self.assertEqual(result["provider"], "World Bank Indicators API")
        self.assertEqual(result["observation_count"], 1)
        self.assertEqual(result["observations"][0]["country_code"], "ID")
        self.assertEqual(result["observations"][0]["value"], 5.05)
        self.assertEqual(result["requests_succeeded"], 1)
        self.assertIn("api.worldbank.org", result["observations"][0]["source_url"])

    @patch("mdv14.economic_data._fetch_json")
    def test_preserves_unavailable_indicator_without_zero_filling(self, fetch):
        fetch.side_effect = OSError("service unavailable")
        result = fetch_world_bank_indicators("ID", start_year=2022, end_year=2022,
                                             indicators=["FP.CPI.TOTL.ZG"])
        self.assertEqual(result["observation_count"], 0)
        self.assertEqual(result["requests_failed"], 1)
        self.assertEqual(result["observations"], [])
        self.assertEqual(result["errors"][0]["status"], "unavailable")

    def test_country_and_year_validation(self):
        self.assertEqual(_parse_countries("id,US,ID"), ["ID", "US"])
        with self.assertRaises(ValueError):
            _parse_countries("ID;US")
        with self.assertRaises(ValueError):
            _parse_countries("ZZZ")
        self.assertEqual(_parse_year_range(2020, 2021), (2020, 2021))
        with self.assertRaises(ValueError):
            _parse_year_range(2050, 2051)
        with self.assertRaises(ValueError):
            _parse_year_range(2025, 2020)

    def test_rejects_unknown_indicators_before_network_access(self):
        with self.assertRaises(ValueError):
            fetch_world_bank_indicators("ID", indicators=["UNKNOWN.CODE"])

    @patch("mdv14.economic_data._fetch_json")
    def test_handles_empty_or_missing_api_values(self, fetch):
        fetch.return_value = [{"total": 2}, [
            {"country": {"value": "Indonesia"}, "indicator": {"value": "GDP growth"},
             "date": "2023", "value": None},
            None,
        ]]
        result = fetch_world_bank_indicators("ID", start_year=2023, end_year=2023,
                                             indicators=["NY.GDP.MKTP.KD.ZG"])
        self.assertEqual(result["observation_count"], 0)


if __name__ == "__main__":
    unittest.main()
