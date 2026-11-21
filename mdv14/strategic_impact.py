"""Explainable strategic-impact and geopolitical context indicators.

Analyses supplied records and explicit metadata only. Keyword matches are review
cues, not causal inference, geopolitical forecasts, or verified risk assessments.
"""
from __future__ import annotations

import re
from collections import Counter
from itertools import combinations
from typing import Any, Iterable

_DIMENSIONS = {
    "economic": {"trade", "tariff", "sanction", "investment", "market", "supply", "export", "import", "inflation", "ekonomi", "perdagangan", "tarif", "investasi", "pasokan", "ekspor", "impor"},
    "security": {"military", "defense", "war", "conflict", "weapon", "cyber", "security", "serangan", "militer", "pertahanan", "perang", "konflik", "keamanan", "siber"},
    "diplomatic": {"diplomacy", "treaty", "summit", "embassy", "negotiation", "alliance", "diplomasi", "perjanjian", "perundingan", "aliansi", "ktt"},
    "societal": {"migration", "election", "protest", "public", "health", "population", "migrasi", "pemilu", "protes", "masyarakat", "kesehatan", "penduduk"},
    "technology": {"semiconductor", "chip", "artificial", "intelligence", "technology", "digital", "quantum", "teknologi", "digitalisasi", "semikonduktor"},
    "environmental": {"climate", "flood", "drought", "energy", "emission", "biodiversity", "iklim", "banjir", "kekeringan", "energi", "emisi", "lingkungan"},
}
_TOKEN = re.compile(r"[a-zA-Z0-9À-ÿ]+")


def _labels(value: Any) -> list[str]:
    if isinstance(value, str):
        value = value.split(",")
    if not isinstance(value, (list, tuple, set)):
        return []
    output, seen = [], set()
    for item in value:
        label = str(item or "").strip()
        if label and label.casefold() not in seen:
            output.append(label)
            seen.add(label.casefold())
    return output


def _score(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number or number in (float("inf"), float("-inf")):
        return 0.0
    return max(0.0, min(100.0, number))


def _assess(signal: dict[str, Any]) -> dict[str, Any]:
    title = str(signal.get("title") or signal.get("topic") or "").strip()
    summary = str(signal.get("summary") or "").strip()
    tokens = {token.casefold() for token in _TOKEN.findall(title + " " + summary)}
    dimensions = sorted(name for name, words in _DIMENSIONS.items() if tokens & words)
    countries = _labels(signal.get("countries")) or _labels(signal.get("country"))
    entities = _labels(signal.get("entities"))
    topics = _labels(signal.get("topics"))
    score = _score(signal.get("score"))
    evidence = signal.get("evidence")
    evidence = evidence if isinstance(evidence, dict) else {}
    evidence_complete = bool(evidence.get("evidence_complete"))
    if evidence_complete and signal.get("url"):
        confidence = "metadata_supported"
    elif signal.get("url") or signal.get("source"):
        confidence = "limited_metadata"
    else:
        confidence = "insufficient_metadata"
    level = "high_attention" if score >= 70 else "moderate_attention" if score >= 40 else "monitor"
    return {
        "signal_id": str(signal.get("id") or ""),
        "title": title,
        "impact_dimensions": dimensions,
        "countries_explicitly_named": countries,
        "entities_explicitly_named": entities,
        "topics_supplied": topics,
        "attention_level": level,
        "input_score": score,
        "metadata_confidence": confidence,
        "evidence_complete": evidence_complete,
        "review_required": True,
        "review_questions": [
            "Verify the event and its date against primary sources.",
            "Identify affected actors and distinguish confirmed impacts from scenarios.",
            "Check whether the supplied country and entity labels are accurate.",
        ],
        "notice": "Attention level reflects the supplied signal score only; it is not a measured impact probability or severity.",
    }


def analyze_strategic_impact(signals: Iterable[dict[str, Any]], *, limit: int = 20) -> dict[str, Any]:
    """Create transparent strategic-impact cues and cross-border review candidates."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    rows = [item for item in signals if isinstance(item, dict)]
    assessments = [_assess(item) for item in rows if str(item.get("title") or item.get("topic") or "").strip()]
    dimension_counts = Counter(d for item in assessments for d in item["impact_dimensions"])
    country_pairs = []
    for left, right in combinations(assessments, 2):
        shared_entities = sorted(set(x.casefold() for x in left["entities_explicitly_named"]) &
                                 set(x.casefold() for x in right["entities_explicitly_named"]))
        shared_topics = sorted(set(x.casefold() for x in left["topics_supplied"]) &
                               set(x.casefold() for x in right["topics_supplied"]))
        cross_country = bool(left["countries_explicitly_named"] and right["countries_explicitly_named"]
                             and set(x.casefold() for x in left["countries_explicitly_named"]) !=
                             set(x.casefold() for x in right["countries_explicitly_named"]))
        if cross_country and (shared_entities or shared_topics):
            country_pairs.append({
                "signal_titles": [left["title"], right["title"]],
                "countries": [left["countries_explicitly_named"], right["countries_explicitly_named"]],
                "shared_entities": shared_entities,
                "shared_topics": shared_topics,
                "relationship_type": "cross_border_review_candidate",
                "causality_verified": False,
                "independence_verified": False,
            })
    assessments.sort(key=lambda item: ({"high_attention": 0, "moderate_attention": 1, "monitor": 2}[item["attention_level"]],
                                       item["title"].casefold()))
    return {
        "engine": "MD V14 Strategic Impact & Geopolitical Analysis",
        "build": "2.4",
        "signals_assessed": len(assessments),
        "impact_dimension_counts": dict(sorted(dimension_counts.items())),
        "attention_level_counts": {key: sum(1 for item in assessments if item["attention_level"] == key)
                                   for key in ("high_attention", "moderate_attention", "monitor")},
        "cross_border_review_candidates": country_pairs[:limit],
        "assessments": assessments[:limit],
        "methodology": {
            "dimensions": "Deterministic keyword matches in supplied titles and summaries; misses and false matches are possible.",
            "attention": "Uses supplied numeric score bands only: 0-39 monitor, 40-69 moderate_attention, 70-100 high_attention.",
            "geopolitical_context": "Requires explicit country labels plus a shared supplied entity or topic; it does not infer alliances, conflict, influence, or causality.",
            "confidence": "Describes metadata completeness only, not truth or source credibility.",
        },
        "limitations": [
            "No live geopolitical intelligence collection or external verification is performed.",
            "Impact dimensions are discovery cues, not a complete assessment of real-world consequences.",
            "Country and entity names are used only when explicitly supplied; missing geography is not inferred.",
            "Cross-border candidates require human review and do not establish a relationship or causal link.",
            "Attention levels are based on supplied scores and are not risk probabilities, forecasts, or severity ratings.",
        ],
        "notice": "Decision-support triage only. Human analysts must verify claims, context, affected stakeholders, and potential consequences before acting.",
    }
