"""Tests for Build 1.8 global data integration."""
import unittest
from mdv14.data_integration import build_data_coverage, normalize_global_signal, validate_source_catalog

class DataIntegrationTests(unittest.TestCase):
    def test_catalog_normalizes_and_skips_disabled(self):
        result = validate_source_catalog([
            {"id":"bbc-world","name":"BBC World","url":"https://feeds.example.org/world.xml",
             "country":"United Kingdom","language":"en","topics":["World","Politics"]},
            {"id":"off","name":"Disabled","url":"https://example.org/rss","enabled":False},
        ])
        self.assertEqual(result["sources_enabled"], 1)
        self.assertEqual(result["sources"][0]["publisher"], "BBC World")
        self.assertEqual(result["sources"][0]["topics"], ["World","Politics"])
        self.assertEqual(result["configuration_errors"], [])

    def test_catalog_rejects_http_credentials_and_duplicate_ids(self):
        result = validate_source_catalog([
            {"id":"a","name":"A","url":"http://example.org/rss"},
            {"id":"b","name":"B","url":"https://user:pass@example.org/rss"},
            {"id":"x","name":"X","url":"https://example.org/x"},
            {"id":"X","name":"X2","url":"https://example.org/y"},
        ])
        self.assertEqual(result["sources_enabled"], 1)
        self.assertEqual(len(result["configuration_errors"]), 3)

    def test_normalization_preserves_provenance_and_unknowns(self):
        item = normalize_global_signal(
            {"title":"Story","published_at":"2026-11-21T08:00:00+07:00","collection_method":"rss_atom"},
            {"id":"src-1","country":"Indonesia","language":"id","topics":["Economy","Markets"]},
            collected_at="2026-11-21T01:00:00Z")
        self.assertEqual(item["data_schema_version"], "1.0")
        self.assertEqual(item["source_id"], "src-1")
        self.assertEqual(item["country"], "Indonesia")
        self.assertEqual(item["published_at"], "2026-11-21T01:00:00Z")
        self.assertIsNone(item["region"])
        self.assertEqual(item["collection_method"], "rss_atom")

    def test_rfc822_publication_timestamp_is_standardized(self):
        item = normalize_global_signal({"published_at": "Sat, 21 Nov 2026 08:00:00 GMT"})
        self.assertEqual(item["published_at"], "2026-11-21T08:00:00Z")

    def test_coverage_counts_unknown_without_inference(self):
        result = build_data_coverage([
            {"country":"Indonesia","language":"id","source_type":"news"},
            {"country":None,"language":"en"}])
        self.assertEqual(result["records_total"], 2)
        self.assertEqual(result["dimensions"]["country"]["known_records"], 1)
        self.assertEqual(result["dimensions"]["country"]["unknown_records"], 1)
        self.assertEqual(result["dimensions"]["source_type"]["unknown_records"], 1)

if __name__ == "__main__":
    unittest.main()
