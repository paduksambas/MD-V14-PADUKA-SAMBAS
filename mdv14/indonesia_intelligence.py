"""Indonesia-focused strategic economic context from official observations.

This module organizes published World Bank indicators and global benchmark prices.
It does not estimate exposure elasticities, infer causality, or make forecasts.
"""
from __future__ import annotations

from html import escape
from typing import Any

INDONESIA_INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": ("GDP growth", "macroeconomy", "annual %"),
    "FP.CPI.TOTL.ZG": ("Consumer inflation", "prices", "annual %"),
    "NE.TRD.GNFS.ZS": ("Trade openness", "external", "% of GDP"),
    "TX.VAL.MRCH.CD.WT": ("Merchandise exports", "external", "current US$"),
    "TM.VAL.MRCH.CD.WT": ("Merchandise imports", "external", "current US$"),
    "NV.AGR.TOTL.ZS": ("Agriculture value added", "real_economy", "% of GDP"),
    "NV.IND.TOTL.ZS": ("Industry value added", "real_economy", "% of GDP"),
    "NV.SRV.TOTL.ZS": ("Services value added", "real_economy", "% of GDP"),
    "SL.UEM.TOTL.ZS": ("Unemployment", "labor", "% of labor force"),
    "BX.KLT.DINV.WD.GD.ZS": ("FDI net inflows", "external", "% of GDP"),
    "FI.RES.TOTL.CD": ("Total reserves", "external", "current US$"),
    "BN.CAB.XOKA.GD.ZS": ("Current account balance", "external", "% of GDP"),
}

COMMODITY_CHANNELS = {
    "energy": {
        "label": "Energi dan biaya produksi",
        "channels": ["Biaya impor energi dan subsidi", "Biaya transportasi dan input industri"],
        "series": ["WB:CRUDE_BRENT", "WB:CRUDE_WTI", "WB:CRUDE_AVERAGE",
                   "WB:NATURAL_GAS_US", "WB:COAL_AUSTRALIA"],
    },
    "agriculture": {
        "label": "Pangan dan perkebunan",
        "channels": ["Biaya input pangan dan volatilitas harga acuan", "Peluang pendapatan ekspor komoditas pertanian"],
        "series": ["WB:COFFEE_ARABICA", "WB:COFFEE_ROBUSTA", "WB:PALM_OIL",
                   "WB:WHEAT_HRW", "WB:MAIZE", "WB:RICE_THAI_5"],
    },
    "metals": {
        "label": "Logam dan manufaktur",
        "channels": ["Biaya bahan baku manufaktur dan konstruksi", "Harga acuan logam untuk rantai pasok industri"],
        "series": ["WB:COPPER", "WB:ALUMINUM"],
    },
    "precious_metals": {
        "label": "Logam mulia",
        "channels": ["Harga acuan ekspor dan nilai persediaan emas", "Perubahan harga benchmark global"],
        "series": ["WB:GOLD", "WB:SILVER"],
    },
    "fertilizers": {
        "label": "Pupuk dan pertanian",
        "channels": ["Biaya input pertanian dan ketahanan pasokan pupuk"],
        "series": ["WB:UREA"],
    },
}


def build_indonesia_economic_intelligence(
    economic_data: dict[str, Any] | None,
    commodity_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Build a traceable Indonesia indicator panel and qualitative price channels."""
    economic_data = economic_data if isinstance(economic_data, dict) else {}
    commodity_data = commodity_data if isinstance(commodity_data, dict) else {}
    raw = economic_data.get("observations", [])
    rows = [item for item in raw if isinstance(item, dict) and item.get("country_code") == "ID"] if isinstance(raw, list) else []
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        code = str(row.get("indicator_code") or "")
        if code not in INDONESIA_INDICATORS:
            continue
        try:
            year = int(str(row.get("year")))
            value = float(row.get("value"))
        except (TypeError, ValueError):
            continue
        grouped.setdefault(code, []).append({**row, "year": year, "value": value})

    indicator_summaries = []
    for code, observations in sorted(grouped.items()):
        ordered = sorted(observations, key=lambda item: item["year"])
        first, latest = ordered[0], ordered[-1]
        label, domain, unit = INDONESIA_INDICATORS[code]
        change = latest["value"] - first["value"]
        indicator_summaries.append({
            "indicator_code": code, "indicator": label, "domain": domain,
            "first_year": first["year"], "latest_year": latest["year"],
            "first_value": first["value"], "latest_value": latest["value"],
            "change": change, "unit": str(latest.get("unit") or unit),
            "observation_count": len(ordered),
            "direction": "rising" if change > 0 else "falling" if change < 0 else "unchanged",
            "source": "World Bank Indicators API",
            "source_url": str(latest.get("source_url") or "https://api.worldbank.org/v2"),
        })

    raw_commodities = commodity_data.get("observations", [])
    commodity_rows = [item for item in raw_commodities if isinstance(item, dict)] if isinstance(raw_commodities, list) else []
    commodity_ids = {str(item.get("series_id")) for item in commodity_rows}
    commodity_context = []
    for category, config in COMMODITY_CHANNELS.items():
        matching = [item for item in commodity_rows if item.get("series_id") in config["series"]]
        if not matching:
            continue
        latest_by_series: dict[str, dict[str, Any]] = {}
        for item in matching:
            series_id = str(item.get("series_id"))
            try:
                year_month = str(item.get("date") or "")
                value = float(item.get("value"))
            except (TypeError, ValueError):
                continue
            if len(year_month) != 10:
                continue
            previous = latest_by_series.get(series_id)
            if previous is None or year_month > previous["date"]:
                latest_by_series[series_id] = {**item, "value": value}
        commodity_context.append({
            "category": category, "label": config["label"],
            "channels": config["channels"],
            "benchmark_series": [{
                "series_id": key, "series": value.get("series", key),
                "date": value.get("date"), "value": value["value"],
                "unit": value.get("unit", ""),
                "source_url": value.get("source_url", ""),
            } for key, value in sorted(latest_by_series.items())],
            "benchmark_count": len(latest_by_series),
            "interpretation": "Qualitative monitoring channel only; not a measured Indonesia exposure or causal effect.",
        })

    return {
        "build": "3.8",
        "status": "available" if indicator_summaries or commodity_context else "no_data",
        "country": "Indonesia", "country_code": "ID",
        "indicator_count": len(indicator_summaries),
        "indicators": indicator_summaries,
        "commodity_channel_count": len(commodity_context),
        "commodity_channels": commodity_context,
        "coverage": {
            "world_bank_indonesia_observations": len(rows),
            "recognized_indicator_observations": sum(item["observation_count"] for item in indicator_summaries),
            "global_commodity_observations_received": len(commodity_rows),
            "commodity_series_available": len(commodity_ids),
        },
        "sources": [
            {"name": "World Bank Indicators API", "url": "https://api.worldbank.org/v2"},
            {"name": "World Bank Commodity Markets (Pink Sheet)", "url": "https://www.worldbank.org/en/research/commodity-markets"},
        ],
        "limitations": [
            "Only official World Bank historical observations are used; latest year differs by indicator and missing values are not zero.",
            "Commodity benchmarks are global monthly prices, not Indonesian transaction prices, local inflation pass-through, or measured trade exposure.",
            "Qualitative channels are analyst review prompts; this module does not calculate exposure elasticities or attribute causes.",
            "No forecasts, risk probabilities, policy recommendations, or investment advice are produced.",
            "World Bank series definitions and revisions apply; consult source metadata before comparing values.",
        ],
    }


def render_indonesia_economic_html(data: dict[str, Any]) -> str:
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    indicators = data.get("indicators", [])
    rows = []
    for item in indicators if isinstance(indicators, list) else []:
        if not isinstance(item, dict):
            continue
        rows.append(
            f"<tr><td>{esc(item.get('indicator'))}</td><td>{esc(item.get('domain'))}</td>"
            f"<td>{esc(item.get('first_year'))}–{esc(item.get('latest_year'))}</td>"
            f"<td class='num'>{esc(item.get('first_value'))} → {esc(item.get('latest_value'))}</td>"
            f"<td class='num'>{esc(item.get('change'))}</td><td>{esc(item.get('unit'))}</td>"
            f"<td>{esc(item.get('direction'))}</td></tr>"
        )
    indicator_body = "".join(rows) or "<tr><td colspan='7'>No Indonesia-specific macroeconomic observations available.</td></tr>"
    channel_sections = []
    for item in data.get("commodity_channels", []) if isinstance(data.get("commodity_channels"), list) else []:
        if not isinstance(item, dict):
            continue
        benchmark_rows = "".join(
            f"<li>{esc(row.get('series'))}: {esc(row.get('value'))} {esc(row.get('unit'))} ({esc(row.get('date'))})</li>"
            for row in item.get("benchmark_series", []) if isinstance(row, dict)
        ) or "<li>No benchmark series received.</li>"
        channel_sections.append(
            f"<article class='metric'><strong>{esc(item.get('label'))}</strong>"
            f"<ul>{''.join('<li>'+esc(channel)+'</li>' for channel in item.get('channels', []))}</ul>"
            f"<small>Latest global benchmark observations:</small><ul>{benchmark_rows}</ul>"
            f"<small>{esc(item.get('interpretation'))}</small></article>"
        )
    channels_html = "".join(channel_sections) or "<p>No mapped commodity benchmark channels available.</p>"
    coverage = data.get("coverage") if isinstance(data.get("coverage"), dict) else {}
    return (
        '<section class="panel" id="indonesia-economic-intelligence"><h2>Indonesia Strategic Economic Intelligence · Build 3.8</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Indonesia indicators</div><strong>{esc(data.get("indicator_count", 0))}</strong><small>Published historical series</small></article>'
        f'<article class="metric"><div class="muted">Commodity channels</div><strong>{esc(data.get("commodity_channel_count", 0))}</strong><small>Qualitative review links</small></article>'
        f'<article class="metric"><div class="muted">Indonesia observations</div><strong>{esc(coverage.get("recognized_indicator_observations", 0))}</strong><small>World Bank non-null values</small></article></div>'
        f'<h3>Macroeconomic indicators</h3><div class="table-wrap"><table><thead><tr><th>Indicator</th><th>Domain</th><th>Years</th><th>First → latest</th><th>Change</th><th>Unit</th><th>Direction</th></tr></thead><tbody>{indicator_body}</tbody></table></div>'
        f'<h3>Global commodity channels relevant for analyst review</h3><div class="grid">{channels_html}</div>'
        '<p class="muted">Official data: <a href="https://api.worldbank.org/v2" rel="noopener noreferrer" target="_blank">World Bank Indicators API</a> and <a href="https://www.worldbank.org/en/research/commodity-markets" rel="noopener noreferrer" target="_blank">Pink Sheet</a>.</p>'
        '<p class="notice">Global commodity prices are not Indonesia-specific prices. Channel mappings are qualitative prompts, not quantified exposure, pass-through, causal effects, forecasts, or policy advice. Latest data years and revisions vary by series.</p></section>'
    )
