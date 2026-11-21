"""Tests for the MD V14 Daily Intelligence Brief generator."""
import unittest

from mdv14.daily_brief import build_daily_brief, normalize_signal


class DailyBriefTests(unittest.TestCase):
    def test_complete_evidence_ranks_before_higher_unverified_score(self):
        result = build_daily_brief([
            {"title": "Unverified", "score": 99, "summary": "No citation"},
            {"title": "Sourced", "source": "Example Desk", "url": "https://example.com/a", "score": 60},
        ], brief_date="2026-11-21")
        self.assertEqual(result["top_signals"][0]["title"], "Sourced")
        self.assertEqual(result["signals_needing_source_review"], 1)

    def test_score_is_clamped(self):
        item = normalize_signal({"title": "Topic", "score": 150})
        self.assertEqual(item["score"], 100.0)

    def test_empty_titles_are_excluded(self):
        result = build_daily_brief([{"source": "Desk", "url": "https://example.com"}])
        self.assertEqual(result["signals_included"], 0)

    def test_limit_must_be_positive(self):
        with self.assertRaises(ValueError):
            build_daily_brief([], limit=0)


if __name__ == "__main__":
    unittest.main()
