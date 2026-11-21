"""Explainable short-horizon trend outlooks from supplied score history.

The module produces scenario indicators in observation units, not dated forecasts,
probabilities, or claims about future events.
"""
from __future__ import annotations

from math import ceil, isfinite
from typing import Any

from .advanced_scoring import assess_advanced_trend
from .early_warning import WarningThresholds


def assess_predictive_outlook(
    signal: dict[str, Any],
    *,
    thresholds: WarningThresholds | None = None,
    horizon_observations: int = 3,
) -> dict[str, Any]:
    """Estimate a bounded score scenario over N future observations.

    A simple mean of up to the last three supplied score changes is extended
    linearly. This is deliberately labelled a heuristic scenario, not a forecast.
    """
    if horizon_observations < 1:
        raise ValueError("horizon_observations must be at least 1")
    thresholds = thresholds or WarningThresholds()
    history = signal.get("score_history")
    if not isinstance(history, list):
        history = []

    scores: list[float] = []
    for row in history:
        if not isinstance(row, dict):
            continue
        try:
            value = float(row.get("score"))
        except (TypeError, ValueError):
            continue
        if isfinite(value):
            scores.append(max(0.0, min(100.0, value)))

    try:
        current = float(signal.get("score", scores[-1] if scores else 0.0))
    except (TypeError, ValueError):
        current = scores[-1] if scores else 0.0
    if not isfinite(current):
        current = scores[-1] if scores else 0.0
    current = max(0.0, min(100.0, current))

    advanced = assess_advanced_trend(history, current_score=current)
    deltas = [b - a for a, b in zip(scores, scores[1:])]
    recent_deltas = deltas[-3:]
    if len(scores) < 2:
        return {
            "status": "insufficient_history",
            "outlook": "insufficient_history",
            "observation_count": len(scores),
            "current_score": round(current, 2),
            "projected_score": None,
            "horizon_observations": horizon_observations,
            "estimated_observations_to_elevated": None,
            "projected_warning_level": None,
            "early_warning_triggered": False,
            "requires_human_review": True,
            "momentum": advanced["momentum"],
            "acceleration": advanced["acceleration"],
            "notice": "At least two valid score observations are required; no projection was fabricated.",
        }

    momentum = round(sum(recent_deltas) / len(recent_deltas), 2)
    acceleration = advanced["acceleration"]
    projected = round(max(0.0, min(100.0, current + momentum * horizon_observations)), 2)
    if momentum > 0 and acceleration is not None and acceleration > 0:
        outlook = "accelerating_rise"
    elif momentum > 0:
        outlook = "rising"
    elif momentum < 0:
        outlook = "declining"
    else:
        outlook = "stable"

    projected_level = (
        "critical" if projected >= thresholds.critical else
        "elevated" if projected >= thresholds.elevated else
        "watch" if projected >= thresholds.watch else "normal"
    )
    current_level = (
        "critical" if current >= thresholds.critical else
        "elevated" if current >= thresholds.elevated else
        "watch" if current >= thresholds.watch else "normal"
    )
    crosses_elevated = current < thresholds.elevated <= projected
    estimated = (
        max(1, ceil((thresholds.elevated - current) / momentum))
        if momentum > 0 and current < thresholds.elevated else None
    )
    return {
        "status": "evaluated",
        "outlook": outlook,
        "observation_count": len(scores),
        "current_score": round(current, 2),
        "recent_average_change": momentum,
        "momentum": advanced["momentum"],
        "acceleration": acceleration,
        "projected_score": projected,
        "horizon_observations": horizon_observations,
        "estimated_observations_to_elevated": estimated,
        "current_warning_level": current_level,
        "projected_warning_level": projected_level,
        "early_warning_triggered": crosses_elevated,
        "requires_human_review": crosses_elevated or projected_level in {"elevated", "critical"},
        "method": "Linear extension of the mean of up to three latest supplied score changes; result clamped to 0-100.",
        "notice": "Scenario indicator only. Observation intervals may be irregular; this is not a dated forecast, probability, causal finding, or guarantee.",
    }
