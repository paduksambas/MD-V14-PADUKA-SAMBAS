"""No-key public daily equity-index and commodity observations from Stooq CSV."""
from __future__ import annotations

import csv
import io
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

STOOQ_HOST = "stooq.com"
STOOQ_URL = "https://stooq.com/q/d/l/"
TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 2_000_000
ASSET_SERIES = {
    "^spx": {"name": "S&P 500 Index", "category": "equity_index", "unit": "index points"},
    "^ndq": {"name": "NASDAQ Composite Index", "category": "equity_index", "unit": "index points"},
    "^dax": {"name": "DAX Index", "category": "equity_index", "unit": "index points"},
    "^nkx": {"name": "Nikkei 225 Index", "category": "equity_index", "unit": "index points"},
    "cl.f": {"name": "WTI Crude Oil Futures", "category": "commodities", "unit": "USD per barrel"},
    "gc.f": {"name": "Gold Futures", "category": "commodities", "unit": "USD per troy ounce"},
}


def _fetch_stooq(url: str, timeout: int = TIMEOUT_SECONDS) -> str:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != STOOQ_HOST or parsed.path != "/q/d/l/":
        raise ValueError("only the Stooq daily CSV endpoint is allowed")
    request = urllib.request.Request(
        url, headers={"User-Agent": "MDV14-PublicAssets/1.0", "Accept": "text/csv"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("Stooq response exceeds size limit")
    return body.decode("utf-8-sig")


def fetch_public_asset_data(
    *, start_date: str | None = None, end_date: str | None = None,
    symbols: list[str] | None = None, timeout: int = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch allowlisted daily close observations; no API key or account required."""
    selected = list(ASSET_SERIES) if symbols is None else list(dict.fromkeys(symbols))
    if not selected or any(symbol not in ASSET_SERIES for symbol in selected):
        raise ValueError("symbols must use the configured public-asset allowlist")
    if timeout < 1:
        raise ValueError("timeout must be positive")
    end = end_date or date.today().isoformat()
    start = start_date or end
    for value in (start, end):
        if len(value) != 10:
            raise ValueError("dates must use YYYY-MM-DD")
        date.fromisoformat(value)
    if start > end:
        raise ValueError("start_date must not be after end_date")
    if (date.fromisoformat(end) - date.fromisoformat(start)).days > 366:
        raise ValueError("public asset date range must not exceed 367 calendar days")

    observations: list[dict[str, Any]] = []
    request_status: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    for symbol in selected:
        params = urllib.parse.urlencode({
            "s": symbol, "d1": start.replace("-", ""),
            "d2": end.replace("-", ""), "i": "d",
        })
        url = f"{STOOQ_URL}?{params}"
        try:
            payload = _fetch_stooq(url, timeout=timeout)
            reader = csv.DictReader(io.StringIO(payload))
            if not reader.fieldnames or not {"Date", "Close"}.issubset(reader.fieldnames):
                raise ValueError("unexpected Stooq CSV columns")
            count = 0
            for row in reader:
                try:
                    observed = date.fromisoformat(str(row.get("Date", "")))
                    value = float(row.get("Close", ""))
                except (TypeError, ValueError):
                    continue
                if not (date.fromisoformat(start) <= observed <= date.fromisoformat(end)):
                    continue
                meta = ASSET_SERIES[symbol]
                observations.append({
                    "series_id": f"STOOQ:{symbol}",
                    "series": meta["name"], "category": meta["category"],
                    "date": observed.isoformat(), "value": value, "unit": meta["unit"],
                    "frequency": "daily close", "source": "Stooq",
                    "source_url": f"https://stooq.com/q/?s={urllib.parse.quote(symbol, safe='')}",
                    "retrieved_at": date.today().isoformat(),
                })
                count += 1
            request_status.append({"symbol": symbol, "status": "ok", "observations_received": count})
        except Exception as exc:
            errors.append({"symbol": symbol, "error": str(exc)[:500], "status": "unavailable"})
            request_status.append({"symbol": symbol, "status": "unavailable", "observations_received": 0})

    observations.sort(key=lambda item: (item["series_id"], item["date"]))
    succeeded = sum(item["status"] == "ok" for item in request_status)
    return {
        "build": "3.6", "provider": "Stooq public daily CSV",
        "provider_url": "https://stooq.com/", "status": (
            "available" if observations else "unavailable" if errors else "no_data"
        ),
        "date_range": {"start": start, "end": end}, "symbols_requested": selected,
        "request_count": len(request_status), "requests_succeeded": succeeded,
        "requests_failed": len(errors), "observation_count": len(observations),
        "observations": observations, "request_status": request_status, "errors": errors,
        "limitations": [
            "No API key or account is required; data availability and symbol coverage depend on Stooq.",
            "Values are provider-supplied daily close observations, not guaranteed real-time or executable quotes.",
            "Equity indices are reported in index points; futures contracts use provider quote conventions and may be affected by contract rolls.",
            "The configured public universe covers four equity indices and two commodity futures; government-bond yields are not included in this no-key adapter.",
            "Market holidays, publication delays, revisions, symbol changes, and missing dates may affect coverage.",
            "No trading signals, investment advice, causal claims, or forecasts are produced.",
        ],
    }


def render_public_asset_html(data: dict[str, Any]) -> str:
    from html import escape

    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    rows = data.get("observations", [])
    rows = [item for item in rows if isinstance(item, dict)] if isinstance(rows, list) else []
    body = "".join(
        f"<tr><td>{esc(item.get('series'))}</td><td>{esc(item.get('date'))}</td>"
        f"<td class='num'>{esc(item.get('value'))}</td><td>{esc(item.get('unit'))}</td>"
        f"<td>{esc(item.get('source'))}</td></tr>" for item in rows
    ) or "<tr><td colspan='5'>No public equity or commodity observations available.</td></tr>"
    errors = data.get("errors", [])
    notes = "; ".join(esc(item.get("symbol")) + ": " + esc(item.get("error"))
                      for item in errors if isinstance(item, dict)) or "No request errors reported."
    return (
        '<section class="panel" id="public-asset-data"><h2>Public Equity &amp; Commodity Data · No API Key</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Observations</div><strong>{esc(data.get("observation_count", 0))}</strong><small>Daily closes</small></article>'
        f'<article class="metric"><div class="muted">Requests succeeded</div><strong>{esc(data.get("requests_succeeded", 0))}</strong><small>Allowlisted symbols</small></article>'
        f'<article class="metric"><div class="muted">Requests failed</div><strong>{esc(data.get("requests_failed", 0))}</strong><small>Provider availability</small></article></div>'
        f'<div class="table-wrap"><table><thead><tr><th>Instrument</th><th>Date</th><th>Close</th><th>Unit</th><th>Source</th></tr></thead><tbody>{body}</tbody></table></div>'
        f'<p class="muted">Provider: <a href="https://stooq.com/" rel="noopener noreferrer" target="_blank">Stooq</a>. Status: {esc(data.get("status", "unknown"))}. {notes}</p>'
        '<p class="notice">Daily close history, not live executable prices. Futures may be affected by contract-roll conventions. No government-bond series in this adapter; no trading advice or forecasts.</p></section>'
    )
