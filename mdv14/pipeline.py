"""Orchestrate MD V14 collection, corroboration and intelligence stages."""
from __future__ import annotations

from typing import Any, Iterable

from .cross_source import corroborate_sources, normalize_title
from .daily_brief import build_daily_brief
from .early_warning import classify_signal
from .fact_check import assess_evidence
from .rss_collector import collect_feeds
from .source_intelligence import assess_source_intelligence
from .trend_registry import TrendRegistry, signal_id


def run_pipeline(
    signals: Iterable[dict[str, Any]],
    brief_date: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    registry = TrendRegistry(signals)
    enriched = []
    for signal in registry.all():
        evidence = assess_evidence(signal)
        source_intelligence = assess_source_intelligence(signal)
        warning = classify_signal(signal)
        enriched.append({
            **signal, "evidence": evidence,
            "source_intelligence": source_intelligence, "warning": warning,
        })

    corroboration = corroborate_sources(enriched)
    corroboration_by_title = {
        item["normalized_title"]: item for item in corroboration
    }
    for signal in enriched:
        signal["corroboration"] = corroboration_by_title.get(
            normalize_title(signal["title"])
        )
        group = signal["corroboration"] or {}
        signal["source_intelligence"]["cross_source_context"] = {
            "mention_count": group.get("mention_count", 0),
            "distinct_source_count": group.get("distinct_source_count", 0),
            "corroboration_level": group.get("corroboration_level", "not_available"),
            "independence_verified": False,
            "notice": "Matching titles and distinct domains are discovery context only; independence and accuracy are not verified.",
        }

    brief = build_daily_brief(enriched, brief_date=brief_date, limit=limit)
    assessments = {item["id"]: item for item in enriched}
    for item in brief["top_signals"]:
        match = assessments.get(signal_id(item))
        if match:
            for field in ("evidence", "warning", "corroboration", "source_intelligence"):
                item[field] = match[field]

    source_status_counts = {}
    for item in enriched:
        status = item["source_intelligence"]["status"]
        source_status_counts[status] = source_status_counts.get(status, 0) + 1

    return {
        "pipeline": "MD V14",
        "stage": "Build 1.7 source intelligence and provenance assessment",
        "registry_size": len(registry),
        "daily_brief": brief,
        "warning_summary": {
            level: sum(1 for item in enriched if item["warning"]["level"] == level)
            for level in ("normal", "watch", "elevated", "critical")
        },
        "evidence_review_required": sum(
            1 for item in enriched if not item["evidence"]["evidence_complete"]
        ),
        "source_intelligence_summary": {
            "signals_assessed": len(enriched),
            "status_counts": dict(sorted(source_status_counts.items())),
            "reputation_verdicts_issued": 0,
            "notice": "Metadata assessment only. No automated source reliability or independence verdict is issued.",
        },
        "cross_source_analysis": corroboration,
        "signals": enriched,
        "limitations": [
            "RSS/Atom collection requires configured feeds and an internet connection.",
            "Cross-source grouping matches normalized titles only; it does not detect semantic duplicates.",
            "Distinct domains do not establish editorial independence or factual truth.",
            "Source intelligence checks supplied metadata and provenance fields only; it does not rate source reputation or verify claims.",
            "Evidence checks validate metadata and URL shape, not the truth of claims.",
            "Warning levels and trend scores are heuristics based on supplied inputs and require human review.",
            "Registry state is in-memory for each run; persist reports with the JSON storage helpers.",
        ],
    }


def collect_and_run(
    feeds: list[dict[str, str]],
    extra_signals: Iterable[dict[str, Any]] = (),
    brief_date: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Fetch configured feeds, combine optional local signals, then build the brief."""
    collection = collect_feeds(feeds)
    local_signals = list(extra_signals)
    combined = [*collection["signals"], *local_signals]
    report = run_pipeline(combined, brief_date=brief_date, limit=limit)
    report["collection"] = {
        key: value for key, value in collection.items() if key != "signals"
    }
    report["collection"]["extra_signals_added"] = len(local_signals)
    return report
