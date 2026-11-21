"""Orchestrate MD V14 collection, standardization and intelligence stages."""
from __future__ import annotations
from typing import Any, Iterable
from .cross_source import corroborate_sources, normalize_title
from .daily_brief import build_daily_brief
from .data_integration import build_data_coverage, normalize_global_signal, validate_source_catalog
from .early_warning import classify_signal
from .fact_check import assess_evidence
from .global_intelligence import analyze_global_trends
from .predictive_intelligence import assess_predictive_outlook
from .rss_collector import collect_feeds
from .source_intelligence import assess_source_intelligence
from .trend_registry import TrendRegistry, signal_id

def run_pipeline(signals: Iterable[dict[str, Any]], brief_date: str | None = None,
                 limit: int = 10) -> dict[str, Any]:
    standardized = [normalize_global_signal(item) for item in signals]
    registry = TrendRegistry(standardized)
    enriched = []
    for signal in registry.all():
        enriched.append({
            **signal, "evidence": assess_evidence(signal),
            "source_intelligence": assess_source_intelligence(signal),
            "warning": classify_signal(signal),
            "predictive_outlook": assess_predictive_outlook(signal),
        })
    corroboration = corroborate_sources(enriched)
    by_title = {item["normalized_title"]: item for item in corroboration}
    for signal in enriched:
        signal["corroboration"] = by_title.get(normalize_title(signal["title"]))
        group = signal["corroboration"] or {}
        signal["source_intelligence"]["cross_source_context"] = {
            "mention_count": group.get("mention_count", 0),
            "distinct_source_count": group.get("distinct_source_count", 0),
            "corroboration_level": group.get("corroboration_level", "not_available"),
            "independence_verified": False,
            "notice": "Matching titles and distinct domains are discovery context only; independence and accuracy are not verified.",
        }
    brief = build_daily_brief(enriched, brief_date=brief_date, limit=limit)
    global_intelligence = analyze_global_trends(enriched, limit=limit)
    assessments = {item["id"]: item for item in enriched}
    for item in brief["top_signals"]:
        match = assessments.get(signal_id(item))
        if match:
            for field in ("evidence", "warning", "predictive_outlook", "corroboration", "source_intelligence"):
                item[field] = match[field]
    statuses = {}
    for item in enriched:
        status = item["source_intelligence"]["status"]
        statuses[status] = statuses.get(status, 0) + 1
    return {
        "pipeline": "MD V14", "stage": "Build 2.2 predictive intelligence and early warning",
        "data_schema_version": "1.0", "registry_size": len(registry),
        "data_coverage": build_data_coverage(enriched), "daily_brief": brief,
        "global_intelligence": global_intelligence,
        "warning_summary": {level: sum(1 for item in enriched if item["warning"]["level"] == level)
                            for level in ("normal", "watch", "elevated", "critical")},
        "predictive_summary": {
            "signals_evaluated": sum(1 for item in enriched if item["predictive_outlook"]["status"] == "evaluated"),
            "insufficient_history": sum(1 for item in enriched if item["predictive_outlook"]["status"] == "insufficient_history"),
            "early_warning_candidates": sum(1 for item in enriched if item["predictive_outlook"]["early_warning_triggered"]),
            "notice": "Scenario indicators only; not probabilities or dated forecasts. Human review is required.",
        },
        "evidence_review_required": sum(1 for item in enriched if not item["evidence"]["evidence_complete"]),
        "source_intelligence_summary": {
            "signals_assessed": len(enriched), "status_counts": dict(sorted(statuses.items())),
            "reputation_verdicts_issued": 0,
            "notice": "Metadata assessment only. No automated source reliability or independence verdict is issued.",
        },
        "cross_source_analysis": corroboration, "signals": enriched,
        "limitations": [
            "RSS/Atom collection requires configured feeds and an internet connection.",
            "Source catalog geography, language, and publisher fields are supplied metadata, not independently verified.",
            "Unknown country, region, language, and publisher values are not inferred from domains.",
            "Coverage counts describe metadata completeness, not global representativeness.",
            "Cross-source grouping matches normalized titles only; distinct domains do not establish editorial independence or truth.",
            "Source intelligence checks metadata only; it does not rate reputation or verify claims.",
            "Warning levels and trend scores are heuristics based on supplied inputs and require human review.",
            "Registry state is in-memory for each run; persist reports with the JSON storage helpers.",
            "Global intelligence uses supplied geography, topics, entities, and score history only; related-event links are not causal findings.",
            "Predictive outlooks are linear scenarios in observation units based on supplied history; they are not dated forecasts or probabilities.",
        ],
    }

def collect_and_run(feeds: list[dict[str, Any]], extra_signals: Iterable[dict[str, Any]] = (),
                    brief_date: str | None = None, limit: int = 10) -> dict[str, Any]:
    """Validate source catalog, collect enabled feeds, and normalize all records."""
    catalog = validate_source_catalog(feeds)
    collection = collect_feeds([
        {"name": source["name"], "url": source["url"]} for source in catalog["sources"]
    ])
    metadata_by_url = {source["url"]: source for source in catalog["sources"]}
    normalized_collected = [
        normalize_global_signal(item, metadata_by_url.get(item.get("feed_url"), {}))
        for item in collection["signals"]
    ]
    local_signals = [normalize_global_signal(item) for item in extra_signals]
    report = run_pipeline([*normalized_collected, *local_signals],
                          brief_date=brief_date, limit=limit)
    report["collection"] = {key: value for key, value in collection.items() if key != "signals"}
    report["collection"].update({
        "sources_configured": catalog["sources_configured"],
        "sources_enabled": catalog["sources_enabled"],
        "source_configuration_errors": catalog["configuration_errors"],
        "extra_signals_added": len(local_signals),
    })
    return report
