"""Geographic country explorer built only from explicitly labelled signal metadata."""
from __future__ import annotations

from collections import defaultdict
from math import isfinite
from typing import Any


# Approximate country-centroid references for plotting only, not territorial boundaries.
_COUNTRY_COORDINATES = {
    "afghanistan": (33.94, 67.71), "argentina": (-38.42, -63.62),
    "australia": (-25.27, 133.78), "bangladesh": (23.68, 90.36),
    "brazil": (-14.24, -51.93), "canada": (56.13, -106.35),
    "china": (35.86, 104.20), "colombia": (4.57, -74.30),
    "egypt": (26.82, 30.80), "france": (46.23, 2.21),
    "germany": (51.17, 10.45), "india": (20.59, 78.96),
    "indonesia": (-0.79, 113.92), "iran": (32.43, 53.69),
    "iraq": (33.22, 43.68), "israel": (31.05, 34.85),
    "italy": (41.87, 12.57), "japan": (36.20, 138.25),
    "kenya": (-0.02, 37.91), "malaysia": (4.21, 101.98),
    "mexico": (23.63, -102.55), "myanmar": (21.92, 95.96),
    "netherlands": (52.13, 5.29), "new zealand": (-40.90, 174.89),
    "nigeria": (9.08, 8.68), "north korea": (40.34, 127.51),
    "pakistan": (30.38, 69.35), "philippines": (12.88, 121.77),
    "poland": (51.92, 19.15), "qatar": (25.35, 51.18),
    "russia": (61.52, 105.32), "saudi arabia": (23.89, 45.08),
    "singapore": (1.35, 103.82), "south africa": (-30.56, 22.94),
    "south korea": (35.91, 127.77), "spain": (40.46, -3.75),
    "sri lanka": (7.87, 80.77), "sudan": (12.86, 30.22),
    "taiwan": (23.70, 120.96), "thailand": (15.87, 100.99),
    "turkey": (38.96, 35.24), "ukraine": (48.38, 31.17),
    "united arab emirates": (23.42, 53.85), "united kingdom": (55.38, -3.44),
    "united states": (37.09, -95.71), "usa": (37.09, -95.71),
    "vietnam": (14.06, 108.28), "yemen": (15.55, 48.52),
}
_ALIASES = {
    "us": "united states", "u.s.": "united states", "u.s.a.": "united states",
    "united states of america": "united states", "uk": "united kingdom",
    "republic of korea": "south korea", "korea, republic of": "south korea",
    "republic of indonesia": "indonesia", "russian federation": "russia",
}


def _number(value: Any) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0
    return result if isfinite(result) else 0.0


def _country_key(value: Any) -> str:
    label = str(value or "").strip().casefold()
    return _ALIASES.get(label, label)


def build_country_explorer(report: dict[str, Any], *, limit: int = 50) -> dict[str, Any]:
    """Aggregate country-labelled signals and map only countries in the curated centroid catalog."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    signals = report.get("signals", [])
    signals = [item for item in signals if isinstance(item, dict)] if isinstance(signals, list) else []
    decision = report.get("strategic_decision", {})
    decision = decision if isinstance(decision, dict) else {}
    queue = decision.get("review_queue", [])
    queue = [item for item in queue if isinstance(item, dict)] if isinstance(queue, list) else []
    queue_by_id = {str(item.get("signal_id") or ""): item for item in queue if item.get("signal_id")}
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    labels: dict[str, str] = {}
    for index, signal in enumerate(signals):
        label = str(signal.get("country") or "").strip()
        key = _country_key(label)
        if not key or key == "unknown":
            continue
        labels.setdefault(key, label)
        groups[key].append(signal)

    countries = []
    for key, members in groups.items():
        scores = [_number(item.get("score")) for item in members]
        high = medium = routine = 0
        warning_counts: dict[str, int] = {}
        source_records = []
        for signal in members:
            sid = str(signal.get("id") or "")
            review = queue_by_id.get(sid, {})
            band = str(review.get("priority_band") or "not_ranked")
            if band == "high":
                high += 1
            elif band == "medium":
                medium += 1
            elif band == "routine":
                routine += 1
            warning = signal.get("warning")
            warning = warning if isinstance(warning, dict) else {}
            level = str(warning.get("level") or "not_assessed")
            warning_counts[level] = warning_counts.get(level, 0) + 1
            source_records.append({
                "signal_id": sid or f"record-{len(source_records) + 1}",
                "title": str(signal.get("title") or signal.get("topic") or ""),
                "source": str(signal.get("source") or "unknown"),
                "url": str(signal.get("url") or ""),
                "score": _number(signal.get("score")),
                "priority_band": band,
                "warning_level": level,
            })
        coords = _COUNTRY_COORDINATES.get(key)
        countries.append({
            "name": labels[key],
            "canonical_name": key,
            "signal_count": len(members),
            "average_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "review_priority_counts": {"high": high, "medium": medium, "routine": routine},
            "warning_counts": dict(sorted(warning_counts.items())),
            "mapped": coords is not None,
            "latitude": coords[0] if coords else None,
            "longitude": coords[1] if coords else None,
            "records": sorted(source_records, key=lambda item: (-item["score"], item["title"].casefold()))[:limit],
            "notice": "Review-priority counts are analyst triage cues, not country risk ratings.",
        })
    countries.sort(key=lambda item: (-item["signal_count"], -item["average_score"], item["name"].casefold()))
    mapped = [item for item in countries if item["mapped"]]
    unmapped = [item for item in countries if not item["mapped"]]
    return {
        "build": "3.1",
        "method": "Explicit country metadata joined to a curated approximate centroid catalog.",
        "countries_total": len(countries),
        "countries_mapped": len(mapped),
        "countries_unmapped": len(unmapped),
        "signals_with_country": sum(item["signal_count"] for item in countries),
        "mapped_countries": mapped[:limit],
        "unmapped_countries": unmapped[:limit],
        "limitations": [
            "Centroids are approximate plotting references, not borders, disputed-territory positions, or evidence of event location.",
            "Only explicit country labels are grouped; unknown geography is not inferred.",
            "Review-priority and warning counts describe supplied signal assessments, not geopolitical risk, threat severity, or probability.",
            "Country coverage reflects configured source metadata and is not globally representative.",
        ],
    }
