"""Auditable research orchestration summaries for configured multi-source runs."""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from .language_intelligence import analyze_language_coverage, normalize_language


_STOP = {"about", "from", "into", "that", "with", "yang", "dan", "untuk", "dari", "dengan", "pada", "dalam"}
_CONCEPTS = (
    ("economy", "economic", "ekonomi", "perekonomian"), ("energy", "energi"),
    ("climate", "iklim"), ("technology", "technological", "teknologi"),
    ("investment", "invest", "investasi", "penanaman"), ("security", "keamanan"),
    ("diplomacy", "diplomatic", "diplomasi"), ("election", "elections", "pemilu", "pemilihan"),
    ("health", "kesehatan"), ("trade", "trading", "perdagangan"),
    ("war", "conflict", "perang", "konflik"), ("supply", "pasokan"), ("chain", "rantai"),
)
_CANONICAL = {term: group[0] for group in _CONCEPTS for term in group}


def _terms(value: Any) -> set[str]:
    words = {word for word in re.findall(r"[\w-]{3,}", str(value or "").casefold())
             if word not in _STOP and not word.isdigit()}
    return {_CANONICAL.get(word, word) for word in words}


def build_research_report(
    question: str,
    signals: list[dict[str, Any]],
    collection: dict[str, Any] | None = None,
    *,
    limit: int = 10,
) -> dict[str, Any]:
    """Build a traceable research brief from collected records; never invent findings."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    prompt = str(question or "").strip()
    query_terms = _terms(prompt)
    ranked = []
    for signal in signals:
        if not isinstance(signal, dict):
            continue
        title = str(signal.get("title") or signal.get("topic") or "").strip()
        summary = str(signal.get("summary") or "").strip()
        content_terms = _terms(title + " " + summary)
        overlap = sorted(query_terms & content_terms)
        relevance = round(100 * len(overlap) / len(query_terms), 2) if query_terms else None
        evidence = signal.get("evidence")
        evidence = evidence if isinstance(evidence, dict) else {}
        warning = signal.get("warning")
        warning = warning if isinstance(warning, dict) else {}
        ranked.append({
            "title": title,
            "source": str(signal.get("source") or "unknown"),
            "url": str(signal.get("url") or ""),
            "country": str(signal.get("country") or "unknown"),
            "published_at": signal.get("published_at"),
            "language": normalize_language(signal.get("language")) or "unknown",
            "matched_terms": overlap,
            "relevance_score": relevance,
            "evidence_complete": bool(evidence.get("evidence_complete")),
            "warning_level": warning.get("level", "not_assessed"),
        })
    if query_terms:
        ranked.sort(key=lambda item: (-(item["relevance_score"] or 0), not item["evidence_complete"], item["title"].casefold()))
    else:
        ranked.sort(key=lambda item: (not item["evidence_complete"], item["title"].casefold()))

    collection = collection if isinstance(collection, dict) else {}
    feed_results = collection.get("feed_results", [])
    feed_results = [item for item in feed_results if isinstance(item, dict)] if isinstance(feed_results, list) else []
    successful = sum(1 for item in feed_results if item.get("ok"))
    failed = sum(1 for item in feed_results if not item.get("ok"))
    countries = Counter(item["country"] for item in ranked)
    complete = sum(1 for item in ranked if item["evidence_complete"])
    matched = sum(1 for item in ranked if item["relevance_score"] and item["relevance_score"] > 0)
    language_coverage = analyze_language_coverage(signals)
    gaps = []
    if not prompt:
        gaps.append("No research question supplied; records are listed without query relevance ranking.")
    if not ranked:
        gaps.append("No records were collected; verify feed configuration and connectivity.")
    if failed:
        gaps.append(f"{failed} configured feed(s) failed; inspect feed_results for the individual errors.")
    if ranked and complete < len(ranked):
        gaps.append("Some records lack complete source evidence metadata; review original URLs and attribution.")
    if len(countries) <= 1:
        gaps.append("Geographic diversity is limited or unknown in the supplied metadata.")
    if prompt and matched == 0 and ranked:
        gaps.append("No record matched the bilingual literal vocabulary; broaden terms or add relevant sources.")
    if language_coverage["records_with_unknown_language"]:
        gaps.append("Some records have no declared language; language coverage is incomplete.")

    return {
        "engine": "MD V14 Research Orchestrator",
        "build": "2.7",
        "research_question": prompt or None,
        "records_reviewed": len(ranked),
        "records_with_keyword_match": matched,
        "records_with_complete_evidence": complete,
        "language_coverage": language_coverage,
        "source_diversity": {
            "distinct_publishers": len({item["source"] for item in ranked if item["source"] != "unknown"}),
            "country_counts": dict(sorted(countries.items())),
        },
        "collection_health": {
            "feeds_attempted": collection.get("feeds_attempted", len(feed_results)),
            "feeds_succeeded": successful,
            "feeds_failed": failed,
            "items_collected": collection.get("items_collected", len(signals)),
        },
        "research_candidates": ranked[:limit],
        "research_gaps": gaps,
        "next_steps": [
            "Open and review original source links before citing claims.",
            "Compare publication timestamps and primary-source references across publishers.",
            "Treat shared headlines, domains, and metadata as discovery clues, not proof of independent corroboration.",
            "Add or enable relevant feeds when source or geographic coverage is insufficient.",
        ],
        "methodology": {
            "relevance": "Literal token overlap with a small deterministic English-Indonesian synonym map; not semantic search, translation, or language detection.",
            "evidence": "Uses the pipeline's evidence-completeness metadata; completeness does not verify truth.",
            "source_diversity": "Counts distinct supplied source labels and country metadata; does not verify ownership or editorial independence.",
        },
        "notice": "This report coordinates analysis of configured feeds and supplied records only. It does not autonomously discover new websites, bypass access controls, verify truth, or publish findings.",
    }
