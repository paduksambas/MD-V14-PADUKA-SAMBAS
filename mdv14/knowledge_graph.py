"""Deterministic multilingual entity extraction and reviewable knowledge graph."""
from __future__ import annotations

import re
from itertools import combinations
from typing import Any, Iterable

# Curated aliases only. These are discovery cues, not a complete named-entity model.
_ENTITY_ALIASES = {
    "Indonesia": ("Indonesia", "Republik Indonesia"),
    "United States": ("United States", "USA", "U.S.", "Amerika Serikat"),
    "China": ("China", "Tiongkok", "Republik Rakyat China"),
    "European Union": ("European Union", "EU", "Uni Eropa"),
    "Russia": ("Russia", "Rusia", "Federasi Rusia"),
    "Japan": ("Japan", "Jepang"),
    "South Korea": ("South Korea", "Korea Selatan"),
    "North Korea": ("North Korea", "Korea Utara"),
    "ASEAN": ("ASEAN", "Association of Southeast Asian Nations", "Perhimpunan Bangsa-Bangsa Asia Tenggara"),
    "United Nations": ("United Nations", "UN", "PBB", "Perserikatan Bangsa-Bangsa"),
    "NATO": ("NATO", "North Atlantic Treaty Organization"),
    "OpenAI": ("OpenAI",),
    "Microsoft": ("Microsoft",),
    "Google": ("Google", "Alphabet"),
    "NVIDIA": ("NVIDIA", "Nvidia"),
    "Apple": ("Apple Inc", "Apple"),
    "Tesla": ("Tesla", "Tesla Inc"),
    "World Bank": ("World Bank", "Bank Dunia"),
    "International Monetary Fund": ("International Monetary Fund", "IMF", "Dana Moneter Internasional"),
}
_ENTITY_TYPES = {
    "Indonesia": "country", "United States": "country", "China": "country",
    "Russia": "country", "Japan": "country", "South Korea": "country",
    "North Korea": "country", "European Union": "supranational",
    "ASEAN": "intergovernmental_organization", "United Nations": "intergovernmental_organization",
    "NATO": "intergovernmental_organization", "OpenAI": "company",
    "Microsoft": "company", "Google": "company", "NVIDIA": "company",
    "Apple": "company", "Tesla": "company", "World Bank": "organization",
    "International Monetary Fund": "organization",
}
_ALIAS_INDEX = {
    alias.casefold(): canonical
    for canonical, aliases in _ENTITY_ALIASES.items()
    for alias in aliases
}
_ALIAS_PATTERNS = [
    (alias, canonical, re.compile(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", re.IGNORECASE))
    for alias, canonical in sorted(_ALIAS_INDEX.items(), key=lambda item: (-len(item[0]), item[0]))
]


def _labels(value: Any) -> list[str]:
    values = value.split(",") if isinstance(value, str) else value
    if not isinstance(values, (list, tuple, set)):
        return []
    result, seen = [], set()
    for raw in values:
        label = str(raw or "").strip()
        key = label.casefold()
        if label and key not in seen:
            result.append(label)
            seen.add(key)
    return result


def _extract_text_entities(text: str) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {}
    for alias, canonical, pattern in _ALIAS_PATTERNS:
        if pattern.search(text):
            found.setdefault(canonical, []).append(alias)
    return found


def build_knowledge_graph(signals: Iterable[dict[str, Any]], *, limit: int = 100) -> dict[str, Any]:
    """Build a bounded graph from explicit metadata and a curated bilingual alias list."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    records = [item for item in signals if isinstance(item, dict)]
    nodes: dict[str, dict[str, Any]] = {}
    edges: dict[tuple[str, str, str], dict[str, Any]] = {}
    record_entities: dict[str, set[str]] = {}
    record_topics: dict[str, set[str]] = {}
    record_countries: dict[str, set[str]] = {}
    recognized_records = 0

    def add_node(node_id: str, label: str, kind: str, source: str) -> None:
        node = nodes.setdefault(node_id, {
            "id": node_id, "label": label, "type": kind,
            "evidence_sources": [],
        })
        if source and source not in node["evidence_sources"]:
            node["evidence_sources"].append(source)

    def add_edge(left: str, right: str, relation: str, record_id: str) -> None:
        if left == right:
            return
        a, b = sorted((left, right))
        key = (a, b, relation)
        edge = edges.setdefault(key, {
            "source": a, "target": b, "relation": relation,
            "supporting_record_ids": [],
        })
        if record_id and record_id not in edge["supporting_record_ids"]:
            edge["supporting_record_ids"].append(record_id)

    for index, signal in enumerate(records):
        record_id = str(signal.get("id") or f"record-{index + 1}")
        title = str(signal.get("title") or signal.get("topic") or "").strip()
        summary = str(signal.get("summary") or "").strip()
        text = title + " " + summary
        detected = _extract_text_entities(text)
        explicit = _labels(signal.get("entities"))
        explicit_country = _labels(signal.get("country")) + _labels(signal.get("countries"))
        for label in explicit:
            canonical = _ALIAS_INDEX.get(label.casefold(), label)
            detected.setdefault(canonical, []).append("explicit_metadata")
        entity_ids = set()
        for canonical, aliases in detected.items():
            entity_type = _ENTITY_TYPES.get(canonical, "explicit_entity")
            node_id = "entity:" + canonical.casefold()
            entity_ids.add(node_id)
            evidence = "explicit_metadata" if "explicit_metadata" in aliases else "title_or_summary_alias"
            add_node(node_id, canonical, entity_type, evidence)
        topic_ids = set()
        for topic in _labels(signal.get("topics")):
            node_id = "topic:" + topic.casefold()
            topic_ids.add(node_id)
            add_node(node_id, topic, "topic", "explicit_metadata")
        country_ids = set()
        for country in explicit_country:
            canonical = _ALIAS_INDEX.get(country.casefold(), country)
            node_id = "country:" + canonical.casefold()
            country_ids.add(node_id)
            add_node(node_id, canonical, "country", "explicit_metadata")
        event_id = "event:" + record_id
        if title:
            add_node(event_id, title, "event", "source_record")
            for entity_id in sorted(entity_ids):
                add_edge(event_id, entity_id, "mentions_entity", record_id)
            for topic_id in sorted(topic_ids):
                add_edge(event_id, topic_id, "tagged_with_topic", record_id)
            for country_id in sorted(country_ids):
                add_edge(event_id, country_id, "declared_country", record_id)
        record_entities[record_id] = entity_ids
        record_topics[record_id] = topic_ids
        record_countries[record_id] = country_ids
        if entity_ids:
            recognized_records += 1

    ids = list(record_entities)
    for left_id, right_id in combinations(ids, 2):
        for entity_id in sorted(record_entities[left_id] & record_entities[right_id]):
            add_edge("event:" + left_id, "event:" + right_id, "shared_entity", left_id)
            edges[tuple(sorted(("event:" + left_id, "event:" + right_id))) + ("shared_entity",)]["supporting_record_ids"].append(right_id)
        for topic_id in sorted(record_topics[left_id] & record_topics[right_id]):
            add_edge("event:" + left_id, "event:" + right_id, "shared_topic", left_id)
            key = tuple(sorted(("event:" + left_id, "event:" + right_id))) + ("shared_topic",)
            if right_id not in edges[key]["supporting_record_ids"]:
                edges[key]["supporting_record_ids"].append(right_id)
        for country_id in sorted(record_countries[left_id] & record_countries[right_id]):
            add_edge("event:" + left_id, "event:" + right_id, "same_declared_country", left_id)
            key = tuple(sorted(("event:" + left_id, "event:" + right_id))) + ("same_declared_country",)
            if right_id not in edges[key]["supporting_record_ids"]:
                edges[key]["supporting_record_ids"].append(right_id)

    node_rows = sorted(nodes.values(), key=lambda item: (item["type"], item["label"].casefold()))
    edge_rows = sorted(edges.values(), key=lambda item: (item["relation"], item["source"], item["target"]))
    total_nodes, total_edges = len(node_rows), len(edge_rows)
    return {
        "engine": "MD V14 Entity Recognition & Cross-Language Knowledge Graph",
        "build": "2.8",
        "records_processed": len(records),
        "records_with_recognized_entities": recognized_records,
        "nodes_total": total_nodes, "edges_total": total_edges,
        "nodes": node_rows[:limit], "edges": edge_rows[:limit],
        "entity_catalog_size": len(_ENTITY_ALIASES),
        "methodology": {
            "recognition": "Exact, case-insensitive matching against a curated alias list with selected English-Indonesian variants, plus explicitly supplied entity metadata.",
            "relations": "Event-to-entity/topic/country links and shared-entity/topic/country links between records.",
            "cross_language": "Aliases normalize selected names to one canonical node; article translation and automatic language detection are not performed.",
        },
        "limitations": [
            "This is deterministic alias matching, not a general-purpose named-entity recognition model.",
            "Ambiguous aliases such as Apple or Google may create false matches; all matches require analyst review.",
            "Only curated aliases and explicit entity/topic/country metadata are represented; unknown entities are not inferred.",
            "Graph edges describe shared labels or text matches, not causality, influence, alliance, or verified relationships.",
            "Source independence and factual accuracy are not established by graph connectivity.",
            "Node and edge lists are truncated to the requested limit; total counts describe the complete in-memory graph.",
        ],
        "notice": "Knowledge graph is an auditable discovery aid for human analysts, not an autonomous geopolitical conclusion.",
    }
