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
    return (
        '<section class="panel" id="indonesia-regional-intelligence"><h2>Indonesia Regional Intelligence · Build 3.9</h2>'
        f'<div class="grid"><article class="metric"><div class="muted">Indicator observations</div><strong>{esc(data.get("observation_count", 0))}</strong><small>Explicit regional records</small></article>'
        f'<article class="metric"><div class="muted">Provinces represented</div><strong>{esc(coverage.get("province", 0))}</strong><small>With supplied indicator data</small></article>'
        f'<article class="metric"><div class="muted">Regencies/cities represented</div><strong>{esc(coverage.get("regency_city", 0))}</strong><small>With supplied indicator data</small></article>'
        f'<article class="metric"><div class="muted">BPS region catalog</div><strong>{esc(catalog.get("region_count", 0))}</strong><small>{esc(catalog.get("status", "not configured"))}</small></article></div>'
        f'<h3>Comparable regional rankings</h3><div class="table-wrap"><table><thead><tr><th>Level</th><th>Indicator</th><th>Period</th><th>Rank</th><th>Region</th><th>Value</th></tr></thead><tbody>{ranking_body}</tbody></table></div>'
        f'<h3>Regional spread (minimum to maximum)</h3><div class="table-wrap"><table><thead><tr><th>Level</th><th>Indicator</th><th>Period</th><th>Minimum</th><th>Maximum</th><th>Range</th></tr></thead><tbody>{spread_body}</tbody></table></div>'
        '<p class="muted">Source: <a href="https://webapi.bps.go.id/documentation/" target="_blank" rel="noopener noreferrer">BPS WebAPI documentation</a>. A BPS API key is required for domain discovery.</p>'
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
                if normalized in {"datacontent", "value", "nilai", "data"}:
                    walk(child, normalized)
                elif isinstance(child, (dict, list)):
                    walk(child, normalized)
                elif normalized in {"nilai", "value"}:
                    try:
                        number = float(child)
                        if math.isfinite(number):
                            found.append(number)
                    except (TypeError, ValueError):
                        pass
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
            safe_error = str(exc).replace(str(api_key), "[REDACTED]")
            errors.append({"item": str(index), "error": safe_error[:250]})
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
