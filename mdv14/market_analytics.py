"""Deterministic cross-asset analytics over observed market-data rows.

Calculations describe the supplied observation window only. They do not infer
missing prices, normalize unlike units, or produce trading recommendations.
"""
from __future__ import annotations

from datetime import date
from html import escape
from math import sqrt
from statistics import pstdev
from typing import Any


def build_market_analytics(*datasets: dict[str, Any]) -> dict[str, Any]:
    """Summarize each observed series independently across supplied providers."""
    grouped: dict[str, list[dict[str, Any]]] = {}
    providers: dict[str, set[str]] = {}
    for dataset in datasets:
        if not isinstance(dataset, dict):
            continue
        rows = dataset.get("observations", [])
        if not isinstance(rows, list):
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            series_id = str(row.get("series_id") or "").strip()
            try:
                observed = date.fromisoformat(str(row.get("date") or ""))
                value = float(row.get("value"))
            except (TypeError, ValueError):
                continue
            if not series_id:
                continue
            normalized = {**row, "date": observed.isoformat(), "value": value}
            grouped.setdefault(series_id, []).append(normalized)
            providers.setdefault(series_id, set()).add(str(row.get("source") or "unknown"))

    summaries = []
    for series_id, rows in sorted(grouped.items()):
        # Duplicate dates from overlapping providers are resolved deterministically:
        # retain the last input row for that date, without blending providers.
        by_date: dict[str, dict[str, Any]] = {}
        for row in rows:
            by_date[row["date"]] = row
        ordered = [by_date[key] for key in sorted(by_date)]
        first, latest = ordered[0], ordered[-1]
        start_value, latest_value = first["value"], latest["value"]
        change = latest_value - start_value
        pct_change = (change / start_value * 100.0) if start_value != 0 else None
        step_returns = []
        for previous, current in zip(ordered, ordered[1:]):
            if previous["value"] != 0:
                step_returns.append((current["value"] / previous["value"] - 1.0) * 100.0)
        volatility = pstdev(step_returns) if len(step_returns) >= 2 else None
        direction = "rising" if change > 0 else "falling" if change < 0 else "unchanged"
        summaries.append({
            "series_id": series_id,
            "series": str(latest.get("series") or first.get("series") or series_id),
            "category": str(latest.get("category") or first.get("category") or "unclassified"),
            "unit": str(latest.get("unit") or first.get("unit") or ""),
            "providers": sorted(providers.get(series_id, {"unknown"})),
            "observation_count": len(ordered),
            "first_date": first["date"],
            "latest_date": latest["date"],
            "first_value": start_value,
            "latest_value": latest_value,
            "absolute_change": change,
            "percentage_change": pct_change,
            "direction": direction,
            "observed_step_volatility_pct": volatility,
            "volatility_observations": len(step_returns),
            "status": "evaluated",
        })
    return {
        "build": "3.5",
        "status": "available" if summaries else "no_data",
        "series_analyzed": len(summaries),
        "observations_analyzed": sum(item["observation_count"] for item in summaries),
        "summaries": summaries,
        "method": "Per-series first-to-latest change; population standard deviation of observed-step percentage changes when at least two steps exist.",
        "limitations": [
            "Each series is analyzed independently; unlike units and asset classes are not combined into a single score.",
            "Percentage change is omitted when the first observed value is zero.",
            "Volatility is descriptive dispersion across available observation steps, not annualized volatility; irregular dates and market closures are not adjusted.",
            "Only returned observations are analyzed. Missing dates are not interpolated or treated as zero.",
            "Direction and volatility are retrospective descriptors, not trading signals, investment advice, causal findings, or forecasts.",
        ],
    }


def render_market_analytics_html(data: dict[str, Any]) -> str:
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    rows = []
    summaries = data.get("summaries", [])
    if isinstance(summaries, list):
        for item in summaries:
            if not isinstance(item, dict):
                continue
            pct = item.get("percentage_change")
            volatility = item.get("observed_step_volatility_pct")
            rows.append(
                f"<tr><td>{esc(item.get('series'))} <small>({esc(item.get('series_id'))})</small></td>"
                f"<td>{esc(item.get('category'))}</td><td>{esc(item.get('first_date'))} → {esc(item.get('latest_date'))}</td>"
                f"<td class='num'>{esc(item.get('first_value'))} → {esc(item.get('latest_value'))}</td>"
                f"<td class='num'>{esc(item.get('absolute_change'))} {esc(item.get('unit'))}</td>"
                f"<td class='num'>{esc(f'{pct:.3f}%' if isinstance(pct, (int, float)) else 'not available')}</td>"
                f"<td>{esc(item.get('direction'))}</td>"
                f"<td class='num'>{esc(f'{volatility:.3f}%' if isinstance(volatility, (int, float)) else 'insufficient observations')}</td></tr>"
            )
    body = "".join(rows) or "<tr><td colspan='8'>No valid market series available for analytics.</td></tr>"
    limitations = data.get("limitations", [])
    notes = " ".join(esc(item) for item in limitations if isinstance(item, str))
    return (
        '<section class="panel" id="market-analytics"><h2>Cross-Asset Market Analytics · Build 3.5</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Series analyzed</div><strong>{esc(data.get("series_analyzed", 0))}</strong><small>Independent series</small></article>'
        f'<article class="metric"><div class="muted">Observations analyzed</div><strong>{esc(data.get("observations_analyzed", 0))}</strong><small>Valid dated values</small></article>'
        f'<article class="metric"><div class="muted">Status</div><strong>{esc(data.get("status", "unknown"))}</strong><small>Observed data only</small></article></div>'
        '<div class="table-wrap"><table><thead><tr><th>Series</th><th>Class</th><th>Observed window</th><th>First → latest</th><th>Absolute change</th><th>Change %</th><th>Direction</th><th>Observed-step volatility</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div>'
        f'<p class="muted">{esc(data.get("method", ""))} {notes}</p>'
        '<p class="notice">Retrospective descriptive analytics only. Volatility is not annualized; no cross-asset composite score, trading signal, forecast, or investment recommendation is generated.</p></section>'
    )
