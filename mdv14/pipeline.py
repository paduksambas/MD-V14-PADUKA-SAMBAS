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
from .research_orchestrator import build_research_report
from .strategic_impact import analyze_strategic_impact
from .strategic_decision import build_strategic_decision_brief
from .monitoring import build_monitoring_status
from .language_intelligence import analyze_language_coverage
from .knowledge_graph import build_knowledge_graph
from .analyst_report import build_analyst_report
from .command_center import build_command_center
from .country_explorer import build_country_explorer
from .economic_intelligence import analyze_economic_intelligence
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
    strategic_impact = analyze_strategic_impact(enriched, limit=max(limit, len(enriched)))
    predictive_summary = {
        "signals_evaluated": sum(1 for item in enriched if item["predictive_outlook"]["status"] == "evaluated"),
        "insufficient_history": sum(1 for item in enriched if item["predictive_outlook"]["status"] == "insufficient_history"),
        "early_warning_candidates": sum(1 for item in enriched if item["predictive_outlook"]["early_warning_triggered"]),
        "notice": "Scenario indicators only; not probabilities or dated forecasts. Human review is required.",
    }
    statuses = {}
    for item in enriched:
        status = item["source_intelligence"]["status"]
        statuses[status] = statuses.get(status, 0) + 1
    report = {
        "pipeline": "MD V14", "stage": "Build 3.0 global strategic intelligence command center",
        "data_schema_version": "1.0", "registry_size": len(registry),
        "data_coverage": build_data_coverage(enriched),
        "language_intelligence": analyze_language_coverage(enriched),
        "knowledge_graph": build_knowledge_graph(enriched, limit=max(limit, len(enriched) * 3)),
        "daily_brief": brief,
        "global_intelligence": global_intelligence,
        "strategic_impact": strategic_impact,
        "strategic_decision": build_strategic_decision_brief(
            enriched, global_intelligence=global_intelligence,
            predictive_summary=predictive_summary, strategic_impact=strategic_impact,
            limit=limit,
        ),
        "warning_summary": {level: sum(1 for item in enriched if item["warning"]["level"] == level)
                            for level in ("normal", "watch", "elevated", "critical")},
        "predictive_summary": predictive_summary,
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
            "Multilingual research relevance uses a small deterministic English-Indonesian vocabulary; it is not translation, semantic search, or language detection.",
            "Knowledge graph entity matching uses a curated alias catalog and explicit metadata only; matches and graph edges require human review and do not establish causality or truth.",
            "Coverage counts describe metadata completeness, not global representativeness.",
            "Cross-source grouping matches normalized titles only; distinct domains do not establish editorial independence or truth.",
            "Source intelligence checks metadata only; it does not rate reputation or verify claims.",
            "Warning levels and trend scores are heuristics based on supplied inputs and require human review.",
            "Registry state is in-memory for each run; persist reports with the JSON storage helpers.",
            "Global intelligence uses supplied geography, topics, entities, and score history only; related-event links are not causal findings.",
            "Predictive outlooks are linear scenarios in observation units based on supplied history; they are not dated forecasts or probabilities.",
            "Strategic impact dimensions are keyword-based review cues; geopolitical cross-border candidates require explicit shared metadata and do not establish causality.",
            "Strategic decision priority scores rank human review order only; they are not severity, probability, or policy recommendations.",
            "Analyst report is deterministic synthesis of existing assessments, not a generative AI model or independent fact verification.",
        ],
    }
    report["analyst_report"] = build_analyst_report(report, limit=limit)
    report["command_center"] = build_command_center(report, limit=limit)
    report["country_explorer"] = build_country_explorer(report, limit=limit)
    report["economic_intelligence"] = analyze_economic_intelligence(report["signals"], limit=limit)
    return report

def collect_and_run(feeds: list[dict[str, Any]], extra_signals: Iterable[dict[str, Any]] = (),
                    brief_date: str | None = None, limit: int = 10,
                    research_question: str | None = None) -> dict[str, Any]:
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
    report["monitoring"] = build_monitoring_status(report["collection"], report["signals"])
    report["analyst_report"] = build_analyst_report(report, limit=limit)
    report["command_center"] = build_command_center(report, limit=limit)
    report["country_explorer"] = build_country_explorer(report, limit=limit)
    if research_question and research_question.strip():
        report["research"] = build_research_report(
            research_question, report["signals"], report["collection"], limit=limit
        )
        report["strategic_decision"] = build_strategic_decision_brief(
            report["signals"], global_intelligence=report["global_intelligence"],
            predictive_summary=report["predictive_summary"],
            research=report["research"], strategic_impact=report["strategic_impact"],
            limit=limit,
        )
        report["analyst_report"] = build_analyst_report(report, limit=limit)
        report["command_center"] = build_command_center(report, limit=limit)
        report["country_explorer"] = build_country_explorer(report, limit=limit)
        report["economic_intelligence"] = analyze_economic_intelligence(report["signals"], limit=limit)
    return report
