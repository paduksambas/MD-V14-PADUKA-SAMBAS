"""Tests for explicit language coverage and bilingual research matching."""
import unittest

from mdv14.language_intelligence import analyze_language_coverage, normalize_language
from mdv14.research_orchestrator import build_research_report


class LanguageIntelligenceTests(unittest.TestCase):
    def test_language_aliases_and_regional_tags_normalize(self):
        self.assertEqual(normalize_language("EN-gb"), "English")
        self.assertEqual(normalize_language("id-ID"), "Indonesian")
        self.assertIsNone(normalize_language(""))

    def test_coverage_counts_declared_values_only(self):
        result = analyze_language_coverage([
            {"language": "en"}, {"language": "id-ID"}, {"title": "Bonjour"},
            {"language": "fr"},
        ])
        self.assertEqual(result["language_counts"], {"English": 1, "French": 1, "Indonesian": 1})
        self.assertEqual(result["records_with_unknown_language"], 1)

    def test_indonesian_question_matches_english_record(self):
        report = build_research_report("investasi energi", [
            {"title": "Energy investment expands", "language": "en", "source": "Desk"}
        ])
        self.assertEqual(report["records_with_keyword_match"], 1)
        self.assertIn("energy", report["research_candidates"][0]["matched_terms"])

    def test_english_question_matches_indonesian_record(self):
        report = build_research_report("climate security", [
            {"title": "Keamanan iklim menjadi perhatian", "language": "id", "source": "Desk"}
        ])
        self.assertEqual(report["records_with_keyword_match"], 1)

    def test_language_is_not_inferred_from_title_or_country(self):
        report = build_research_report("economy", [
            {"title": "Ekonomi Indonesia", "country": "Indonesia"}
        ])
        self.assertEqual(report["research_candidates"][0]["language"], "unknown")
        self.assertEqual(report["language_coverage"]["records_with_unknown_language"], 1)

    def test_unsupported_declared_language_is_counted_not_claimed_supported(self):
        report = build_research_report("climate", [
            {"title": "Cambio climático", "language": "es"}
        ])
        self.assertEqual(report["language_coverage"]["language_counts"], {"es": 1})
        self.assertEqual(report["records_with_keyword_match"], 0)


if __name__ == "__main__":
    unittest.main()
