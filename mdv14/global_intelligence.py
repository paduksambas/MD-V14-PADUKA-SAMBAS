"""Explainable cross-country and cross-topic trend intelligence for MD V14."""
from __future__ import annotations

import re
from collections import defaultdict
from math import isfinite
from typing import Any, Iterable

from .advanced_scoring import assess_advanced_trend

_STOP_WORDS = {
    "about", "after", "against", "among", "because", "before", "being",
    "between", "could", "from", "have", "into", "more", "over", "said",
    "says", "that", "their", "there", "these", "they", "this", "those",
    "through", "under", "very", "were", "what", "when", "where", "which",
    "while", "with", "will", "would", "yang", "dan", "dari", "untuk",
    "pada", "dengan", "dalam", "karena", "oleh", "akan", "adalah", "yang",
}


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _labels(value: Any) -> list[str]:
    values = value.split(",") if isinstance(value, str) else value
    if not isinstance(values, (list, tuple, set)):
        return []
    result: list[str] = []
    seen: set[str] = set()
    for item in values:
        label = _text(item)
        key = label.casefold()
        if label and key not in seen:
            result.append(label)
            seen.add(key)
    return result


def _score(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not isfinite(number):
        return 0.0
    return max(0.0, min(100.0, number))


def _terms(title: str) -> set[str]:
    return {
        token for token in re.findall(r"[\w-]{4,}", title.casefold())
        if token not in _STOP_WORDS and not token.isdigit()
    }


def analyze_global_trends(
    signals: Iterable[dict[str, Any]], *, limit: int = 10, relation_limit: int = 25
) -> dict[str, Any]:
    """Summarize supplied signals by geography/topic and surface explainable links.

    This function does not fetch data, infer missing geography, establish causality,
    or verify editorial independence. Related-event links are discovery candidates
    based only on explicit shared entities/topics or repeated title terms.
    """
    if limit < 1 or relation_limit < 0:
        raise ValueError("limit must be positive and relation_limit cannot be negative")

    rows = [dict(item) for item in signals if isinstance(item, dict)]
    assessments: list[dict[str, Any]] = []
    country_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    topic_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for index, signal in enumerate(rows):
        title = _text(signal.get("title") or signal.get("topic"))
        if not title:
            continue
        score = _score(signal.get("score"))
        history = signal.get("score_history")
        if not isinstance(history, list):
            history = []
        trend = assess_advanced_trend(history, current_score=score)
        country = _text(signal.get("country")) or "unknown"
        topics = _labels(signal.get("topics")) or (
            [_text(signal.get("category"))] if _text(signal.get("category")) else ["Unclassified"]
        )
        item = {
            "signal_id": _text(signal.get("id")) or f"signal-{index + 1}",
            "title": title,
            "country": country,
            "region": _text(signal.get("region")) or "unknown",
            "topics": topics,
            "score": score,
            "momentum": trend["momentum"],
            "momentum_direction": trend["momentum_direction"],
            "attention_potential_index": trend["attention_potential_index"],
            "data_sufficiency": trend["data_sufficiency"],
        }
        assessments.append(item)
        country_groups[country].append(item)
        for topic in topics:
            topic_groups[topic].append(item)

    def summarize(groups: dict[str, list[dict[str, Any]]]) -> list[dict[str, Any]]:
        output = []
        for label, members in groups.items():
            scores = [item["score"] for item in members]
            momenta = [item["momentum"] for item in members if item["momentum"] is not None]
            output.append({
                "name": label,
                "signal_count": len(members),
                "average_score": round(sum(scores) / len(scores), 2),
                "maximum_score": max(scores),
                "signals_with_history": len(momenta),
                "average_momentum": round(sum(momenta) / len(momenta), 2) if momenta else None,
                "top_signals": [item["title"] for item in sorted(
                    members, key=lambda value: (-value["score"], value["title"].casefold())
                )[:3]],
            })
        return sorted(output, key=lambda item: (-item["signal_count"], -item["average_score"], item["name"].casefold()))

    # Pairwise links are deliberately labelled as discovery hints, never causal links.
    relations: list[dict[str, Any]] = []
    for left_index, left in enumerate(rows):
        left_title = _text(left.get("title") or left.get("topic"))
        if not left_title:
            continue
        left_entities = {x.casefold() for x in _labels(left.get("entities"))}
        left_topics = {x.casefold() for x in _labels(left.get("topics"))}
        left_terms = _terms(left_title)
        for right_index in range(left_index + 1, len(rows)):
            right = rows[right_index]
            right_title = _text(right.get("title") or right.get("topic"))
            if not right_title:
                continue
            shared_entities = sorted(left_entities & {x.casefold() for x in _labels(right.get("entities"))})
            shared_topics = sorted(left_topics & {x.casefold() for x in _labels(right.get("topics"))})
            shared_terms = sorted(left_terms & _terms(right_title))
            if shared_entities or shared_topics or len(shared_terms) >= 2:
                basis = []
                if shared_entities:
                    basis.append("shared_explicit_entities")
                if shared_topics:
                    basis.append("shared_explicit_topics")
                if len(shared_terms) >= 2:
                    basis.append("shared_title_terms")
                relations.append({
                    "left_title": left_title,
                    "right_title": right_title,
                    "left_country": _text(left.get("country")) or "unknown",
                    "right_country": _text(right.get("country")) or "unknown",
                    "shared_entities": shared_entities,
                    "shared_topics": shared_topics,
                    "shared_title_terms": shared_terms,
                    "relationship_basis": basis,
                    "cross_country": (_text(left.get("country")) or "unknown") != (_text(right.get("country")) or "unknown"),
                    "causality_verified": False,
                    "notice": "Discovery relationship only; shared metadata or wording does not establish causality or factual corroboration.",
                })
            if len(relations) >= relation_limit:
                break
        if len(relations) >= relation_limit:
            break

    rising = sorted(
        (item for item in assessments if item["momentum"] is not None and item["momentum"] > 0),
        key=lambda item: (-item["momentum"], -item["score"], item["title"].casefold()),
    )[:limit]
    return {
        "engine": "MD V14 Global Intelligence Engine",
        "build": "2.0",
        "signals_analyzed": len(assessments),
        "country_analysis": summarize(country_groups)[:limit],
        "topic_analysis": summarize(topic_groups)[:limit],
        "rising_signals": rising,
        "signal_momentum": assessments,
        "related_events": relations,
        "methodology": {
            "geography": "Uses explicit country and region metadata only; unknown values remain unknown.",
            "topics": "Uses supplied topics, falling back to category; no topic is inferred.",
            "momentum": "Uses each signal's optional score_history; missing history is reported as insufficient.",
            "event_relationships": "Requires a shared explicit entity/topic or at least two meaningful shared title terms.",
        },
        "limitations": [
            "This is analysis of supplied records only; no live global collection is performed here.",
            "Country and topic coverage depends on source metadata and is not globally representative by default.",
            "Related-event links are discovery candidates, not causal findings or verified corroboration.",
            "Momentum is unavailable without at least two valid historical score observations.",
            "Scores and group summaries are descriptive heuristics, not forecasts or probabilities.",
        ],
    }
