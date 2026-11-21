import unittest
from mdv14.indonesia_intelligence import (
    build_indonesia_economic_intelligence, render_indonesia_economic_html,
)


class IndonesiaEconomicIntelligenceTests(unittest.TestCase):
    def test_summarizes_indonesia_indicators_and_excludes_other_countries(self):
        economic = {"observations": [
            {"country_code": "ID", "indicator_code": "NY.GDP.MKTP.KD.ZG", "year": "2022", "value": 5.0, "unit": "%"},
            {"country_code": "ID", "indicator_code": "NY.GDP.MKTP.KD.ZG", "year": "2023", "value": 5.1, "unit": "%"},
            {"country_code": "US", "indicator_code": "NY.GDP.MKTP.KD.ZG", "year": "2023", "value": 2.5, "unit": "%"},
        ]}
        result = build_indonesia_economic_intelligence(economic, {})
        self.assertEqual(result["build"], "3.8")
        self.assertEqual(result["indicator_count"], 1)
        self.assertEqual(result["indicators"][0]["latest_value"], 5.1)
        self.assertEqual(result["indicators"][0]["direction"], "rising")
        self.assertEqual(result["coverage"]["world_bank_indonesia_observations"], 2)

    def test_builds_qualitative_commodity_channels_from_available_benchmarks(self):
        commodities = {"observations": [
            {"series_id": "WB:GOLD", "series": "Gold", "date": "2026-08-01", "value": 3300, "unit": "USD/oz"},
            {"series_id": "WB:GOLD", "series": "Gold", "date": "2026-09-01", "value": 3400, "unit": "USD/oz"},
            {"series_id": "WB:PALM_OIL", "series": "Palm oil", "date": "2026-09-01", "value": 950, "unit": "USD/t"},
        ]}
        result = build_indonesia_economic_intelligence({}, commodities)
        self.assertEqual(result["commodity_channel_count"], 2)
        gold = next(item for item in result["commodity_channels"] if item["category"] == "precious_metals")
        self.assertEqual(gold["benchmark_series"][0]["value"], 3400)
        self.assertIn("not a measured Indonesia exposure", gold["interpretation"])

    def test_missing_data_is_not_filled_and_empty_inputs_are_clear(self):
        result = build_indonesia_economic_intelligence({}, {})
        self.assertEqual(result["status"], "no_data")
        self.assertEqual(result["indicator_count"], 0)
        self.assertEqual(result["commodity_channel_count"], 0)

    def test_invalid_indicator_rows_are_skipped(self):
        result = build_indonesia_economic_intelligence({"observations": [
            {"country_code": "ID", "indicator_code": "UNKNOWN", "year": "2024", "value": 2},
            {"country_code": "ID", "indicator_code": "NY.GDP.MKTP.KD.ZG", "year": "bad", "value": "x"},
        ]}, {})
        self.assertEqual(result["indicator_count"], 0)

    def test_dashboard_escapes_untrusted_labels(self):
        html = render_indonesia_economic_html({
            "indicator_count": 1, "commodity_channel_count": 0,
            "coverage": {"recognized_indicator_observations": 1},
            "indicators": [{"indicator": "<script>", "domain": "macro", "first_year": 2020,
                "latest_year": 2021, "first_value": 1, "latest_value": 2,
                "change": 1, "unit": "%", "direction": "rising"}],
            "commodity_channels": [],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("qualitative", html.lower())


if __name__ == "__main__":
    unittest.main()
