"""Unified, explainable strategic decision-support brief for MD V14.

This module prioritizes supplied signals for human review. It does not make
autonomous decisions, verify claims, or infer causal geopolitical outcomes.
"""
from __future__ import annotations

from math import isfinite
from typing import Any, Iterable


def _number(value: Any) -> float | None:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if isfinite(result) else None


def _bounded(value: float) -> float:
    return max(0.0, min(100.0, value))


def _signal_priority(signal: dict[str, Any], impact: dict[str, Any] | None) -> dict[str, Any]:
    score = _number(signal.get("score"))
    score = _bounded(score) if score is not None else None
    warning = signal.get("warning")
    warning = warning if isinstance(warning, dict) else {}
    predictive = signal.get("predictive_outlook")
    predictive = predictive if isinstance(predictive, dict) else {}
    evidence = signal.get("evidence")
    evidence = evidence if isinstance(evidence, dict) else {}

    dimensions = impact.get("impact_dimensions", []) if isinstance(impact, dict) else []
    dimensions = sorted({str(item) for item in dimensions if str(item).strip()}) if isinstance(dimensions, list) else []
    momentum = _number(predictive.get("momentum"))
    components: list[tuple[str, float, float]] = []
    if score is not None:
        components.append(("supplied_score", score, 0.55))
    if momentum is not None:
        components.append(("observed_momentum", _bounded(50.0 + momentum), 0.20))
    if impact is not None:
        components.append(("impact_dimension_cues", _bounded(len(dimensions) * 25.0), 0.15))
    if isinstance(evidence, dict) and "evidence_complete" in evidence:
        components.append(("evidence_gap_review", 0.0 if evidence.get("evidence_complete") else 100.0, 0.10))

    total_weight = sum(weight for _, _, weight in components)
    priority = round(sum(value * weight for _, value, weight in components) / total_weight, 2) if total_weight else 0.0
    band = "high" if priority >= 70 else "medium" if priority >= 40 else "routine"
    title = str(signal.get("title") or signal.get("topic") or "").strip()
    return {
        "signal_id": str(signal.get("id") or ""),
        "title": title,
        "source": str(signal.get("source") or "unknown"),
        "url": str(signal.get("url") or ""),
        "country": str(signal.get("country") or "unknown"),
        "priority_score": priority,
        "priority_band": band,
        "warning_level": str(warning.get("level") or "not_assessed"),
        "trend_outlook": str(predictive.get("outlook") or "not_assessed"),
        "momentum": round(momentum, 2) if momentum is not None else None,
        "impact_dimensions": dimensions,
        "evidence_complete": evidence.get("evidence_complete") if "evidence_complete" in evidence else None,
        "scoring_components": [
            {"component": name, "value": round(value, 2), "configured_weight": weight}
            for name, value, weight in components
        ],
        "requires_human_review": True,
    }


def build_strategic_decision_brief(
    signals: Iterable[dict[str, Any]],
    *,
    global_intelligence: dict[str, Any] | None = None,
    predictive_summary: dict[str, Any] | None = None,
    research: dict[str, Any] | None = None,
    strategic_impact: dict[str, Any] | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Fuse existing assessments into a traceable human-review priority list."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    rows = [item for item in signals if isinstance(item, dict)
            and str(item.get("title") or item.get("topic") or "").strip()]
    impact_rows = strategic_impact.get("assessments", []) if isinstance(strategic_impact, dict) else []
    impact_by_id = {
        str(item.get("signal_id") or ""): item
        for item in impact_rows if isinstance(item, dict) and item.get("signal_id")
    } if isinstance(impact_rows, list) else {}
    ranked = [
        _signal_priority(item, impact_by_id.get(str(item.get("id") or "")))
        for item in rows
    ]
    ranked.sort(key=lambda item: (-item["priority_score"], item["title"].casefold(), item["signal_id"]))

    evidence_gaps = sum(1 for item in ranked if item["evidence_complete"] is False)
    missing_urls = sum(1 for item in ranked if not item["url"])
    missing_country = sum(1 for item in ranked if item["country"] == "unknown")
    research_gaps = research.get("research_gaps", []) if isinstance(research, dict) else []
    research_gaps = [str(item) for item in research_gaps] if isinstance(research_gaps, list) else []
    momentum_candidates = (
        global_intelligence.get("rising_signals", [])
        if isinstance(global_intelligence, dict) else []
    )
    momentum_candidates = len(momentum_candidates) if isinstance(momentum_candidates, list) else 0
    predictive_candidates = (
        predictive_summary.get("early_warning_candidates", 0)
        if isinstance(predictive_summary, dict) else 0
    )
    try:
        predictive_candidates = max(0, int(predictive_candidates))
    except (TypeError, ValueError):
        predictive_candidates = 0

    return {
        "engine": "MD V14 Global Intelligence Fusion & Strategic Decision Support",
        "build": "2.5",
        "signals_fused": len(ranked),
        "priority_band_counts": {
            band: sum(1 for item in ranked if item["priority_band"] == band)
            for band in ("high", "medium", "routine")
        },
        "review_queue": ranked[:limit],
        "evidence_and_coverage_gaps": {
            "signals_missing_complete_evidence": evidence_gaps,
            "signals_without_url": missing_urls,
            "signals_with_unknown_country": missing_country,
            "research_gaps": research_gaps,
        },
        "fused_context": {
            "global_rising_signal_candidates": momentum_candidates,
            "predictive_early_warning_candidates": predictive_candidates,
            "strategic_cross_border_review_candidates": (
                len(strategic_impact.get("cross_border_review_candidates", []))
                if isinstance(strategic_impact, dict)
                and isinstance(strategic_impact.get("cross_border_review_candidates", []), list)
                else 0
            ),
        },
        "recommended_human_actions": [
            "Review high-priority records against original sources and primary documents.",
            "Check publication dates, source attribution, and whether evidence is independently corroborated.",
            "Validate country, actor, and impact labels; leave missing metadata explicitly unknown.",
            "Compare conflicting accounts and document uncertainty before making a strategic judgment.",
            "Escalate or communicate findings only through an authorized human decision-maker.",
        ],
        "methodology": {
            "priority_score": "Weighted mean of available components: supplied score 55%, observed momentum indicator 20%, keyword impact-dimension cues 15%, evidence-gap review cue 10%; weights are renormalized when a component is unavailable.",
            "momentum_indicator": "Maps observed score momentum to a bounded 0-100 review indicator using 50 + momentum; it is not a forecast.",
            "impact_dimension_cues": "Uses the existing keyword-based impact dimensions; at most four dimensions contribute to this component.",
            "traceability": "Each queue item preserves signal ID, title, source, URL, country, warning, outlook, evidence state, and component values.",
            "fusion": "Global, predictive, research, and strategic-impact summaries are context indicators; they are not treated as independent confirmations.",
        },
        "limitations": [
            "Priority scores rank analyst review order only; they are not event severity, probability, or policy recommendations.",
            "Inputs are supplied metadata and existing heuristic assessments; this stage performs no new web research or independent fact verification.",
            "Momentum and warning indicators may share underlying score history or score inputs and must not be interpreted as independent evidence.",
            "Keyword impact dimensions can miss context or produce false matches.",
            "No causal inference, geopolitical forecast, autonomous action, notification, or publication is performed.",
        ],
        "notice": "Human decision support only. Verify original evidence, context, uncertainty, and affected stakeholders before acting.",
    }
