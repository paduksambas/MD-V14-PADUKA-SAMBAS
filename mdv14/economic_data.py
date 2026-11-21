"""Official World Bank indicator retrieval for MD V14 economic monitoring.

Only the public api.worldbank.org host and a fixed indicator allowlist are used.
Values are observations, not forecasts; unavailable data is preserved as missing.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from typing import Any

API_HOST = "api.worldbank.org"
BASE_URL = "https://api.worldbank.org/v2"
TIMEOUT_SECONDS = 15
MAX_RESPONSE_BYTES = 3_000_000
INDICATORS = {
    "NY.GDP.MKTP.KD.ZG": {"name": "GDP growth (annual %)", "sector": "macroeconomy", "unit": "%"},
    "FP.CPI.TOTL.ZG": {"name": "Inflation, consumer prices (annual %)", "sector": "macroeconomy", "unit": "%"},
    "NE.TRD.GNFS.ZS": {"name": "Trade (% of GDP)", "sector": "trade_supply_chain", "unit": "% of GDP"},
    "EG.IMP.CONS.ZS": {"name": "Energy imports, net (% of energy use)", "sector": "energy", "unit": "%"},
    "TX.VAL.MRCH.CD.WT": {"name": "Merchandise exports (current US$)", "sector": "trade_supply_chain", "unit": "current US$"},
    "TM.VAL.MRCH.CD.WT": {"name": "Merchandise imports (current US$)", "sector": "trade_supply_chain", "unit": "current US$"},
}
_COUNTRY = re.compile(r"^[A-Z]{2}$")
_YEAR = re.compile(r"^\d{4}$")


def _parse_countries(countries: str | list[str]) -> list[str]:
    values = countries.split(",") if isinstance(countries, str) else countries
    if not isinstance(values, (list, tuple)):
        raise ValueError("countries must be comma-separated ISO alpha-2 codes")
    result = []
    for value in values:
        code = str(value).strip().upper()
        if not _COUNTRY.fullmatch(code):
            raise ValueError(f"invalid country code: {value!r}")
        if code not in result:
            result.append(code)
    if not result:
        raise ValueError("at least one country code is required")
    if len(result) > 30:
        raise ValueError("maximum 30 country codes per request")
    return result


def _parse_year_range(start_year: int | str, end_year: int | str) -> tuple[int, int]:
    if not _YEAR.fullmatch(str(start_year)) or not _YEAR.fullmatch(str(end_year)):
        raise ValueError("years must be four-digit integers")
    start, end = int(start_year), int(end_year)
    if start < 1960 or end > date.today().year or start > end or end - start > 30:
        raise ValueError("year range must be within 1960..current year and at most 31 years")
    return start, end


def _fetch_json(url: str, timeout: int = TIMEOUT_SECONDS) -> Any:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != API_HOST:
        raise ValueError("only the official World Bank API host is allowed")
    request = urllib.request.Request(
        url, headers={"User-Agent": "MDV14-EconomicData/1.0", "Accept": "application/json"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        body = response.read(MAX_RESPONSE_BYTES + 1)
    if len(body) > MAX_RESPONSE_BYTES:
        raise ValueError("World Bank response exceeds size limit")
    return json.loads(body.decode("utf-8"))


def fetch_world_bank_indicators(
    countries: str | list[str] = ("ID", "US", "CN"),
    *,
    start_year: int | str = 2020,
    end_year: int | str | None = None,
    indicators: list[str] | None = None,
    timeout: int = TIMEOUT_SECONDS,
) -> dict[str, Any]:
    """Fetch allowlisted World Bank observations; report each indicator failure."""
    codes = _parse_countries(countries)
    end = date.today().year if end_year is None else end_year
    start, end = _parse_year_range(start_year, end)
    selected = list(INDICATORS) if indicators is None else list(dict.fromkeys(indicators))
    if not selected or any(code not in INDICATORS for code in selected):
        raise ValueError("indicators must use the configured World Bank indicator allowlist")
    if timeout < 1:
        raise ValueError("timeout must be positive")
    observations = []
    requests = []
    errors = []
    for country in codes:
        for indicator in selected:
            query = urllib.parse.urlencode({
                "date": f"{start}:{end}", "format": "json", "per_page": 100
            })
            url = f"{BASE_URL}/country/{country}/indicator/{indicator}?{query}"
            try:
                payload = _fetch_json(url, timeout=timeout)
                if not isinstance(payload, list) or len(payload) < 2 or not isinstance(payload[1], list):
                    raise ValueError("unexpected World Bank API response structure")
                meta = payload[0] if isinstance(payload[0], dict) else {}
                rows = payload[1]
                count = 0
                for row in rows:
                    if not isinstance(row, dict) or row.get("value") is None:
                        continue
                    country_meta = row.get("country") if isinstance(row.get("country"), dict) else {}
                    indicator_meta = row.get("indicator") if isinstance(row.get("indicator"), dict) else {}
                    observations.append({
                        "country_code": country,
                        "country": str(country_meta.get("value") or country),
                        "indicator_code": indicator,
                        "indicator": str(indicator_meta.get("value") or INDICATORS[indicator]["name"]),
                        "sector": INDICATORS[indicator]["sector"],
                        "year": str(row.get("date") or ""),
                        "value": row.get("value"),
                        "unit": INDICATORS[indicator]["unit"],
                        "source": "World Bank",
                        "source_url": url,
                        "retrieved_at": date.today().isoformat(),
                    })
                    count += 1
                requests.append({"country_code": country, "indicator_code": indicator,
                                  "status": "ok", "observations_received": count,
                                  "api_total": meta.get("total")})
            except (urllib.error.URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as exc:
                errors.append({"country_code": country, "indicator_code": indicator,
                               "error": str(exc), "status": "unavailable"})
                requests.append({"country_code": country, "indicator_code": indicator,
                                  "status": "unavailable", "observations_received": 0})
    observations.sort(key=lambda item: (item["country_code"], item["indicator_code"], item["year"]))
    return {
        "build": "3.3",
        "provider": "World Bank Indicators API",
        "provider_url": "https://api.worldbank.org/v2",
        "countries_requested": codes,
        "year_range": {"start": start, "end": end},
        "indicators_requested": selected,
        "request_count": len(requests),
        "requests_succeeded": sum(item["status"] == "ok" for item in requests),
        "requests_failed": len(errors),
        "observation_count": len(observations),
        "observations": observations,
        "request_status": requests,
        "errors": errors,
        "limitations": [
            "Values are official published historical observations, not real-time market quotes or forecasts.",
            "The latest available year varies by indicator and country; missing observations are not zero.",
            "World Bank definitions, revisions, units, and reporting lags apply; consult provider metadata before comparison.",
            "GDP, inflation, trade, and energy indicators are macroeconomic context, not proof that a news event caused a change.",
            "Merchandise trade values are current US dollars and are not inflation-adjusted.",
        ],
    }
