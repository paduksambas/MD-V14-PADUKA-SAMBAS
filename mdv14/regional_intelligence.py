"""Indonesia subnational intelligence from supplied BPS regional observations.

BPS domain discovery is optional and authenticated. Indicator observations are
loaded from an explicitly supplied, normalized JSON export; no regional values
are fabricated or inferred from national aggregates.
"""
from __future__ import annotations

import json
import math
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from html import escape
from typing import Any

BPS_HOST = "webapi.bps.go.id"
BPS_BASE = "https://webapi.bps.go.id/v1/api"
TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 3_000_000
REGION_TYPES = {"prov": "province", "kab": "regency_city"}


def _request_json(url: str, timeout: int) -> Any:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != BPS_HOST:
        raise ValueError("Only the official HTTPS BPS WebAPI host is allowed")
    request = urllib.request.Request(
        url, headers={"User-Agent": "MDV14-RegionalIntelligence/1.0", "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("BPS response exceeds size limit")
    return json.loads(body.decode("utf-8"))


def _domain_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        if len(payload) > 1 and isinstance(payload[1], list):
            candidates = payload[1]
        else:
            candidates = payload
    elif isinstance(payload, dict):
        candidates = payload.get("data") or payload.get("domains") or payload.get("results") or []
        if isinstance(candidates, dict):
            candidates = list(candidates.values())
    else:
        candidates = []
    return [item for item in candidates if isinstance(item, dict)] if isinstance(candidates, list) else []


def fetch_bps_region_catalog(api_key: str | None, *, timeout: int = TIMEOUT_SECONDS) -> dict[str, Any]:
    """Discover BPS province and regency/city domains; never expose the API key."""
    if not api_key or not str(api_key).strip():
        return {
            "build": "3.9", "provider": "BPS WebAPI", "status": "not_configured",
            "requests_succeeded": 0, "requests_failed": 0, "regions": [], "errors": [],
            "limitations": ["Set BPS_API_KEY as a GitHub Actions secret to enable authenticated region-catalog discovery."],
        }
    if timeout < 1:
        raise ValueError("timeout must be positive")
    regions: list[dict[str, Any]] = []
    errors = []
    succeeded = 0
    for kind, level in REGION_TYPES.items():
        url = f"{BPS_BASE}/domain/type/{kind}/key/{urllib.parse.quote(str(api_key), safe='')}"
        try:
            payload = _request_json(url, timeout)
            rows = _domain_rows(payload)
            if not rows:
                raise ValueError("BPS returned no recognizable domain rows")
            for row in rows:
                code = row.get("domain_id") or row.get("domain") or row.get("id") or row.get("kode")
                name = row.get("domain_name") or row.get("name") or row.get("nama")
                if code is None or not name:
                    continue
                regions.append({
                    "region_code": str(code), "region_name": str(name),
                    "level": level, "parent_code": str(row.get("parent_id") or row.get("parent") or ""),
                    "source": "BPS WebAPI", "source_url": "https://webapi.bps.go.id/documentation/",
                })
            succeeded += 1
        except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
            safe_error = str(exc).replace(str(api_key), "[REDACTED]")
            errors.append({"region_type": kind, "error": safe_error[:300]})
    # Do not emit credential-bearing request URLs in the returned data.
    unique = {(r["level"], r["region_code"]): r for r in regions}
    return {
        "build": "3.9", "provider": "BPS WebAPI",
        "status": "available" if unique and not errors else "partial" if unique else "unavailable",
        "requests_succeeded": succeeded, "requests_failed": len(errors),
        "regions": sorted(unique.values(), key=lambda r: (r["level"], r["region_name"].casefold())),
        "region_count": len(unique), "errors": errors,
        "limitations": [
            "This endpoint discovers BPS administrative domains only; it does not download regional indicator tables.",
            "BPS API keys are private credentials and are never included in report URLs or error output.",
            "BPS domain identifiers and coverage may change; check current official metadata.",
        ],
    }


def _normalize_observations(data: Any) -> tuple[list[dict[str, Any]], list[str]]:
    raw = data.get("observations", data) if isinstance(data, dict) else data
    if not isinstance(raw, list):
        raise ValueError("regional data must be a JSON array or an object containing observations")
    rows, rejected = [], []
    for index, item in enumerate(raw):
        if not isinstance(item, dict):
            rejected.append(f"row {index}: not an object")
            continue
        code = str(item.get("region_code") or "").strip()
        name = str(item.get("region_name") or "").strip()
        level = str(item.get("level") or "").strip().lower()
        indicator = str(item.get("indicator_code") or item.get("indicator") or "").strip()
        period = str(item.get("period") or item.get("year") or "").strip()
        try:
            value = float(item.get("value"))
        except (TypeError, ValueError):
            rejected.append(f"row {index}: missing or invalid numeric value")
            continue
        if not code or not name or level not in {"province", "regency_city"} or not indicator or not period:
            rejected.append(f"row {index}: required region, level, indicator or period field missing")
            continue
        if not math.isfinite(value):
            rejected.append(f"row {index}: non-finite value")
            continue
        rows.append({
            "region_code": code, "region_name": name, "level": level,
            "province_code": str(item.get("province_code") or ""),
            "indicator_code": indicator,
            "indicator_name": str(item.get("indicator_name") or indicator),
            "period": period, "value": value, "unit": str(item.get("unit") or ""),
            "source": str(item.get("source") or "User-supplied BPS export"),
            "source_url": str(item.get("source_url") or ""),
        })
    return rows, rejected


def build_regional_intelligence(
    regional_data: Any = None,
    region_catalog: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Summarize supplied provincial/regency indicators with comparable rankings."""
    rows, rejected = _normalize_observations(regional_data if regional_data is not None else [])
    latest: dict[tuple[str, str, str], dict[str, Any]] = {}
    histories: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (row["level"], row["region_code"], row["indicator_code"])
        histories[key].append(row)
    for key, values in histories.items():
        latest[key] = max(values, key=lambda item: item["period"])

    profiles = []
    for (level, code, indicator), observations in sorted(histories.items()):
        ordered = sorted(observations, key=lambda item: item["period"])
        first, current = ordered[0], ordered[-1]
        delta = current["value"] - first["value"]
        profiles.append({
            "region_code": code, "region_name": current["region_name"],
            "province_code": current["province_code"], "level": level,
            "indicator_code": indicator, "indicator_name": current["indicator_name"],
            "first_period": first["period"], "latest_period": current["period"],
            "first_value": first["value"], "latest_value": current["value"],
            "change": delta, "unit": current["unit"],
            "direction": "rising" if delta > 0 else "falling" if delta < 0 else "unchanged",
            "observation_count": len(ordered), "source": current["source"],
            "source_url": current["source_url"],
        })

    comparison_groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for item in latest.values():
        comparison_groups[(item["level"], item["indicator_code"], item["period"])].append(item)
    rankings = []
    disparities = []
    for (level, indicator, period), values in sorted(comparison_groups.items()):
        ordered = sorted(values, key=lambda item: item["value"], reverse=True)
        for rank, item in enumerate(ordered, 1):
            rankings.append({
                "level": level, "indicator_code": indicator,
                "indicator_name": item["indicator_name"], "period": period,
                "rank": rank, "region_code": item["region_code"],
                "region_name": item["region_name"], "value": item["value"],
                "unit": item["unit"], "regions_compared": len(ordered),
            })
        numbers = [item["value"] for item in values]
        low = min(values, key=lambda item: item["value"])
        high = max(values, key=lambda item: item["value"])
        disparities.append({
            "level": level, "indicator_code": indicator,
            "indicator_name": values[0]["indicator_name"], "period": period,
            "regions_compared": len(values), "minimum": low["value"],
            "minimum_region": low["region_name"], "maximum": high["value"],
            "maximum_region": high["region_name"], "range": max(numbers) - min(numbers),
            "unit": values[0]["unit"],
        })

    catalog = region_catalog if isinstance(region_catalog, dict) else {}
    catalog_regions = catalog.get("regions", []) if isinstance(catalog.get("regions"), list) else []
    levels = {
        "province": len({r["region_code"] for r in rows if r["level"] == "province"}),
        "regency_city": len({r["region_code"] for r in rows if r["level"] == "regency_city"}),
    }
    return {
        "build": "3.9",
        "status": "available" if profiles or catalog_regions else "no_data",
        "observation_count": len(rows), "rejected_rows": len(rejected),
        "rejection_reasons": rejected[:30], "region_profiles": profiles,
        "rankings": rankings, "disparities": disparities,
        "regions_with_indicator_data": levels,
        "bps_region_catalog": {
            "status": catalog.get("status", "not_configured"),
            "region_count": catalog.get("region_count", len(catalog_regions)),
            "regions": catalog_regions,
            "requests_succeeded": catalog.get("requests_succeeded", 0),
            "requests_failed": catalog.get("requests_failed", 0),
            "errors": catalog.get("errors", []),
        },
        "sources": [
            {"name": "Badan Pusat Statistik (BPS) WebAPI", "url": "https://webapi.bps.go.id/documentation/"},
        ],
        "limitations": [
            "Regional indicator values are only computed from explicitly supplied regional observations; no values are inferred from national data.",
            "Rankings compare only the same indicator, period and administrative level; different definitions, units or coverage can invalidate comparisons.",
            "A range is a descriptive min-to-max spread, not a statistical inequality index or causal explanation.",
            "BPS domain discovery does not itself provide indicator observations; table selection and a normalized export are still required.",
            "Data revisions, administrative boundary changes, period definitions and missing regions must be reviewed against the original BPS table.",
        ],
    }


def render_regional_intelligence_html(data: dict[str, Any]) -> str:
    esc = lambda value: escape(str(value if value is not None else ""), quote=True)
    rows = []
    for item in data.get("rankings", []) if isinstance(data.get("rankings"), list) else []:
        if isinstance(item, dict):
            rows.append(
                f"<tr><td>{esc(item.get('level'))}</td><td>{esc(item.get('indicator_name'))}</td>"
                f"<td>{esc(item.get('period'))}</td><td>{esc(item.get('rank'))}/{esc(item.get('regions_compared'))}</td>"
                f"<td>{esc(item.get('region_name'))}</td><td class='num'>{esc(item.get('value'))} {esc(item.get('unit'))}</td></tr>"
            )
    ranking_body = "".join(rows) or "<tr><td colspan='6'>No comparable regional indicator observations loaded.</td></tr>"
    spread_rows = []
    for item in data.get("disparities", []) if isinstance(data.get("disparities"), list) else []:
        if isinstance(item, dict):
            spread_rows.append(
                f"<tr><td>{esc(item.get('level'))}</td><td>{esc(item.get('indicator_name'))}</td>"
                f"<td>{esc(item.get('period'))}</td><td>{esc(item.get('minimum_region'))}: {esc(item.get('minimum'))}</td>"
                f"<td>{esc(item.get('maximum_region'))}: {esc(item.get('maximum'))}</td>"
                f"<td>{esc(item.get('range'))} {esc(item.get('unit'))}</td></tr>"
            )
    spread_body = "".join(spread_rows) or '<tr><td colspan="6">No comparable spread available.</td></tr>'
    coverage = data.get("regions_with_indicator_data") if isinstance(data.get("regions_with_indicator_data"), dict) else {}
    catalog = data.get("bps_region_catalog") if isinstance(data.get("bps_region_catalog"), dict) else {}
    public_export = data.get("public_export") if isinstance(data.get("public_export"), dict) else {}
    airtable = data.get("airtable") if isinstance(data.get("airtable"), dict) else {}
    pending_observations = airtable.get("pending_observations", [])
    pending_observations = pending_observations if isinstance(pending_observations, list) else []
    pending_rows = "".join(
        f"<tr><td>{esc(item.get('region_name'))}</td><td>{esc(item.get('indicator_name'))} ({esc(item.get('indicator_code'))})</td>"
        f"<td>{esc(item.get('period'))}</td><td class='num'>{esc(item.get('value'))} {esc(item.get('unit'))}</td>"
        f"<td>{esc(item.get('validation_status'))}</td><td>{esc(item.get('date_collected'))}</td></tr>"
        for item in pending_observations if isinstance(item, dict)
    ) or "<tr><td colspan='6'>Tidak ada observasi yang menunggu validasi.</td></tr>"
    airtable_review_html = ""
    if airtable.get("records_read", 0):
        airtable_review_html = (
            f"<h3>Observasi Airtable · {esc(airtable.get('base_name') or 'PADUKA')}</h3>"
            f"<p class='muted'>Snapshot {esc(airtable.get('snapshot_date') or 'tanggal tidak tersedia')} · "
            f"{esc(airtable.get('records_read', 0))} record dibaca · "
            f"{esc(airtable.get('valid_count', 0))} valid · "
            f"{esc(airtable.get('pending_validation_count', 0))} menunggu validasi · "
            f"{esc(airtable.get('rejected_count', 0))} ditolak/tidak terbaca.</p>"
            "<div class='table-wrap'><table><thead><tr><th>Wilayah</th><th>Indikator</th><th>Periode</th>"
            "<th>Nilai</th><th>Status validasi</th><th>Tanggal diambil</th></tr></thead>"
            f"<tbody>{pending_rows}</tbody></table></div>"
            "<p class='notice'>Observasi berstatus Belum ditinjau atau Menunggu validasi ditampilkan untuk ditinjau manusia, "
            "tetapi tidak dipakai dalam ranking, peringkat, atau perhitungan disparitas sampai Status Validasi di Airtable menjadi Valid.</p>"
        )
    return (
        '<section class="panel" id="indonesia-regional-intelligence"><h2>Indonesia Regional Intelligence · Build 4.1</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Indicator observations</div><strong>{esc(data.get("observation_count", 0))}</strong><small>Explicit regional records</small></article>'
        f'<article class="metric"><div class="muted">Provinces represented</div><strong>{esc(coverage.get("province", 0))}</strong><small>With supplied indicator data</small></article>'
        f'<article class="metric"><div class="muted">Regencies/cities represented</div><strong>{esc(coverage.get("regency_city", 0))}</strong><small>With supplied indicator data</small></article>'
        f'<article class="metric"><div class="muted">BPS region catalog</div><strong>{esc(catalog.get("region_count", 0))}</strong><small>{esc(catalog.get("status", "not configured"))}</small></article></div>'
        f'<h3>Comparable regional rankings</h3><div class="table-wrap"><table><thead><tr><th>Level</th><th>Indicator</th><th>Period</th><th>Rank</th><th>Region</th><th>Value</th></tr></thead><tbody>{ranking_body}</tbody></table></div>'
        f'<h3>Regional spread (minimum to maximum)</h3><div class="table-wrap"><table><thead><tr><th>Level</th><th>Indicator</th><th>Period</th><th>Minimum</th><th>Maximum</th><th>Range</th></tr></thead><tbody>{spread_body}</tbody></table></div>'
        f'{airtable_review_html}'
        f'<p class="muted">BPS public export: {esc(public_export.get("status", "not configured"))}; {esc(public_export.get("observation_count", 0))} observations; {esc(public_export.get("rejected_rows", 0))} rejected. File: {esc(public_export.get("file_name", "not supplied"))}. SHA-256: {esc(public_export.get("file_sha256", "not available"))}</p>'
        '<p class="muted">Source: <a href="https://webapi.bps.go.id/documentation/" target="_blank" rel="noopener noreferrer">BPS WebAPI documentation</a> (API key required for API catalog/table requests) and <a href="https://www.bps.go.id/id/query-builder" target="_blank" rel="noopener noreferrer">BPS public table exports</a> (no API key for downloaded public files).</p>'
        '<p class="notice">Rankings compare like-for-like indicator, period and administrative level only. BPS domain discovery is not the same as loading regional statistics. No national-to-regional downscaling, causal inference, forecasts or policy advice.</p></section>'
    )


MAX_TABLE_REQUESTS = 100


def _numeric_candidates(payload: Any) -> list[float]:
    """Extract unambiguous numeric cells from documented BPS JSON envelopes."""
    found: list[float] = []
    def walk(value: Any, key: str = "") -> None:
        if isinstance(value, dict):
            for child_key, child in value.items():
                normalized = str(child_key).lower().replace("_", "")
                if key == "datacontent" or normalized in {"value", "nilai"}:
                    try:
                        number = float(child)
                        if math.isfinite(number):
                            found.append(number)
                            continue
                    except (TypeError, ValueError):
                        pass
                if isinstance(child, (dict, list)):
                    walk(child, normalized)
        elif isinstance(value, list):
            for child in value:
                walk(child, key)
        elif key in {"datacontent", "nilai", "value", "data"}:
            try:
                number = float(value)
                if math.isfinite(number):
                    found.append(number)
            except (TypeError, ValueError):
                pass
    walk(payload)
    return found


def _bps_table_value(payload: Any) -> float | None:
    """Return a value only when a BPS response contains exactly one numeric cell."""
    candidates = _numeric_candidates(payload)
    return candidates[0] if len(candidates) == 1 else None


def fetch_bps_regional_tables(
    api_key: str | None,
    table_config: Any,
    *,
    timeout: int = TIMEOUT_SECONDS,
    max_requests: int = MAX_TABLE_REQUESTS,
) -> dict[str, Any]:
    """Fetch explicitly configured BPS dynamic-table cells with strict request bounds.

    Each item identifies one BPS domain, variable and period. The API key is
    never returned. Ambiguous response cells are rejected rather than guessed.
    """
    if not api_key or not str(api_key).strip():
        return {"build": "4.0", "status": "not_configured", "request_count": 0,
                "requests_succeeded": 0, "requests_failed": 0, "observations": [],
                "errors": [], "limitations": ["Set BPS_API_KEY as a GitHub Actions secret."]}
    if not isinstance(table_config, dict) or not isinstance(table_config.get("tables"), list):
        return {"build": "4.0", "status": "invalid_config", "request_count": 0,
                "requests_succeeded": 0, "requests_failed": 0, "observations": [],
                "errors": ["Configuration must be an object with a tables array."]}
    if not 1 <= max_requests <= MAX_TABLE_REQUESTS or timeout < 1:
        raise ValueError("max_requests must be 1..100 and timeout must be positive")
    specs = table_config["tables"]
    if len(specs) > max_requests:
        return {"build": "4.0", "status": "request_limit_exceeded", "request_count": 0,
                "requests_succeeded": 0, "requests_failed": 0, "observations": [],
                "errors": [f"Configured {len(specs)} table requests; limit is {max_requests}."]}
    observations: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []
    succeeded = 0
    for index, spec in enumerate(specs):
        if not isinstance(spec, dict):
            errors.append({"item": str(index), "error": "table spec must be an object"})
            continue
        required = ("domain_id", "region_name", "level", "indicator_code",
                    "variable_id", "period_id", "period")
        if any(spec.get(key) in (None, "") for key in required) or spec.get("level") not in {"province", "regency_city"}:
            errors.append({"item": str(index), "error": "missing required table/domain metadata"})
            continue
        values = [str(spec[k]) for k in ("domain_id", "variable_id", "period_id")]
        if any(not value.isdigit() for value in values):
            errors.append({"item": str(index), "error": "domain_id, variable_id and period_id must be numeric IDs"})
            continue
        domain_id, variable_id, period_id = values
        url = (f"{BPS_BASE}/list/model/data/domain/{domain_id}/var/{variable_id}"
               f"/th/{period_id}/key/{urllib.parse.quote(str(api_key), safe='')}")
        try:
            payload = _request_json(url, timeout)
            value = _bps_table_value(payload)
            if value is None:
                raise ValueError("BPS response did not contain exactly one unambiguous numeric cell")
            observations.append({
                "region_code": domain_id, "region_name": str(spec["region_name"]),
                "level": spec["level"], "province_code": str(spec.get("province_code") or ""),
                "indicator_code": str(spec["indicator_code"]),
                "indicator_name": str(spec.get("indicator_name") or spec["indicator_code"]),
                "period": str(spec["period"]), "value": value,
                "unit": str(spec.get("unit") or ""), "source": "BPS WebAPI",
                "source_url": "https://webapi.bps.go.id/documentation/",
                "bps_variable_id": variable_id, "bps_period_id": period_id,
            })
            succeeded += 1
        except (OSError, ValueError, urllib.error.URLError, json.JSONDecodeError) as exc:
            # Never echo exception text: HTTP errors can contain the credential-bearing URL.
            errors.append({"item": str(index), "error": f"BPS request failed ({type(exc).__name__})"})
    return {
        "build": "4.0", "status": "available" if observations and not errors else
                  "partial" if observations else "unavailable" if errors else "no_data",
        "request_count": len(specs), "requests_succeeded": succeeded,
        "requests_failed": len(errors), "observations": observations, "errors": errors,
        "limitations": [
            "Only explicitly configured domain/variable/period combinations are queried.",
            "The maximum is 100 requests per run; expand coverage in deliberate, rate-limit-aware batches.",
            "A response with zero or multiple numeric cells is rejected as ambiguous.",
            "BPS table definitions, units, periods and revisions must be checked against source metadata.",
        ],
    }


# Public BPS exports (CSV/XLSX/JSON) do not require a WebAPI key.
import csv
import hashlib
import io
import posixpath
import zipfile
import xml.etree.ElementTree as ET

MAX_PUBLIC_EXPORT_BYTES = 10_000_000
MAX_PUBLIC_EXPORT_ROWS = 100_000


def _xlsx_first_sheet(content: bytes) -> list[dict[str, str]]:
    """Read the first worksheet using the standard library; reject oversized/unsafe archives."""
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = set(archive.namelist())
        if len(names) > 500 or any(name.startswith("/") or ".." in name.split("/") for name in names):
            raise ValueError("invalid XLSX archive paths or excessive file count")
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rel_ns = "{http://schemas.openxmlformats.org/package/2006/relationships}"
        rel_map = {item.attrib["Id"]: item.attrib["Target"] for item in rels.findall(f"{rel_ns}Relationship")}
        sheet = workbook.find(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheet")
        if sheet is None:
            raise ValueError("XLSX contains no worksheet")
        target = rel_map.get(sheet.attrib.get("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"))
        if not target:
            raise ValueError("XLSX first worksheet relationship is missing")
        sheet_path = posixpath.normpath(posixpath.join("xl", target))
        if not sheet_path.startswith("xl/") or sheet_path not in names:
            raise ValueError("XLSX worksheet path is invalid")
        shared = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(".//{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si"):
                shared.append("".join(node.text or "" for node in item.iter("{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t")))
        root = ET.fromstring(archive.read(sheet_path))
        ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
        matrix = []
        for row in root.findall(".//" + ns + "sheetData/" + ns + "row"):
            values = {}
            for cell in row.findall(ns + "c"):
                ref = cell.attrib.get("r", "")
                col = "".join(ch for ch in ref if ch.isalpha())
                if not col:
                    continue
                value_node = cell.find(ns + "v")
                value = value_node.text if value_node is not None else ""
                if cell.attrib.get("t") == "s" and value:
                    value = shared[int(value)]
                elif cell.attrib.get("t") == "inlineStr":
                    value = "".join(node.text or "" for node in cell.iter(ns + "t"))
                values[col] = value
            matrix.append(values)
            if len(matrix) > MAX_PUBLIC_EXPORT_ROWS + 1:
                raise ValueError("XLSX row limit exceeded")
    if not matrix:
        return []
    def col_number(label: str) -> int:
        number = 0
        for char in label:
            number = number * 26 + ord(char.upper()) - 64
        return number
    max_col = max((col_number(k) for row in matrix for k in row), default=0)
    headers = [matrix[0].get(_column_label(i), "").strip() for i in range(1, max_col + 1)]
    result = []
    for row in matrix[1:]:
        result.append({headers[i-1]: row.get(_column_label(i), "") for i in range(1, len(headers)+1) if headers[i-1]})
    return result


def _column_label(number: int) -> str:
    label = ""
    while number:
        number, remainder = divmod(number - 1, 26)
        label = chr(65 + remainder) + label
    return label


def load_bps_public_export(path: str, config: Any) -> dict[str, Any]:
    """Normalize a downloaded BPS CSV, XLSX or JSON export using explicit column mapping.

    Config format: {"columns": {"region_code":"Kode Wilayah", ...},
    "defaults": {"level":"province", ...}, "source_url":"official table URL"}.
    """
    if not isinstance(config, dict) or not isinstance(config.get("columns"), dict):
        raise ValueError("BPS public export config must contain a columns mapping")
    file_path = str(path)
    with open(file_path, "rb") as handle:
        content = handle.read(MAX_PUBLIC_EXPORT_BYTES + 1)
    if len(content) > MAX_PUBLIC_EXPORT_BYTES:
        raise ValueError("BPS public export exceeds 10 MB limit")
    suffix = file_path.lower().rsplit(".", 1)[-1]
    if suffix == "csv":
        decoded = None
        for encoding in ("utf-8-sig", "utf-8", "cp1252"):
            try:
                decoded = content.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        if decoded is None:
            raise ValueError("CSV encoding is unsupported; save as UTF-8")
        sample = decoded[:8192]
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\\t")
        except csv.Error:
            dialect = csv.excel
        source_rows = list(csv.DictReader(io.StringIO(decoded), dialect=dialect))
    elif suffix == "xlsx":
        source_rows = _xlsx_first_sheet(content)
    elif suffix == "json":
        payload = json.loads(content.decode("utf-8-sig"))
        source_rows = payload.get("observations", payload) if isinstance(payload, dict) else payload
        if not isinstance(source_rows, list):
            raise ValueError("JSON export must be an array or contain observations array")
    else:
        raise ValueError("supported BPS public export formats are CSV, XLSX and JSON")
    if len(source_rows) > MAX_PUBLIC_EXPORT_ROWS:
        raise ValueError("BPS public export row limit exceeded")
    columns = config["columns"]
    defaults = config.get("defaults", {})
    if not isinstance(defaults, dict):
        raise ValueError("config defaults must be an object")
    required = ("region_code", "region_name", "level", "indicator_code", "period", "value")
    if any(key not in columns and key not in defaults for key in required):
        raise ValueError("mapping/defaults must define region_code, region_name, level, indicator_code, period and value")
    normalized, rejected = [], []
    for index, raw in enumerate(source_rows, start=2):
        if not isinstance(raw, dict):
            rejected.append(f"row {index}: not an object")
            continue
        item = dict(defaults)
        for field, header in columns.items():
            if not isinstance(header, str):
                raise ValueError(f"column mapping for {field} must be a header string")
            item[field] = raw.get(header, "")
        item.setdefault("source", "BPS public table export")
        item.setdefault("source_url", str(config.get("source_url") or ""))
        rows, row_rejections = _normalize_observations([item])
        if rows:
            normalized.extend(rows)
        else:
            rejected.append(f"row {index}: " + "; ".join(row_rejections))
    return {
        "build": "4.1", "status": "available" if normalized and not rejected else
                  "partial" if normalized else "no_data",
        "file_name": file_path.rsplit("/", 1)[-1],
        "file_sha256": hashlib.sha256(content).hexdigest(),
        "format": suffix, "source_url": str(config.get("source_url") or ""),
        "rows_read": len(source_rows), "observation_count": len(normalized),
        "rejected_rows": len(rejected), "rejection_reasons": rejected[:30],
        "observations": normalized,
        "limitations": [
            "No BPS WebAPI key is used; the source file must be downloaded from a public BPS table/export page.",
            "Column mapping and indicator metadata are explicit user configuration, not guessed from column names.",
            "Only the first worksheet is read from XLSX files; formulas are not recalculated.",
            "Check source table definitions, units, period, regional coverage and revision date before comparing values.",
        ],
    }
