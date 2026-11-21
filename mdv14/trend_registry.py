"""In-memory trend registry with stable IDs and deterministic deduplication."""
from __future__ import annotations

import hashlib
from typing import Any, Iterable

from .daily_brief import normalize_signal


def signal_id(signal: dict[str, Any]) -> str:
    """Create a stable identifier from normalized title and source URL."""
    normalized = normalize_signal(signal)
    identity = "|".join((normalized["title"].casefold(), normalized["url"].casefold()))
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


class TrendRegistry:
    """Small in-memory registry; persistence is deliberately delegated to callers."""

    def __init__(self, signals: Iterable[dict[str, Any]] = ()) -> None:
        self._signals: dict[str, dict[str, Any]] = {}
        for signal in signals:
            self.upsert(signal)

    def upsert(self, signal: dict[str, Any]) -> dict[str, Any]:
        normalized = normalize_signal(signal)
        if not normalized["title"]:
            raise ValueError("signal must include a title or topic")
        key = signal_id(normalized)
        current = self._signals.get(key, {})
        # Preserve supplied provenance fields (author, publication time, citations,
        # and source_profile) for later assessments; normalized core fields win.
        merged = {**current, **signal, **normalized, "id": key}
        self._signals[key] = merged
        return dict(merged)

    def all(self) -> list[dict[str, Any]]:
        return sorted(self._signals.values(), key=lambda item: item["id"])

    def __len__(self) -> int:
        return len(self._signals)
