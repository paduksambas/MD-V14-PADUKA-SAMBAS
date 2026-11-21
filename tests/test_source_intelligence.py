"""Tests for transparent source intelligence and metadata checks."""
import unittest

from mdv14.source_intelligence import assess_source_intelligence


class SourceIntelligenceTests(unittest.TestCase):
    def test_empty_source_does_not_receive_reliability_verdict(self):
        result = assess_source_intelligence({})
        self.assertEqual(result["status"], "insufficient_source_metadata")
        self.assertIsNone(result["reputation_score"])
        self.assertEqual(result["reliability_verdict"], "not_assessed")
        self.assertFalse(result["checks"]["article_url_valid"])

    def test_https_and_provenance_fields_are_reported(self):
        result = assess_source_intelligence({
            "source": "Example Journal",
            "url": "https://news.example.org/story",
            "published_at": "2026-11-21T08:30:00Z",
            "author": "A. Reporter",
            "summary": "A source-provided summary.",
            "citations": ["https://example.org/document"],
            "is_primary_source": True,
            "source_profile": {
                "corrections_policy_url": "https://news.example.org/corrections",
                "ownership_url": "https://news.example.org/about",
                "editorial_policy_url": "https://news.example.org/editorial",
            },
        })
        self.assertEqual(result["source_domain"], "news.example.org")
        self.assertTrue(result["checks"]["https_transport"])
        self.assertTrue(result["checks"]["publication_time_present"])
        self.assertTrue(result["checks"]["author_attribution_present"])
        self.assertEqual(result["status"], "metadata_rich_human_review_required")
        self.assertIsNone(result["reputation_score"])
        self.assertEqual(result["reliability_verdict"], "not_assessed")

    def test_invalid_policy_urls_are_not_counted(self):
        result = assess_source_intelligence({
            "source": "Desk", "url": "http://example.org/story",
            "source_profile": {
                "corrections_policy_url": "javascript:alert(1)",
                "ownership_url": "not-a-url",
            },
        })
        self.assertFalse(result["checks"]["https_transport"])
        self.assertFalse(result["checks"]["corrections_policy_url_valid"])
        self.assertFalse(result["checks"]["ownership_information_url_valid"])
        self.assertIn("editorial_policy_url", result["unknown_profile_fields"])

    def test_invalid_timestamp_is_not_accepted(self):
        result = assess_source_intelligence({
            "source": "Desk", "url": "https://example.org/story",
            "published_at": "yesterday",
        })
        self.assertFalse(result["checks"]["publication_time_present"])


if __name__ == "__main__":
    unittest.main()
