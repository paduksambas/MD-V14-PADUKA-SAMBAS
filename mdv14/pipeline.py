"""Orchestrate MD V14's deterministic trend intelligence stages."""
from __future__ import annotations

from typing import Any, Iterable

from .daily_brief import build_daily_brief
from .early_warning import classify_signal
from .fact_check import assess_evidence
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

    brief = build_daily_brief(enriched, brief_date=brief_date, limit=limit)
    # Attach assessment metadata to the selected brief entries without changing ranking.
    assessments = {item["id"]: item for item in enriched}
    for item in brief["top_signals"]:
        match = assessments.get(signal_id(item))
        if match:
            item["evidence"] = match["evidence"]
            item["warning"] = match["warning"]

    return {
        "pipeline": "MD V14",
        "stage": "Build 1.2 integrated deterministic pipeline",
        "registry_size": len(registry),
        "daily_brief": brief,
        "warning_summary": {
            level: sum(1 for item in enriched if item["warning"]["level"] == level)
            for level in ("normal", "watch", "elevated", "critical")
        },
        "evidence_review_required": sum(
            1 for item in enriched if not item["evidence"]["evidence_complete"]
        ),
        "signals": enriched,
        "limitations": [
            "Trend collection is an upstream responsibility; this pipeline does not fetch live data.",
            "Evidence checks validate metadata and URL shape, not the truth of claims.",
            "Warning levels are heuristics based on supplied scores and require human review.",
            "Registry state is in-memory and must be persisted by an integrating application.",
        ],
    }
