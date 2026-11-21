"""Explainable momentum, acceleration and anomaly indicators for trend histories."""
from __future__ import annotations

from statistics import median
from typing import Any, Iterable


def assess_advanced_trend(
    observations: Iterable[dict[str, Any]] = (),
    *,
    current_score: float | int | None = None,
) -> dict[str, Any]:
    """Assess supplied score history; never infer missing observations or probabilities.

    Anomaly detection compares the latest score delta with at least three prior
    deltas. The attention index is a bounded heuristic indicator, not a forecast.
    """
    rows = list(observations)
    scores: list[float] = []
    for row in rows:
        try:
            value = float(row["score"])
        except (KeyError, TypeError, ValueError):
            continue
        if value == value and value not in (float("inf"), float("-inf")):
            scores.append(max(0.0, min(100.0, value)))

    if current_score is not None and not scores:
        try:
            scores = [max(0.0, min(100.0, float(current_score)))]
        except (TypeError, ValueError):
            scores = []

    deltas = [round(b - a, 2) for a, b in zip(scores, scores[1:])]
    momentum = deltas[-1] if deltas else None
    acceleration = round(deltas[-1] - deltas[-2], 2) if len(deltas) >= 2 else None

    anomaly = {
        "detected": False,
        "status": "insufficient_history",
        "latest_delta": momentum,
        "baseline_median_delta": None,
        "threshold": None,
        "notice": "Anomaly checks require at least three prior score changes plus a latest change.",
    }
    if len(deltas) >= 4:
        baseline = deltas[:-1]
        center = median(baseline)
        mad = median([abs(value - center) for value in baseline])
        threshold = max(15.0, 3.0 * mad)
        deviation = abs(deltas[-1] - center)
        anomaly = {
            "detected": deviation > threshold,
            "status": "evaluated",
            "latest_delta": deltas[-1],
            "baseline_median_delta": round(center, 2),
            "threshold": round(threshold, 2),
            "notice": "Unusual score movement is a review flag, not evidence of virality or manipulation.",
        }

    count = len(scores)
    if count >= 3:
        confidence = "moderate"
        sufficiency = "sufficient_for_momentum_and_acceleration"
    elif count == 2:
        confidence = "low"
        sufficiency = "limited_momentum_only"
    else:
        confidence = "insufficient"
        sufficiency = "insufficient_history"

    score = scores[-1] if scores else (
        max(0.0, min(100.0, float(current_score))) if current_score is not None else 0.0
    )
    # A compact descriptive index: current score plus a restrained momentum
    # adjustment. It is intentionally unavailable without two observations.
    attention_index = (
        round(max(0.0, min(100.0, score + max(-10.0, min(10.0, momentum)) * 0.5)), 2)
        if momentum is not None else None
    )
    return {
        "observation_count": count,
        "momentum": momentum,
        "acceleration": acceleration,
        "momentum_direction": (
            "rising" if momentum > 0 else "falling" if momentum < 0 else "stable"
        ) if momentum is not None else "insufficient_history",
        "anomaly": anomaly,
        "attention_potential_index": attention_index,
        "data_sufficiency": sufficiency,
        "confidence": confidence,
        "method": {
            "momentum": "latest supplied score minus previous supplied score",
            "acceleration": "latest score delta minus preceding score delta; needs three observations",
            "anomaly": "latest delta compared with prior-delta median; requires five observations",
            "attention_potential_index": "current score plus half the latest delta, capped to a ten-point adjustment",
        },
        "notice": "All indicators are descriptive heuristics from supplied scores, not probabilities, causal findings, or guaranteed forecasts. Domain counts do not prove independent reporting or truth.",
    }
