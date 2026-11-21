"""Tests for Build 1.3 collection orchestration."""
import unittest
from unittest.mock import patch

from mdv14.pipeline import collect_and_run


class CollectionPipelineTests(unittest.TestCase):
    @patch("mdv14.pipeline.collect_feeds")
    def test_collect_and_run_includes_collected_signals(self, collector):
        collector.return_value = {
            "collector": "MD V14 RSS/Atom",
            "feeds_attempted": 1,
            "feeds_succeeded": 1,
            "feeds_failed": 0,
            "items_collected": 1,
            "feed_results": [],
            "signals": [{
                "title": "A current story",
                "source": "Example News",
                "url": "https://example.com/story",
                "summary": "Source summary",
                "feed_url": "https://example.com/rss",
                "collection_method": "rss_atom",
                "score": 0,
            }],
        }
        report = collect_and_run([{"id": "example", "name": "Example", "url": "https://example.com/rss", "country": "Indonesia", "language": "id", "topics": ["Technology"]}])
        self.assertEqual(report["registry_size"], 1)
        self.assertEqual(report["signals"][0]["source_id"], "example")
        self.assertEqual(report["signals"][0]["country"], "Indonesia")
        self.assertEqual(report["signals"][0]["language"], "id")
        self.assertEqual(report["signals"][0]["topics"], ["Technology"])
        self.assertEqual(report["collection"]["feeds_succeeded"], 1)
        self.assertEqual(report["daily_brief"]["signals_included"], 1)

    @patch("mdv14.pipeline.collect_feeds")
    def test_research_question_is_integrated_with_collected_records(self, collector):
        collector.return_value = {
            "collector": "MD V14 RSS/Atom",
            "feeds_attempted": 1,
            "feeds_succeeded": 1,
            "feeds_failed": 0,
            "items_collected": 1,
            "feed_results": [{"ok": True}],
            "signals": [{
                "title": "AI semiconductor investment expands",
                "source": "Example News",
                "url": "https://example.com/story",
                "summary": "New chip investment",
                "feed_url": "https://example.com/rss",
                "score": 0,
            }],
        }
        report = collect_and_run(
            [{"id": "example", "name": "Example", "url": "https://example.com/rss"}],
            research_question="AI semiconductor investment",
        )
        self.assertIn("research", report)
        self.assertEqual(report["research"]["records_reviewed"], 1)
        self.assertEqual(report["research"]["records_with_keyword_match"], 1)

    @patch("mdv14.pipeline.collect_feeds")
    def test_failed_feed_does_not_prevent_pipeline(self, collector):
        collector.return_value = {
            "collector": "MD V14 RSS/Atom", "feeds_attempted": 1,
            "feeds_succeeded": 0, "feeds_failed": 1, "items_collected": 0,
            "feed_results": [], "signals": [],
        }
        report = collect_and_run([{"id": "broken", "name": "Broken", "url": "https://broken.example/rss"}])
        self.assertEqual(report["registry_size"], 0)
        self.assertEqual(report["collection"]["feeds_failed"], 1)


if __name__ == "__main__":
    unittest.main()
