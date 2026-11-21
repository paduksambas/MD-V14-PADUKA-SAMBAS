"""Tests for multilingual entity recognition and knowledge graph construction."""
import unittest

from mdv14.knowledge_graph import build_knowledge_graph


class KnowledgeGraphTests(unittest.TestCase):
    def test_indonesian_and_english_aliases_share_canonical_entity(self):
        result = build_knowledge_graph([
            {"id": "a", "title": "Indonesia and OpenAI announce a program"},
            {"id": "b", "title": "Program announced in Republik Indonesia by OpenAI"},
        ])
        entity_labels = {item["label"] for item in result["nodes"] if item["type"] in ("country", "company")}
        self.assertIn("Indonesia", entity_labels)
        self.assertIn("OpenAI", entity_labels)
        shared = [edge for edge in result["edges"] if edge["relation"] == "shared_entity"]
        self.assertTrue(shared)

    def test_explicit_metadata_entities_and_topics_are_linked(self):
        result = build_knowledge_graph([{
            "id": "sig-1", "title": "New development",
            "entities": ["ASEAN"], "topics": ["Trade"], "country": "Indonesia",
        }])
        relations = {edge["relation"] for edge in result["edges"]}
        self.assertIn("mentions_entity", relations)
        self.assertIn("tagged_with_topic", relations)
        self.assertIn("declared_country", relations)

    def test_shared_topic_creates_discovery_edge_not_causal_claim(self):
        result = build_knowledge_graph([
            {"id": "a", "title": "Event A", "topics": ["Energy"]},
            {"id": "b", "title": "Event B", "topics": ["Energy"]},
        ])
        edge = next(item for item in result["edges"] if item["relation"] == "shared_topic")
        self.assertEqual(edge["supporting_record_ids"], ["a", "b"])
        self.assertIn("not causality", " ".join(result["limitations"]))

    def test_unknown_entities_are_not_inferred(self):
        result = build_knowledge_graph([{"id": "a", "title": "A fictional entity Zorblax"}])
        self.assertEqual(result["records_with_recognized_entities"], 0)
        self.assertEqual([node for node in result["nodes"] if node["type"] != "event"], [])

    def test_unsafe_html_like_entity_is_data_not_markup(self):
        result = build_knowledge_graph([{
            "id": "x", "title": "Story", "entities": ["<script>alert(1)</script>"],
        }])
        self.assertTrue(any(node["label"] == "<script>alert(1)</script>" for node in result["nodes"]))

    def test_limit_validation_and_truncation(self):
        result = build_knowledge_graph([
            {"id": "a", "title": "Indonesia and ASEAN"},
            {"id": "b", "title": "China and ASEAN"},
        ], limit=1)
        self.assertEqual(len(result["nodes"]), 1)
        self.assertGreater(result["nodes_total"], 1)
        with self.assertRaises(ValueError):
            build_knowledge_graph([], limit=0)


if __name__ == "__main__":
    unittest.main()
