"""Optional FRED financial-market observations for MD V14.

Uses the official FRED observations API and a fixed series allowlist. Values are
historical observations, not executable quotes, investment advice, or forecasts.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
from datetime import date
from html import escape
from typing import Any

API_HOST = "api.stlouisfed.org"
BASE_URL = "https://api.stlouisfed.org/fred/series/observations"
TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 2_000_000
SERIES = {
    "DEXIDUS": {"name": "Indonesian Rupiah to U.S. Dollar", "category": "foreign_exchange", "unit": "IDR per USD", "frequency": "daily"},
    "DEXUSEU": {"name": "U.S. Dollar to Euro", "category": "foreign_exchange", "unit": "USD per EUR", "frequency": "daily"},
    "DEXCHUS": {"name": "Chinese Yuan to U.S. Dollar", "category": "foreign_exchange", "unit": "CNY per USD", "frequency": "daily"},
    "SP500": {"name": "S&P 500", "category": "equity_index", "unit": "index points", "frequency": "daily"},
    "NASDAQCOM": {"name": "NASDAQ Composite", "category": "equity_index", "unit": "index points", "frequency": "daily"},
    "DGS10": {"name": "10-Year Treasury Constant Maturity Rate", "category": "government_bonds", "unit": "percent", "frequency": "daily"},
    "DCOILWTICO": {"name": "WTI Crude Oil Price", "category": "commodities", "unit": "USD per barrel", "frequency": "daily"},
    "GOLDPMGBD228NLBM": {"name": "Gold Price, London Bullion Market", "category": "commodities", "unit": "USD per troy ounce", "frequency": "daily"},
}
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _fetch_fred(url: str, timeout: int = TIMEOUT_SECONDS) -> Any:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != API_HOST or parsed.path != "/fred/series/observations":
        raise ValueError("only the official FRED observations endpoint is allowed")
    request = urllib.request.Request(
        url, headers={"User-Agent": "MDV14-MarketData/1.0", "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("FRED response exceeds size limit")
    return json.loads(body.decode("utf-8"))


def fetch_fred_market_data(
    api_key: str | None,
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    series_ids: list[str] | None = None,
    timeout: int = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch allowlisted FRED observations; never include API key in returned URLs."""
    selected = list(SERIES) if series_ids is None else list(dict.fromkeys(series_ids))
    if not selected or any(item not in SERIES for item in selected):
        raise ValueError("series_ids must use the configured FRED series allowlist")
    if timeout < 1:
        raise ValueError("timeout must be positive")
    start = start_date or "2020-01-01"
    end = end_date or date.today().isoformat()
    for value in (start, end):
        if not _DATE.fullmatch(value):
            raise ValueError("dates must use YYYY-MM-DD")
        date.fromisoformat(value)
    if start > end:
        raise ValueError("start_date must not be after end_date")
    if not api_key or not api_key.strip():
        return {
            "build": "3.4", "provider": "Federal Reserve Bank of St. Louis FRED",
            "status": "not_configured", "series_requested": selected,
            "request_count": 0, "requests_succeeded": 0, "requests_failed": 0,
            "observation_count": 0, "observations": [], "request_status": [],
            "errors": [], "limitations": [
                "Set FRED_API_KEY in the environment or GitHub Actions secret to enable this optional provider.",
                "No market observations were fetched because no API key was configured.",
            ],
        }
    observations: list[dict[str, Any]] = []
    request_status: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for series_id in selected:
        params = urllib.parse.urlencode({
            "series_id": series_id, "api_key": api_key.strip(),
            "file_type": "json", "observation_start": start, "observation_end": end,
            "sort_order": "asc",
        })
        url = f"{BASE_URL}?{params}"
        try:
            payload = _fetch_fred(url, timeout=timeout)
            if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
                raise ValueError("unexpected FRED API response structure")
            count = 0
            for row in payload["observations"]:
                if not isinstance(row, dict) or row.get("value") in (None, "", "."):
                    continue
                try:
                    value = float(row["value"])
                    date.fromisoformat(str(row.get("date", "")))
                except (TypeError, ValueError):
                    continue
                observations.append({
                    "series_id": series_id, "series": SERIES[series_id]["name"],
                    "category": SERIES[series_id]["category"], "date": row["date"],
                    "value": value, "unit": SERIES[series_id]["unit"],
                    "frequency": SERIES[series_id]["frequency"],
                    "source": "FRED", "source_url": f"https://fred.stlouisfed.org/series/{series_id}",
                    "retrieved_at": date.today().isoformat(),
                })
                count += 1
            request_status.append({"series_id": series_id, "status": "ok", "observations_received": count})
        except Exception as exc:
            # Provider errors are isolated per series; credentials are never copied into errors.
            message = str(exc).replace(api_key.strip(), "[REDACTED]")
            errors.append({"series_id": series_id, "error": message[:500], "status": "unavailable"})
            request_status.append({"series_id": series_id, "status": "unavailable", "observations_received": 0})
    observations.sort(key=lambda item: (item["series_id"], item["date"]))
    return {
        "build": "3.4", "provider": "Federal Reserve Bank of St. Louis FRED",
        "provider_url": "https://fred.stlouisfed.org", "status": "available",
        "date_range": {"start": start, "end": end}, "series_requested": selected,
        "request_count": len(request_status),
        "requests_succeeded": sum(x["status"] == "ok" for x in request_status),
        "requests_failed": len(errors), "observation_count": len(observations),
        "observations": observations, "request_status": request_status, "errors": errors,
        "limitations": [
            "FRED series are published observations and may be delayed, revised, or subject to holidays and missing dates.",
            "These series are not guaranteed executable or real-time quotes; units and conventions differ by series.",
            "FX series labels and quote conventions must be checked before comparing or calculating returns.",
            "No trading signals, investment recommendations, causal claims, or forecasts are produced.",
        ],
    }


def render_fred_html(data: dict[str, Any]) -> str:
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    observations = data.get("observations", [])
    observations = [x for x in observations if isinstance(x, dict)] if isinstance(observations, list) else []
    rows = "".join(
        f'<tr><td>{esc(x.get("series"))}</td><td>{esc(x.get("date"))}</td>'
        f'<td class="num">{esc(x.get("value"))}</td><td>{esc(x.get("unit"))}</td>'
        f'<td>{esc(x.get("frequency"))}</td></tr>' for x in observations
    ) or '<tr><td colspan="5">No FRED observations available for this run.</td></tr>'
    errors = data.get("errors", [])
    error_text = "; ".join(
        f'{esc(x.get("series_id"))}: {esc(x.get("error"))}' for x in errors if isinstance(x, dict)
    ) or ("Provider not configured." if data.get("status") == "not_configured" else "No request errors reported.")
    return (
        '<section class="panel" id="fred-market-data"><h2>Global Financial Markets · FRED · Build 3.4</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Observations</div><strong>{data.get("observation_count", 0)}</strong><small>Published non-null values</small></article>'
        f'<article class="metric"><div class="muted">Requests succeeded</div><strong>{data.get("requests_succeeded", 0)}</strong><small>Series requests</small></article>'
        f'<article class="metric"><div class="muted">Requests unavailable</div><strong>{data.get("requests_failed", 0)}</strong><small>Not configured or failed requests remain visible</small></article></div>'
        f'<div class="table-wrap"><table><thead><tr><th>Series</th><th>Date</th><th>Value</th><th>Unit</th><th>Frequency</th></tr></thead><tbody>{rows}</tbody></table></div>'
        f'<p class="muted">Provider: <a href="https://fred.stlouisfed.org" rel="noopener noreferrer" target="_blank">FRED</a>. Status: {esc(data.get("status", "unknown"))}. Notes: {error_text}</p>'
        '<p class="notice"><strong>This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis.</strong></p>'
        '<p class="notice">Historical published observations, not guaranteed real-time or executable quotes. No trading signals, investment advice, or forecasts. Verify series definitions, units, release dates, and quote conventions before analysis.</p>'
        '<p class="muted">Use of FRED data is subject to the <a href="https://fred.stlouisfed.org/docs/api/terms_of_use.html" rel="noopener noreferrer" target="_blank">FRED API Terms of Use</a>.</p></section>'
    )
