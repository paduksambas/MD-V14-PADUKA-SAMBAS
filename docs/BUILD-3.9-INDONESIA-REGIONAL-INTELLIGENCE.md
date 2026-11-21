# Build 3.9 — Indonesia Regional Intelligence

## What is added

Build 3.9 adds an explicit province and regency/city intelligence layer. It accepts normalized regional observations from a BPS statistical table export, computes per-region history, ranks comparable regions, and shows a descriptive min-to-max spread for the same indicator, period and administrative level.

It also supports optional BPS WebAPI administrative-domain discovery for province and regency/city domains.

## BPS WebAPI setup

BPS WebAPI is read-only and requires registration/API credentials. Register the MD V14 application with BPS and store the key as a GitHub Actions secret named `BPS_API_KEY`. Do not place the key in source code, JSON input, public workflow output, or report URLs.

The BPS domain-catalog discovery calls the documented province and regency domain endpoints. This discovers administrative domains only; it does not automatically choose statistical tables or download their indicator data. Review the current BPS documentation and terms, rate limits, and attribution requirements.

Official documentation: https://webapi.bps.go.id/documentation/

## Regional data input

Pass `--regional-data path/to/bps-regional-export.json`. The file may be a JSON array or an object with an `observations` array. Each observation should contain:

- `region_code`, `region_name`
- `level`: `province` or `regency_city`
- `indicator_code`, optional `indicator_name`
- `period` (for example `2023`), numeric `value`, optional `unit`
- optional `province_code`, `source`, `source_url`

Example:

```json
{
  "observations": [
    {
      "region_code": "32",
      "region_name": "Jawa Barat",
      "level": "province",
      "indicator_code": "PDRB_GROWTH",
      "indicator_name": "Pertumbuhan PDRB",
      "period": "2023",
      "value": 5.0,
      "unit": "%"
    }
  ]
}
```

## Analytical safeguards

- Regional rankings are grouped by indicator, period, and administrative level; provinces are never ranked against regencies/cities.
- No missing values are filled and no national indicator is downscaled to local government.
- The min-to-max range is descriptive, not a formal inequality index.
- A ranking is not a performance judgment, cause attribution, forecast, or policy recommendation.
- Check original BPS table definitions, units, publication period, revisions, and administrative boundaries before interpretation.
- The dashboard labels the number of regions represented by actual supplied observations; it does not imply complete coverage.

## CLI

`python -m mdv14 --regional-data build/bps-regional-export.json --bps-api-key-env BPS_API_KEY --dashboard build/dashboard.html`

Without `BPS_API_KEY`, catalog status is `not_configured`. Without a regional JSON export, regional indicator coverage remains zero. Global monitoring continues without either optional input.
