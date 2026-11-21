"""Tests for cautious cross-source corroboration."""
import unittest

from mdv14.cross_source import corroborate_sources, normalize_title


class CrossSourceTests(unittest.TestCase):
    def test_normalize_title(self):
        self.assertEqual(normalize_title("Big-News: AI 2026!"), "big news ai 2026")

    def test_count_distinct_domains(self):
        results = corroborate_sources([
            {"title": "Major story!", "url": "https://one.example/a"},
            {"title": "Major story", "url": "https://two.example/b"},
            {"title": "Major story", "url": "https://one.example/c"},
        ])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["mention_count"], 3)
        self.assertEqual(results[0]["distinct_source_count"], 2)
        self.assertEqual(results[0]["corroboration_level"], "multiple_domains")
        self.assertFalse(results[0]["truth_verified"])

    def test_no_url_not_counted_as_domain(self):
        result = corroborate_sources([{"title": "Only claim"}])[0]
        self.assertEqual(result["distinct_source_count"], 0)


if __name__ == "__main__":
    unittest.main()
