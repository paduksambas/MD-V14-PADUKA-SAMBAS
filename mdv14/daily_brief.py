"""Daily Intelligence Brief generator for MD V14.

This module turns a collection of already-collected trend signals into a concise,
evidence-aware daily brief. It performs no web requests and never invents sources.
"""
from __future__ import annotations

from collections import Counter
from datetime import date
from typing import Any, Iterable
from urllib.parse import urlparse


def _clean_text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def normalize_signal(signal: dict[str, Any]) -> dict[str, Any]:
    """Normalize one signal without fabricating missing evidence."""
    title = _clean_text(signal.get("title") or signal.get("topic"))
    source = _clean_text(signal.get("source"))
    url = _clean_text(signal.get("url"))
    summary = _clean_text(signal.get("summary"))
    category = _clean_text(signal.get("category")) or "Unclassified"
    try:
        score = float(signal.get("score", 0))
    except (TypeError, ValueError):
        score = 0.0
    score = max(0.0, min(100.0, score))
    parsed_url = urlparse(url)
    valid_url = parsed_url.scheme in {"http", "https"} and bool(parsed_url.netloc)
    return {
        "id": _clean_text(signal.get("id")),
        "title": title,
        "source": source,
        "url": url,
        "summary": summary,
        "category": category,
        "score": round(score, 2),
        "evidence_complete": bool(title and source and valid_url),
    }


def build_daily_brief(
    signals: Iterable[dict[str, Any]],
    brief_date: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """Build a deterministic brief, ranking sourced signals ahead of incomplete ones."""
    if limit < 1:
        raise ValueError("limit must be at least 1")

    normalized = [normalize_signal(item) for item in signals]
    valid = [item for item in normalized if item["title"]]
    valid.sort(
        key=lambda item: (
            item["evidence_complete"],
            item["score"],
            item["title"].casefold(),
        ),
        reverse=True,
    )
    selected = valid[:limit]
    category_counts = Counter(item["category"] for item in selected)

    return {
        "date": brief_date or date.today().isoformat(),
        "title": "MD V14 — Daily Intelligence Brief",
        "total_signals_received": len(normalized),
        "signals_included": len(selected),
        "signals_needing_source_review": sum(
            1 for item in selected if not item["evidence_complete"]
        ),
        "top_signals": selected,
        "category_summary": dict(sorted(category_counts.items())),
        "methodology": (
            "Signals are ranked by evidence completeness, then supplied score. "
            "A signal is evidence-complete only when title, source, and URL exist. "
            "Scores are supplied inputs, not independently verified facts."
        ),
    }
