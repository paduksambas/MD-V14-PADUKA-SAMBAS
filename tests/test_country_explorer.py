"""Tests for Build 3.1 country explorer."""
import unittest

from mdv14.country_explorer import build_country_explorer


class CountryExplorerTests(unittest.TestCase):
    def test_maps_only_explicit_known_countries_and_keeps_traceability(self):
        report = {
            "signals": [
                {"id": "s1", "title": "Energy policy", "country": "Indonesia", "source": "ANTARA",
                 "url": "https://example.org/1", "score": 80, "warning": {"level": "elevated"}},
                {"id": "s2", "title": "Trade update", "country": "United States", "source": "BBC",
                 "score": 40, "warning": {"level": "watch"}},
                {"id": "s3", "title": "Unknown event", "country": "Atlantis", "score": 99},
                {"id": "s4", "title": "No country", "score": 90},
            ],
            "strategic_decision": {"review_queue": [
                {"signal_id": "s1", "priority_band": "high"},
                {"signal_id": "s2", "priority_band": "medium"},
            ]},
        }
        result = build_country_explorer(report)
        self.assertEqual(result["build"], "3.1")
        self.assertEqual(result["countries_total"], 3)
        self.assertEqual(result["countries_mapped"], 2)
        self.assertEqual(result["countries_unmapped"], 1)
        indonesia = next(item for item in result["mapped_countries"] if item["name"] == "Indonesia")
        self.assertEqual(indonesia["review_priority_counts"]["high"], 1)
        self.assertEqual(indonesia["records"][0]["signal_id"], "s1")
        self.assertIn("not country risk ratings", indonesia["notice"])

    def test_country_aliases_use_curated_canonical_mapping(self):
        result = build_country_explorer({"signals": [
            {"id": "a", "title": "One", "country": "US"},
            {"id": "b", "title": "Two", "country": "United States"},
        ]})
        self.assertEqual(result["countries_total"], 1)
        self.assertEqual(result["mapped_countries"][0]["signal_count"], 2)

    def test_empty_and_invalid_limit(self):
        self.assertEqual(build_country_explorer({"signals": []})["countries_total"], 0)
        with self.assertRaises(ValueError):
            build_country_explorer({}, limit=0)


if __name__ == "__main__":
    unittest.main()
