"""Group matching story titles and count distinct reporting domains."""
from __future__ import annotations

import re
from collections import defaultdict
from typing import Any
from urllib.parse import urlparse


def normalize_title(title: str) -> str:
    """Normalize punctuation and whitespace for exact-title matching only."""
    return " ".join(re.findall(r"[a-z0-9]+", title.casefold()))


def corroborate_sources(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Count distinct URL domains per normalized title; this is not truth verification."""
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for signal in signals:
        title = str(signal.get("title") or signal.get("topic") or "").strip()
        key = normalize_title(title)
        if key:
            groups[key].append(signal)

    reports = []
    for key, items in sorted(groups.items()):
        domains = sorted({
            (urlparse(str(item.get("url", ""))).hostname or "").lower()
            for item in items
            if urlparse(str(item.get("url", ""))).scheme in {"http", "https"}
            and urlparse(str(item.get("url", ""))).hostname
        })
        reports.append({
            "normalized_title": key,
            "representative_title": str(items[0].get("title") or items[0].get("topic") or ""),
            "mention_count": len(items),
            "distinct_source_domains": domains,
            "distinct_source_count": len(domains),
            "corroboration_level": (
                "multiple_domains" if len(domains) >= 2
                else "single_domain" if len(domains) == 1
                else "no_valid_source_domain"
            ),
            "truth_verified": False,
            "caveat": "Distinct domains do not prove editorial independence or factual accuracy; inspect original reporting.",
        })
    return reports
