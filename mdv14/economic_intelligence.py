"""Global economic intelligence and sectoral market-impact review cues.

Uses supplied article metadata and curated bilingual keywords only. It does not
measure financial-market moves, infer causality, or produce investment advice.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any, Iterable

_SECTORS = {
    "energy": {
        "label": "Energy",
        "keywords": {"oil", "crude", "petroleum", "gas", "lng", "opec", "electricity", "power", "renewable", "solar", "wind", "coal", "minyak", "mentah", "petroleum", "gas", "listrik", "energi", "terbarukan", "surya", "batu", "bara"},
        "channels": ["Energy supply and infrastructure", "Fuel import/export exposure", "Energy transition policy"],
    },
    "commodities_mining": {
        "label": "Commodities & Mining",
        "keywords": {"commodity", "commodities", "gold", "copper", "nickel", "tin", "aluminium", "aluminum", "lithium", "mineral", "mining", "ore", "smelter", "komoditas", "emas", "tembaga", "nikel", "timah", "aluminium", "litium", "mineral", "tambang", "bijih", "smelter"},
        "channels": ["Raw-material supply and processing", "Export restrictions and royalties", "Industrial input availability"],
    },
    "trade_supply_chain": {
        "label": "Trade & Supply Chains",
        "keywords": {"trade", "tariff", "export", "exports", "import", "imports", "customs", "sanction", "sanctions", "embargo", "supply", "chain", "shipping", "container", "logistics", "trade", "perdagangan", "tarif", "ekspor", "impor", "bea", "cukai", "sanksi", "embargo", "pasokan", "rantai", "pelayaran", "kontainer", "logistik"},
        "channels": ["Cross-border goods flows", "Tariff and sanctions exposure", "Supplier and logistics concentration"],
    },
    "finance_macro": {
        "label": "Finance & Macroeconomy",
        "keywords": {"inflation", "interest", "rates", "central", "bank", "currency", "exchange", "forex", "bond", "debt", "fiscal", "monetary", "recession", "gdp", "budget", "rupiah", "inflasi", "bunga", "suku", "bank", "sentral", "mata", "uang", "kurs", "obligasi", "utang", "fiskal", "moneter", "resesi", "pdb", "anggaran"},
        "channels": ["Monetary and fiscal policy", "Currency and financing conditions", "Inflation and growth context"],
    },
    "technology_semiconductors": {
        "label": "Technology & Semiconductors",
        "keywords": {"semiconductor", "semiconductors", "chip", "chips", "foundry", "wafer", "lithography", "artificial", "intelligence", "data", "center", "cloud", "technology", "export", "control", "semikonduktor", "cip", "pabrik", "wafer", "litografi", "kecerdasan", "buatan", "pusat", "data", "awan", "teknologi", "kendali", "ekspor"},
        "channels": ["Chip and critical technology supply", "Export controls and investment screening", "Digital infrastructure capacity"],
    },
    "agriculture_food": {
        "label": "Agriculture & Food",
        "keywords": {"agriculture", "farming", "wheat", "rice", "corn", "maize", "soy", "fertilizer", "food", "grain", "palm", "cpo", "crops", "pertanian", "pangan", "beras", "jagung", "kedelai", "pupuk", "gandum", "sawit", "hasil", "panen"},
        "channels": ["Food and agricultural commodity supply", "Fertilizer and input costs", "Food security and export policy"],
    },
    "transport_logistics": {
        "label": "Transport & Logistics",
        "keywords": {"port", "ports", "shipping", "freight", "vessel", "canal", "strait", "rail", "airport", "airline", "transport", "suez", "panama", "pelabuhan", "kapal", "angkutan", "kargo", "kanal", "selat", "kereta", "bandara", "maskapai", "transportasi"},
        "channels": ["Maritime chokepoints and port capacity", "Freight and transit disruption", "Transport infrastructure investment"],
    },
}
_TOKEN = re.compile(r"[a-zA-Z0-9À-ÿ]+")


def _labels(value: Any) -> list[str]:
    if isinstance(value, str):
        value = [part.strip() for part in value.split(",")]
    if not isinstance(value, (list, tuple, set)):
        return []
    return list(dict.fromkeys(str(item).strip() for item in value if str(item or "").strip()))


def _safe_score(value: Any) -> float:
    try:
        score = float(value)
    except (TypeError, ValueError):
        return 0.0
    if score != score or score in (float("inf"), float("-inf")):
        return 0.0
    return max(0.0, min(100.0, score))


def analyze_economic_intelligence(signals: Iterable[dict[str, Any]], *, limit: int = 25) -> dict[str, Any]:
    """Classify records into economic sectors and build traceable analyst review cues."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    records = [item for item in signals if isinstance(item, dict)]
    assessments = []
    sector_records: dict[str, list[dict[str, Any]]] = {key: [] for key in _SECTORS}
    country_counts: Counter[str] = Counter()
    for signal in records:
        title = str(signal.get("title") or signal.get("topic") or "").strip()
        if not title:
            continue
        tokens = {token.casefold() for token in _TOKEN.findall(title + " " + str(signal.get("summary") or ""))}
        matched = {}
        for key, spec in _SECTORS.items():
            hits = sorted(tokens & spec["keywords"])
            if hits:
                matched[key] = hits
        if not matched:
            continue
        score = _safe_score(signal.get("score"))
        warning = signal.get("warning") if isinstance(signal.get("warning"), dict) else {}
        evidence = signal.get("evidence") if isinstance(signal.get("evidence"), dict) else {}
        countries = _labels(signal.get("countries")) or _labels(signal.get("country"))
        topics = _labels(signal.get("topics"))
        entities = _labels(signal.get("entities"))
        row = {
            "signal_id": str(signal.get("id") or ""),
            "title": title,
            "source": str(signal.get("source") or "unknown"),
            "url": str(signal.get("url") or ""),
            "score": score,
            "attention_level": "high_attention" if score >= 70 else "moderate_attention" if score >= 40 else "monitor",
            "sectors": sorted(matched),
            "matched_terms": matched,
            "countries_explicitly_named": countries,
            "topics_supplied": topics,
            "entities_explicitly_named": entities,
            "warning_level": str(warning.get("level") or "not_assessed"),
            "evidence_complete": bool(evidence.get("evidence_complete")),
            "review_required": True,
        }
        assessments.append(row)
        for sector in matched:
            sector_records[sector].append(row)
        country_counts.update(countries)
    sector_summaries = []
    for key, spec in _SECTORS.items():
        members = sector_records[key]
        if not members:
            continue
        sector_summaries.append({
            "sector": key,
            "label": spec["label"],
            "signal_count": len(members),
            "average_signal_score": round(sum(item["score"] for item in members) / len(members), 2),
            "high_attention_count": sum(item["attention_level"] == "high_attention" for item in members),
            "countries_named": sorted({country for item in members for country in item["countries_explicitly_named"]}),
            "potential_review_channels": spec["channels"],
            "matched_terms": sorted({term for item in members for terms in item["matched_terms"].values() for term in terms}),
            "signals": sorted(members, key=lambda item: (-item["score"], item["title"].casefold()))[:limit],
        })
    sector_summaries.sort(key=lambda item: (-item["signal_count"], -item["average_signal_score"], item["sector"]))
    assessments.sort(key=lambda item: (-item["score"], item["title"].casefold()))
    return {
        "build": "3.2",
        "signals_assessed": len(assessments),
        "sector_count": len(sector_summaries),
        "sector_summaries": sector_summaries[:limit],
        "country_mentions": [{"country": name, "signal_mentions": count} for name, count in country_counts.most_common(limit)],
        "priority_review_queue": assessments[:limit],
        "coverage": {
            "input_records": len(records),
            "records_classified": len(assessments),
            "records_without_sector_match": max(0, len([item for item in records if str(item.get("title") or item.get("topic") or "").strip()]) - len(assessments)),
        },
        "methodology": {
            "classification": "Curated exact-token English/Indonesian keyword matching against title and summary.",
            "sector_channels": "Potential review channels are prompts for analysts, not observed or quantified market effects.",
            "scores": "Average supplied signal scores are descriptive input scores, not sector performance or financial risk.",
        },
        "limitations": [
            "No live asset prices, exchange rates, yields, company fundamentals, trade statistics, or commodity benchmarks are ingested by this module.",
            "Keyword matches can miss relevant records and produce false positives; terms are discovery cues only.",
            "Country labels and entity names are copied from supplied metadata and are not independently verified.",
            "Sector association does not prove that an event caused a market move or affected a specific company, asset, or economy.",
            "No price forecast, investment recommendation, financial advice, or automated trading signal is produced.",
        ],
        "notice": "Economic intelligence review aid only. Verify primary sources, time period, market data, exposure, and causal mechanism before drawing conclusions.",
    }


def render_economic_intelligence_html(data: dict[str, Any]) -> str:
    """Render escaped economic sector coverage and traceable review records."""
    from html import escape

    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    sectors = data.get("sector_summaries", [])
    sectors = [item for item in sectors if isinstance(item, dict)] if isinstance(sectors, list) else []
    queue = data.get("priority_review_queue", [])
    queue = [item for item in queue if isinstance(item, dict)] if isinstance(queue, list) else []
    cards = "".join(
        f'<article class="metric"><div class="muted">{esc(item.get("label"))}</div><strong>{item.get("signal_count", 0)}</strong>'
        f'<small>Avg supplied score: {item.get("average_signal_score", 0)} · High attention: {item.get("high_attention_count", 0)}</small></article>'
        for item in sectors
    ) or '<p>No economic-sector keyword matches in this report.</p>'
    rows = []
    for item in queue:
        sectors_label = ", ".join(item.get("sectors", []))
        countries = ", ".join(item.get("countries_explicitly_named", [])) or "Not supplied"
        url = str(item.get("url") or "")
        link = f'<a rel="noopener noreferrer" target="_blank" href="{esc(url)}">Open source</a>' if url.startswith(("https://", "http://")) else "Unavailable"
        rows.append(
            f'<tr><td>{esc(item.get("title"))}</td><td>{esc(sectors_label)}</td><td>{esc(countries)}</td>'
            f'<td>{esc(item.get("source"))}</td><td>{item.get("score", 0)}</td><td>{esc(item.get("warning_level"))}</td>'
            f'<td>{esc(item.get("signal_id"))}</td><td>{link}</td></tr>'
        )
    country_rows = "".join(
        f'<tr><td>{esc(item.get("country"))}</td><td class="num">{item.get("signal_mentions", 0)}</td></tr>'
        for item in data.get("country_mentions", []) if isinstance(item, dict)
    ) or '<tr><td colspan="2">No country labels supplied.</td></tr>'
    review_rows = "".join(rows) or '<tr><td colspan="8">No economic review candidates.</td></tr>'
    return (
        '<section class="panel" id="economic-intelligence"><h2>Global Economic Intelligence &amp; Strategic Market Impact · Build 3.2</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Classified signals</div><strong>{data.get("signals_assessed", 0)}</strong><small>Keyword-linked records</small></article>'
        f'<article class="metric"><div class="muted">Sectors represented</div><strong>{data.get("sector_count", 0)}</strong><small>Curated sector taxonomy</small></article>'
        f'<article class="metric"><div class="muted">Records without match</div><strong>{(data.get("coverage") or {}).get("records_without_sector_match", 0)}</strong><small>Not automatically irrelevant</small></article></div>'
        f'<div class="grid">{cards}</div><div class="columns"><div><h3>Country mentions in economic signals</h3>'
        f'<div class="table-wrap"><table><thead><tr><th>Country label</th><th>Signal mentions</th></tr></thead><tbody>{country_rows}</tbody></table></div></div>'
        f'<div><h3>Potential market-review channels</h3><ul>{"".join(f"<li>{esc(channel)}</li>" for item in sectors for channel in item.get("potential_review_channels", []))}</ul></div></div>'
        f'<h3>Traceable economic signal review queue</h3><div class="table-wrap"><table><thead><tr><th>Signal</th><th>Sector cues</th><th>Country</th><th>Source</th><th>Input score</th><th>Warning</th><th>ID</th><th>Article</th></tr></thead><tbody>{review_rows}</tbody></table></div>'
        '<p class="notice">Sector matches are keyword-based review cues. No asset prices, FX rates, yields, fundamentals, or measured market impacts are included. Association is not causation; no forecast or investment recommendation is produced.</p></section>'
    )
