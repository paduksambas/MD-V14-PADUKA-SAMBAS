import unittest
from mdv14.regional_intelligence import (
    build_regional_intelligence, fetch_bps_region_catalog, fetch_bps_regional_tables, render_regional_intelligence_html,
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
        self.assertAlmostEqual(result["region_profiles"][0]["change"], 0.2)
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

    def test_bps_catalog_fetch_normalizes_domains_without_exposing_key(self):
        from unittest.mock import patch
        payloads = [
            [{"status": "ok"}, [{"domain_id": "32", "domain_name": "Jawa Barat"}]],
            [{"status": "ok"}, [{"domain_id": "3201", "domain_name": "Kabupaten Bogor", "parent_id": "32"}]],
        ]
        with patch("mdv14.regional_intelligence._request_json", side_effect=payloads):
            result = fetch_bps_region_catalog("secret-token")
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["region_count"], 2)
        self.assertEqual({item["level"] for item in result["regions"]}, {"province", "regency_city"})
        self.assertNotIn("secret-token", str(result))

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

    def test_bps_dynamic_table_fetch_extracts_single_cell(self):
        from unittest.mock import patch
        config = {"tables": [{
            "domain_id": "32", "region_name": "Jawa Barat", "level": "province",
            "indicator_code": "PDRB_GROWTH", "indicator_name": "Pertumbuhan PDRB",
            "variable_id": "145", "period_id": "100", "period": "2023", "unit": "%"
        }]}
        with patch("mdv14.regional_intelligence._request_json",
                   return_value={"status": "OK", "data": [{"datacontent": {"32": "5.31"}}]}):
            result = fetch_bps_regional_tables("private-key", config)
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["observations"][0]["value"], 5.31)
        self.assertNotIn("private-key", str(result))

    def test_bps_dynamic_table_rejects_ambiguous_cells(self):
        from unittest.mock import patch
        config = {"tables": [{
            "domain_id": "32", "region_name": "Jawa Barat", "level": "province",
            "indicator_code": "X", "variable_id": "145", "period_id": "100", "period": "2023"
        }]}
        with patch("mdv14.regional_intelligence._request_json",
                   return_value={"data": [{"datacontent": {"32": "5", "33": "6"}}]}):
            result = fetch_bps_regional_tables("private-key", config)
        self.assertEqual(result["requests_failed"], 1)
        self.assertEqual(result["observations"], [])

    def test_bps_dynamic_table_request_limit_prevents_network_calls(self):
        from unittest.mock import patch
        config = {"tables": [{}] * 101}
        with patch("mdv14.regional_intelligence._request_json") as request:
            result = fetch_bps_regional_tables("private-key", config)
        request.assert_not_called()
        self.assertEqual(result["status"], "request_limit_exceeded")

    def test_bps_dynamic_table_requires_key(self):
        result = fetch_bps_regional_tables(None, {"tables": []})
        self.assertEqual(result["status"], "not_configured")
        self.assertEqual(result["request_count"], 0)


if __name__ == "__main__":
    unittest.main()
