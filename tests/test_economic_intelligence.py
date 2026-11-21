"""Tests for Build 3.2 global economic intelligence."""
import unittest

from mdv14.economic_intelligence import analyze_economic_intelligence, render_economic_intelligence_html


class EconomicIntelligenceTests(unittest.TestCase):
    def test_classifies_multiple_sectors_and_preserves_traceability(self):
        result = analyze_economic_intelligence([{
            "id": "sig-1", "title": "Indonesia nickel exports and EV battery supply chain",
            "summary": "Mining and trade policy", "country": "Indonesia",
            "source": "Example Desk", "url": "https://example.org/story", "score": 82,
            "warning": {"level": "elevated"}, "evidence": {"evidence_complete": True},
        }])
        self.assertEqual(result["build"], "3.2")
        self.assertGreaterEqual(result["sector_count"], 2)
        self.assertIn("commodities_mining", result["priority_review_queue"][0]["sectors"])
        self.assertEqual(result["priority_review_queue"][0]["signal_id"], "sig-1")
        self.assertEqual(result["country_mentions"][0]["country"], "Indonesia")

    def test_indonesian_keywords_are_supported(self):
        result = analyze_economic_intelligence([{
            "id": "id-1", "title": "Harga minyak dan inflasi meningkat",
            "country": "Indonesia", "score": 50,
        }])
        sectors = {item["sector"] for item in result["sector_summaries"]}
        self.assertIn("energy", sectors)
        self.assertIn("finance_macro", sectors)

    def test_no_match_is_not_claimed_as_no_economic_effect(self):
        result = analyze_economic_intelligence([{"title": "A general political update"}])
        self.assertEqual(result["signals_assessed"], 0)
        self.assertEqual(result["coverage"]["records_without_sector_match"], 1)
        self.assertIn("Not automatically irrelevant", render_economic_intelligence_html(result))

    def test_escapes_untrusted_content_and_keeps_safe_source_link(self):
        result = analyze_economic_intelligence([{
            "id": "x", "title": "<script>oil</script>", "source": "Desk",
            "url": "https://example.org/x", "score": 75,
        }])
        html = render_economic_intelligence_html(result)
        self.assertNotIn("<script>oil</script>", html)
        self.assertIn("&lt;script&gt;", html)
        self.assertIn('href="https://example.org/x"', html)

    def test_invalid_limit_and_empty_input(self):
        self.assertEqual(analyze_economic_intelligence([])["signals_assessed"], 0)
        with self.assertRaises(ValueError):
            analyze_economic_intelligence([], limit=0)


if __name__ == "__main__":
    unittest.main()
