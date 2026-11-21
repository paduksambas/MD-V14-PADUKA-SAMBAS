"""Threshold-based early warning classification; no autonomous external alerts."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class WarningThresholds:
    watch: float = 40.0
    elevated: float = 60.0
    critical: float = 80.0

    def __post_init__(self) -> None:
        values = (self.watch, self.elevated, self.critical)
        if any(value < 0 or value > 100 for value in values):
            raise ValueError("thresholds must be between 0 and 100")
        if not self.watch < self.elevated < self.critical:
            raise ValueError("thresholds must be strictly increasing")


def classify_signal(signal: dict[str, Any], thresholds: WarningThresholds | None = None) -> dict[str, Any]:
    thresholds = thresholds or WarningThresholds()
    try:
        score = float(signal.get("score", 0))
    except (TypeError, ValueError):
        score = 0.0
    score = max(0.0, min(100.0, score))
    if score >= thresholds.critical:
        level = "critical"
    elif score >= thresholds.elevated:
        level = "elevated"
    elif score >= thresholds.watch:
        level = "watch"
    else:
        level = "normal"
    return {
        "level": level,
        "score": round(score, 2),
        "thresholds": {
            "watch": thresholds.watch,
            "elevated": thresholds.elevated,
            "critical": thresholds.critical,
        },
        "requires_human_review": level in {"elevated", "critical"},
        "notice": "Classification is a heuristic based on the supplied score, not a verified prediction.",
    }
