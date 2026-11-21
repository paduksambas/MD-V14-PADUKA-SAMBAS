import unittest
from mdv14.regional_intelligence import (
    build_regional_intelligence, fetch_bps_region_catalog, render_regional_intelligence_html,
)


class RegionalIntelligenceTests(unittest.TestCase):
    def test_region_rankings_compare_same_indicator_period_and_level(self):
        data = {"observations": [
            {"region_code": "11", "region_name": "Aceh", "level": "province", "indicator_code": "PDRB", "period": "2023", "value": 4.1, "unit": "%"},
            {"region_code": "12", "region_name": "North Sumatra", "level": "province", "indicator_code": "PDRB", "period": "2023", "value": 5.2, "unit": "%"},
            {"region_code": "1101", "region_name": "Simeulue", "level": "regency_city", "province_code": "11", "indicator_code": "PDRB", "period": "2023", "value": 3.0, "unit": "%"},
        ]}
        result = build_regional_intelligence(data)
        self.assertEqual(result["status"], "available")
        self.assertEqual(len(result["rankings"]), 3)
        provincial = [r for r in result["rankings"] if r["level"] == "province"]
        self.assertEqual([r["region_name"] for r in provincial], ["North Sumatra", "Aceh"])
        self.assertEqual(len(result["disparities"]), 2)

    def test_profiles_compute_history_and_change(self):
        data = {"observations": [
            {"region_code": "32", "region_name": "West Java", "level": "province", "indicator_code": "PDRB", "period": "2022", "value": 5.0},
            {"region_code": "32", "region_name": "West Java", "level": "province", "indicator_code": "PDRB", "period": "2023", "value": 5.2},
        ]}
        result = build_regional_intelligence(data)
        self.assertEqual(result["region_profiles"][0]["change"], 0.2)
        self.assertEqual(result["region_profiles"][0]["direction"], "rising")

    def test_invalid_and_nonfinite_rows_are_rejected(self):
        result = build_regional_intelligence({"observations": [
            {"region_code": "", "region_name": "Bad", "level": "province", "indicator_code": "X", "period": "2023", "value": 1},
            {"region_code": "1", "region_name": "Bad", "level": "province", "indicator_code": "X", "period": "2023", "value": "NaN"},
            "bad",
        ]})
        self.assertEqual(result["observation_count"], 0)
        self.assertEqual(result["rejected_rows"], 3)

    def test_no_key_is_explicit_not_configured(self):
        result = fetch_bps_region_catalog(None)
        self.assertEqual(result["status"], "not_configured")
        self.assertEqual(result["requests_succeeded"], 0)

    def test_catalog_parser_accepts_bps_list_shape(self):
        from mdv14.regional_intelligence import _domain_rows
        rows = _domain_rows([{"status": "ok"}, [{"domain_id": "32", "domain_name": "Jawa Barat"}]])
        self.assertEqual(rows[0]["domain_id"], "32")

    def test_dashboard_escapes_untrusted_region_names(self):
        html = render_regional_intelligence_html({
            "observation_count": 1, "regions_with_indicator_data": {"province": 1, "regency_city": 0},
            "bps_region_catalog": {"status": "not_configured", "region_count": 0},
            "rankings": [{"level": "province", "indicator_name": "<script>", "period": "2023",
                "rank": 1, "regions_compared": 1, "region_name": "<img>", "value": 1, "unit": "%"}],
            "disparities": [],
        })
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
        self.assertIn("&lt;img&gt;", html)


if __name__ == "__main__":
    unittest.main()
