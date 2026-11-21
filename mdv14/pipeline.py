"""Orchestrate MD V14 collection, corroboration and intelligence stages."""
from __future__ import annotations

from typing import Any, Iterable

from .cross_source import corroborate_sources
from .daily_brief import build_daily_brief
from .early_warning import classify_signal
from .fact_check import assess_evidence
from .rss_collector import collect_feeds
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
        warning = classify_signal(signal)
        enriched.append({**signal, "evidence": evidence, "warning": warning})

    corroboration = corroborate_sources(enriched)
    corroboration_by_title = {
        item["normalized_title"]: item for item in corroboration
    }
    for signal in enriched:
        from .cross_source import normalize_title
        signal["corroboration"] = corroboration_by_title.get(
            normalize_title(signal["title"])
        )

    brief = build_daily_brief(enriched, brief_date=brief_date, limit=limit)
    assessments = {item["id"]: item for item in enriched}
    for item in brief["top_signals"]:
        match = assessments.get(signal_id(item))
        if match:
            item["evidence"] = match["evidence"]
            item["warning"] = match["warning"]
            item["corroboration"] = match["corroboration"]

    return {
        "pipeline": "MD V14",
        "stage": "Build 1.3 live RSS/Atom collection and cross-source analysis",
        "registry_size": len(registry),
        "daily_brief": brief,
        "warning_summary": {
            level: sum(1 for item in enriched if item["warning"]["level"] == level)
            for level in ("normal", "watch", "elevated", "critical")
        },
        "evidence_review_required": sum(
            1 for item in enriched if not item["evidence"]["evidence_complete"]
        ),
        "cross_source_analysis": corroboration,
        "signals": enriched,
        "limitations": [
            "RSS/Atom collection requires configured feeds and an internet connection.",
            "Cross-source grouping matches normalized titles only; it does not detect semantic duplicates.",
            "Distinct domains do not establish editorial independence or factual truth.",
            "Evidence checks validate metadata and URL shape, not the truth of claims.",
            "Warning levels are heuristics based on supplied scores and require human review.",
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
    combined = [*collection["signals"], *list(extra_signals)]
    report = run_pipeline(combined, brief_date=brief_date, limit=limit)
    report["collection"] = {
        key: value for key, value in collection.items() if key != "signals"
    }
    report["collection"]["extra_signals_added"] = len(list(extra_signals)) if not isinstance(extra_signals, list) else len(extra_signals)
    return report
