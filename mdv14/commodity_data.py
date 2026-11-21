"""Official World Bank Pink Sheet monthly commodity observations.

The workbook URL is discovered from the World Bank commodity-markets landing page
because its release directory changes. XLSX parsing uses only the Python standard
library; no API key or third-party package is required.
"""
from __future__ import annotations

import json
import re
import urllib.parse
import urllib.request
import zipfile
import io
import xml.etree.ElementTree as ET
from datetime import date
from html import escape
from html.parser import HTMLParser
from typing import Any

LANDING_URL = "https://www.worldbank.org/en/research/commodity-markets"
LANDING_HOSTS = {"www.worldbank.org", "worldbank.org"}
WORKBOOK_HOST = "thedocs.worldbank.org"
TIMEOUT_SECONDS = 20
MAX_HTML_BYTES = 3_000_000
MAX_WORKBOOK_BYTES = 20_000_000
MAX_DATE_RANGE_MONTHS = 120
SHEET_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
REL_NS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
PKG_REL_NS = "{http://schemas.openxmlformats.org/package/2006/relationships}"
PERIOD_RE = re.compile(r"^(\d{4})M(\d{1,2})$", re.I)
COMMODITIES = {
    "Crude oil, Brent": {"id": "WB:CRUDE_BRENT", "category": "energy", "unit_hint": "USD per barrel"},
    "Crude oil, WTI": {"id": "WB:CRUDE_WTI", "category": "energy", "unit_hint": "USD per barrel"},
    "Crude oil, average": {"id": "WB:CRUDE_AVERAGE", "category": "energy", "unit_hint": "USD per barrel"},
    "Natural gas, U.S.": {"id": "WB:NATURAL_GAS_US", "category": "energy", "unit_hint": "USD per MMBtu"},
    "Coal, Australia": {"id": "WB:COAL_AUSTRALIA", "category": "energy", "unit_hint": "USD per metric ton"},
    "Gold": {"id": "WB:GOLD", "category": "precious_metals", "unit_hint": "USD per troy ounce"},
    "Silver": {"id": "WB:SILVER", "category": "precious_metals", "unit_hint": "USD per troy ounce"},
    "Copper": {"id": "WB:COPPER", "category": "metals", "unit_hint": "USD per metric ton"},
    "Aluminum": {"id": "WB:ALUMINUM", "category": "metals", "unit_hint": "USD per metric ton"},
    "Coffee, Arabica": {"id": "WB:COFFEE_ARABICA", "category": "agriculture", "unit_hint": "USD per kg"},
    "Coffee, Robusta": {"id": "WB:COFFEE_ROBUSTA", "category": "agriculture", "unit_hint": "USD per kg"},
    "Palm oil": {"id": "WB:PALM_OIL", "category": "agriculture", "unit_hint": "USD per metric ton"},
    "Wheat, U.S. HRW": {"id": "WB:WHEAT_HRW", "category": "agriculture", "unit_hint": "USD per metric ton"},
    "Maize": {"id": "WB:MAIZE", "category": "agriculture", "unit_hint": "USD per metric ton"},
    "Rice, Thai 5%": {"id": "WB:RICE_THAI_5", "category": "agriculture", "unit_hint": "USD per metric ton"},
    "Urea": {"id": "WB:UREA", "category": "fertilizers", "unit_hint": "USD per metric ton"},
}


class _WorkbookLinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        href = dict(attrs).get("href")
        if href and "CMO-Historical-Data-Monthly.xlsx" in href:
            self.links.append(href)


def _read_url(url: str, *, allowed_hosts: set[str], max_bytes: int, timeout: int) -> tuple[bytes, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in allowed_hosts:
        raise ValueError("only allowlisted World Bank HTTPS hosts are permitted")
    request = urllib.request.Request(
        url, headers={"User-Agent": "MDV14-WorldBankCommodities/1.0", "Accept": "*/*"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        final = urllib.parse.urlparse(response.geturl())
        if final.scheme != "https" or final.hostname not in allowed_hosts:
            raise ValueError("World Bank download redirected outside the allowlist")
        body = response.read(max_bytes + 1)
    if len(body) > max_bytes:
        raise ValueError("World Bank response exceeds size limit")
    return body, response.geturl()


def discover_monthly_workbook_url(*, timeout: int = TIMEOUT_SECONDS) -> str:
    body, _ = _read_url(
        LANDING_URL, allowed_hosts=LANDING_HOSTS, max_bytes=MAX_HTML_BYTES, timeout=timeout
    )
    parser = _WorkbookLinkParser()
    parser.feed(body.decode("utf-8", errors="replace"))
    for href in parser.links:
        absolute = urllib.parse.urljoin(LANDING_URL, href)
        parsed = urllib.parse.urlparse(absolute)
        if (parsed.scheme == "https" and parsed.hostname == WORKBOOK_HOST
                and parsed.path.endswith("/related/CMO-Historical-Data-Monthly.xlsx")):
            return absolute
    raise ValueError("current monthly Pink Sheet workbook link was not found on the World Bank page")


def _column_index(reference: str) -> int:
    letters = re.match(r"[A-Z]+", reference.upper())
    if not letters:
        return 0
    value = 0
    for char in letters.group(0):
        value = value * 26 + ord(char) - 64
    return value


def _cell_value(cell: ET.Element, shared: list[str]) -> str:
    kind = cell.attrib.get("t")
    value = cell.find(f"{SHEET_NS}v")
    if kind == "s" and value is not None:
        try:
            return shared[int(value.text or "")]
        except (ValueError, IndexError):
            return ""
    if kind == "inlineStr":
        return "".join(node.text or "" for node in cell.iter(f"{SHEET_NS}t"))
    return (value.text or "") if value is not None else ""


def _parse_workbook(payload: bytes, *, start_date: str | None, end_date: str | None) -> list[dict[str, Any]]:
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        names = set(archive.namelist())
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        targets = {
            item.attrib["Id"]: item.attrib["Target"]
            for item in rels.findall(f"{PKG_REL_NS}Relationship")
        }
        sheet_path = None
        for sheet in workbook.findall(f".//{SHEET_NS}sheet"):
            if sheet.attrib.get("name") == "Monthly Prices":
                target = targets.get(sheet.attrib.get(REL_NS + "id", ""))
                if target:
                    sheet_path = target.lstrip("/")
                    if not sheet_path.startswith("xl/"):
                        sheet_path = "xl/" + sheet_path
                break
        if not sheet_path or sheet_path not in names:
            raise ValueError("Monthly Prices worksheet was not found in the workbook")
        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = ["".join(node.text or "" for node in item.iter(f"{SHEET_NS}t"))
                      for item in root.findall(f"{SHEET_NS}si")]
        root = ET.fromstring(archive.read(sheet_path))
        rows = root.findall(f".//{SHEET_NS}sheetData/{SHEET_NS}row")

    grid: list[list[str]] = []
    for row in rows:
        values: list[str] = []
        for cell in row.findall(f"{SHEET_NS}c"):
            index = _column_index(cell.attrib.get("r", ""))
            if index <= 0:
                continue
            while len(values) < index:
                values.append("")
            values[index - 1] = _cell_value(cell, shared)
        grid.append(values)

    header_index = None
    for index, row in enumerate(grid):
        normalized = [value.strip().casefold() for value in row]
        if normalized and normalized[0] in {"period", "month", "date"} and any(
            name.casefold() in normalized for name in COMMODITIES
        ):
            header_index = index
            break
    if header_index is None:
        raise ValueError("could not identify the Pink Sheet monthly price header row")
    header = grid[header_index]
    unit_row = grid[header_index + 1] if header_index + 1 < len(grid) else []
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    observations: list[dict[str, Any]] = []
    for row in grid[header_index + 2:]:
        if not row:
            continue
        period = row[0].strip().upper()
        match = PERIOD_RE.fullmatch(period)
        if not match:
            continue
        year, month = int(match.group(1)), int(match.group(2))
        if not 1 <= month <= 12:
            continue
        observed = date(year, month, 1)
        if start and observed < date(start.year, start.month, 1):
            continue
        if end and observed > date(end.year, end.month, 1):
            continue
        for column, label in enumerate(header[1:], start=1):
            meta = COMMODITIES.get(label.strip())
            if not meta or column >= len(row):
                continue
            raw = row[column].strip()
            if not raw or raw in {"...", "—", "-"}:
                continue
            try:
                value = float(raw.replace(",", ""))
            except ValueError:
                continue
            unit = unit_row[column].strip() if column < len(unit_row) and unit_row[column].strip() else meta["unit_hint"]
            observations.append({
                "series_id": meta["id"], "series": label.strip(),
                "category": meta["category"], "date": observed.isoformat(),
                "value": value, "unit": unit, "frequency": "monthly average",
                "source": "World Bank Pink Sheet",
                "source_url": "https://www.worldbank.org/en/research/commodity-markets",
                "retrieved_at": date.today().isoformat(),
            })
    observations.sort(key=lambda item: (item["series_id"], item["date"]))
    return observations


def fetch_world_bank_commodity_data(
    *, start_date: str | None = None, end_date: str | None = None,
    timeout: int = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch selected official World Bank Pink Sheet monthly prices, without a key."""
    if timeout < 1:
        raise ValueError("timeout must be positive")
    end = date.fromisoformat(end_date) if end_date else date.today()
    start = date.fromisoformat(start_date) if start_date else date(end.year - 2, end.month, 1)
    if start > end:
        raise ValueError("start_date must not be after end_date")
    months = (end.year - start.year) * 12 + end.month - start.month
    if months > MAX_DATE_RANGE_MONTHS:
        raise ValueError("commodity date range must not exceed 120 months")
    try:
        workbook_url = discover_monthly_workbook_url(timeout=timeout)
        payload, final_url = _read_url(
            workbook_url, allowed_hosts={WORKBOOK_HOST},
            max_bytes=MAX_WORKBOOK_BYTES, timeout=timeout,
        )
        observations = _parse_workbook(
            payload, start_date=start.isoformat(), end_date=end.isoformat()
        )
        return {
            "build": "3.7", "provider": "World Bank Commodity Price Data (Pink Sheet)",
            "provider_url": "https://www.worldbank.org/en/research/commodity-markets",
            "workbook_url": final_url, "license": "CC BY 4.0; attribution required",
            "attribution": "World Bank Commodity Price Data (The Pink Sheet), monthly prices.",
            "status": "available" if observations else "no_data",
            "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "request_count": 2, "requests_succeeded": 2, "requests_failed": 0,
            "observation_count": len(observations), "observations": observations,
            "errors": [], "limitations": [
                "Official World Bank Pink Sheet monthly nominal benchmark averages; not intraday, real-time, or executable quotes.",
                "Series use commodity-specific units and may be revised; blank source cells remain missing.",
                "Workbook release links can change; the current link is discovered from the official landing page each run.",
                "Coverage is global benchmark pricing, not Indonesian farm-gate, retail, or transaction prices.",
                "Attribution is required under the stated CC BY 4.0 terms; check source notes for series definitions.",
                "No trading signals, forecasts, causal claims, or investment advice are produced.",
            ],
        }
    except Exception as exc:
        return {
            "build": "3.7", "provider": "World Bank Commodity Price Data (Pink Sheet)",
            "provider_url": "https://www.worldbank.org/en/research/commodity-markets",
            "status": "unavailable", "date_range": {"start": start.isoformat(), "end": end.isoformat()},
            "request_count": 0, "requests_succeeded": 0, "requests_failed": 1,
            "observation_count": 0, "observations": [],
            "errors": [{"provider": "World Bank Pink Sheet", "error": str(exc)[:500]}],
            "limitations": ["Official commodity workbook could not be retrieved or parsed; missing data are not zero-filled."],
        }


def render_world_bank_commodity_html(data: dict[str, Any]) -> str:
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    rows = data.get("observations", [])
    rows = [item for item in rows if isinstance(item, dict)] if isinstance(rows, list) else []
    body = "".join(
        f"<tr><td>{esc(item.get('series'))}</td><td>{esc(item.get('date'))}</td>"
        f"<td class='num'>{esc(item.get('value'))}</td><td>{esc(item.get('unit'))}</td>"
        f"<td>{esc(item.get('category'))}</td></tr>" for item in rows
    ) or "<tr><td colspan='5'>No World Bank commodity observations available.</td></tr>"
    errors = data.get("errors", [])
    note = "; ".join(esc(item.get("error")) for item in errors if isinstance(item, dict)) or "No retrieval errors reported."
    return (
        '<section class="panel" id="world-bank-commodities"><h2>World Bank Pink Sheet · Commodity Benchmarks</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Monthly observations</div><strong>{esc(data.get("observation_count", 0))}</strong><small>Selected commodity series</small></article>'
        f'<article class="metric"><div class="muted">Requests succeeded</div><strong>{esc(data.get("requests_succeeded", 0))}</strong><small>Landing page and workbook</small></article>'
        f'<article class="metric"><div class="muted">Status</div><strong>{esc(data.get("status", "unknown"))}</strong><small>Official public source</small></article></div>'
        f'<div class="table-wrap"><table><thead><tr><th>Commodity</th><th>Month</th><th>Average</th><th>Unit</th><th>Sector</th></tr></thead><tbody>{body}</tbody></table></div>'
        f'<p class="muted">Source: <a href="https://www.worldbank.org/en/research/commodity-markets" rel="noopener noreferrer" target="_blank">World Bank Commodity Markets</a>. {note}</p>'
        '<p class="notice">Monthly nominal global benchmark averages, not local retail prices or live trading quotes. Attribution required (CC BY 4.0).</p></section>'
    )
