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

from html import escape


def render_country_explorer_html(data: dict[str, Any]) -> str:
    """Render an interactive, self-contained country centroid plot and traceable record list."""
    mapped = data.get("mapped_countries", [])
    unmapped = data.get("unmapped_countries", [])
    mapped = [item for item in mapped if isinstance(item, dict)] if isinstance(mapped, list) else []
    unmapped = [item for item in unmapped if isinstance(item, dict)] if isinstance(unmapped, list) else []
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    markers = []
    buttons = []
    details = []
    rows = []
    for item in mapped:
        lat = _number(item.get("latitude"))
        lon = _number(item.get("longitude"))
        x = 40 + ((lon + 180) / 360) * 680
        y = 20 + ((90 - lat) / 180) * 340
        counts = item.get("review_priority_counts") or {}
        band = "high" if counts.get("high", 0) else "medium" if counts.get("medium", 0) else "routine"
        radius = max(5, min(14, 4 + (int(item.get("signal_count", 0) or 0) ** 0.5) * 2))
        key, name = esc(item.get("canonical_name")), esc(item.get("name"))
        markers.append(
            f'<g class="country-marker priority-{band}" data-country-key="{key}" role="button" tabindex="0" aria-label="Select {name}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}"></circle>'
            f'<title>{name}: {item.get("signal_count", 0)} signals</title></g>'
        )
        buttons.append(f'<button type="button" class="country-select" data-country-key="{key}" aria-pressed="false">{name} · {item.get("signal_count", 0)}</button>')
        record_rows = []
        for record in item.get("records", []):
            url = str(record.get("url") or "")
            link = f'<a rel="noopener noreferrer" target="_blank" href="{esc(url)}">Open source</a>' if url.startswith(("http://", "https://")) else "Unavailable"
            record_rows.append(
                f'<tr><td>{esc(record.get("title"))}</td><td>{esc(record.get("source"))}</td>'
                f'<td>{esc(record.get("priority_band"))}</td><td>{esc(record.get("warning_level"))}</td>'
                f'<td>{esc(record.get("signal_id"))}</td><td>{link}</td></tr>'
            )
        details.append(
            f'<div class="country-detail" data-country-key="{key}" hidden><h3>{name}</h3>'
            f'<p>{item.get("signal_count", 0)} signals · average supplied score {item.get("average_score", 0)}</p>'
            f'<p>Review priority — high: {counts.get("high", 0)}, medium: {counts.get("medium", 0)}, routine: {counts.get("routine", 0)}</p>'
            f'<div class="table-wrap"><table><thead><tr><th>Signal</th><th>Source</th><th>Priority</th><th>Warning</th><th>ID</th><th>Article</th></tr></thead>'
            f'<tbody>{"".join(record_rows) or "<tr><td colspan=6>No records.</td></tr>"}</tbody></table></div></div>'
        )
        rows.append(
            f'<tr><td>{name}</td><td class="num">{item.get("signal_count", 0)}</td>'
            f'<td class="num">{item.get("average_score", 0)}</td>'
            f'<td>{counts.get("high", 0)} / {counts.get("medium", 0)} / {counts.get("routine", 0)}</td><td>Mapped</td></tr>'
        )
    for item in unmapped:
        counts = item.get("review_priority_counts") or {}
        rows.append(
            f'<tr><td>{esc(item.get("name"))}</td><td class="num">{item.get("signal_count", 0)}</td>'
            f'<td class="num">{item.get("average_score", 0)}</td>'
            f'<td>{counts.get("high", 0)} / {counts.get("medium", 0)} / {counts.get("routine", 0)}</td>'
            '<td>Unmapped — centroid unavailable</td></tr>'
        )
    grid = "".join(
        f'<line x1="{40 + ((lon + 180) / 360) * 680:.1f}" y1="20" x2="{40 + ((lon + 180) / 360) * 680:.1f}" y2="360" class="map-gridline"/>'
        for lon in (-120, -60, 0, 60, 120)
    ) + "".join(
        f'<line x1="40" y1="{20 + ((90 - lat) / 180) * 340:.1f}" x2="720" y2="{20 + ((90 - lat) / 180) * 340:.1f}" class="map-gridline"/>'
        for lat in (-60, -30, 0, 30, 60)
    )
    markers_html = "".join(markers) or '<text x="380" y="190" text-anchor="middle" fill="currentColor">No mapped country records</text>'
    return (
        '<section class="panel" id="country-explorer"><h2>Global Geopolitical Intelligence Map &amp; Country Explorer · Build 3.1</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Countries represented</div><strong>{data.get("countries_total", 0)}</strong><small>Explicit country labels</small></article>'
        f'<article class="metric"><div class="muted">Mapped countries</div><strong>{data.get("countries_mapped", 0)}</strong><small>Approximate centroid references</small></article>'
        f'<article class="metric"><div class="muted">Unmapped countries</div><strong>{data.get("countries_unmapped", 0)}</strong><small>No coordinate guessed</small></article>'
        f'<article class="metric"><div class="muted">Signals with country</div><strong>{data.get("signals_with_country", 0)}</strong><small>Supplied country metadata</small></article></div>'
        '<p class="muted">Geographic signal plot using approximate country centroid references. Points indicate records labelled with that country; they do not locate an event or represent territorial boundaries.</p>'
        f'<div class="map-wrap"><svg class="world-plot" viewBox="0 0 760 380" role="img" aria-label="Longitude and latitude plot of countries represented in the report">'
        f'<rect x="0" y="0" width="760" height="380" rx="12" class="map-bg"/>{grid}{markers_html}</svg></div>'
        '<div class="map-legend"><span><i class="legend-dot priority-high"></i>Contains high review-priority signals</span>'
        '<span><i class="legend-dot priority-medium"></i>Contains medium review-priority signals</span>'
        '<span><i class="legend-dot priority-routine"></i>No high/medium queue item</span></div>'
        f'<div class="country-picker">{"".join(buttons) or "<p>No mapped countries to select.</p>"}</div>'
        f'<div id="country-detail-panel"><p>Select a plotted country or country label to inspect its signals.</p>{"".join(details) or "<p>No country detail available.</p>"}</div>'
        '<h3>Country coverage and review profile</h3><div class="table-wrap"><table><thead><tr><th>Country label</th><th>Signals</th><th>Average score</th><th>High / medium / routine</th><th>Map status</th></tr></thead>'
        f'<tbody>{"".join(rows) or "<tr><td colspan=5>No country-labelled signals in this report.</td></tr>"}</tbody></table></div>'
        '<p class="muted">Priority counts are review-order cues, not geopolitical risk ratings, threat levels, or probabilities. Countries without a supported centroid remain visible in the table but are not plotted.</p></section>'
        '<script>document.querySelectorAll(".country-marker, .country-select").forEach(function(el) {'
        'function selectCountry() { var key=el.getAttribute("data-country-key");'
        'document.querySelectorAll(".country-detail").forEach(function(panel) {panel.hidden=panel.getAttribute("data-country-key")!==key;});'
        'document.querySelectorAll(".country-select").forEach(function(button) {button.setAttribute("aria-pressed",button.getAttribute("data-country-key")===key?"true":"false");});'
        'var prompt=document.querySelector("#country-detail-panel > p"); if(prompt) prompt.hidden=true; }'
        'el.addEventListener("click",selectCountry);el.addEventListener("keydown",function(event){'
        'if(event.key==="Enter"||event.key===" "){event.preventDefault();selectCountry();}});});</script>'
    )
