"""Explicit-language coverage and deterministic bilingual research helpers."""
from __future__ import annotations

from collections import Counter
from typing import Any

SUPPORTED_RESEARCH_LANGUAGES = ("en", "id")
_LANGUAGE_NAMES = {
    "en": "English", "eng": "English", "english": "English",
    "id": "Indonesian", "ind": "Indonesian", "indonesian": "Indonesian",
    "in": "Indonesian",
    "fr": "French", "fra": "French", "french": "French",
    "es": "Spanish", "spa": "Spanish", "spanish": "Spanish",
    "de": "German", "ger": "German", "german": "German",
    "ar": "Arabic", "ara": "Arabic", "arabic": "Arabic",
    "zh": "Chinese", "zho": "Chinese", "chinese": "Chinese",
}


def normalize_language(value: Any) -> str | None:
    """Normalize a supplied language label; never infer language from content or URL."""
    raw = str(value or "").strip().casefold().replace("_", "-")
    if not raw:
        return None
    base = raw.split("-", 1)[0]
    return _LANGUAGE_NAMES.get(raw, _LANGUAGE_NAMES.get(base, raw))


def analyze_language_coverage(signals: list[dict[str, Any]]) -> dict[str, Any]:
    """Count only explicitly supplied language metadata."""
    counts = Counter()
    unknown = 0
    for signal in signals:
        label = normalize_language(signal.get("language")) if isinstance(signal, dict) else None
        if label:
            counts[label] += 1
        else:
            unknown += 1
    return {
        "records_total": len(signals),
        "records_with_declared_language": sum(counts.values()),
        "records_with_unknown_language": unknown,
        "language_counts": dict(sorted(counts.items())),
        "supported_research_languages": list(SUPPORTED_RESEARCH_LANGUAGES),
        "notice": "Language coverage uses explicit source/record metadata only. Language is not inferred from titles, text, country, or domain.",
    }
