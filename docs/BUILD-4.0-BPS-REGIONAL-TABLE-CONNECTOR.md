# Build 4.0 — Automated BPS Regional Table Connector

Build 4.0 adds an optional, bounded client for BPS WebAPI dynamic-table data. It complements Build 3.9's domain catalog and regional ranking engine.

## What it does

- Calls the documented BPS dynamic-data route:
  `/v1/api/list/model/data/domain/{domain_id}/var/{variable_id}/th/{period_id}/key/{API_KEY}`
- Reads only explicit domain/variable/period combinations from a JSON configuration.
- Converts an unambiguous single numeric cell into a normalized regional observation and feeds it to Build 3.9 profiles/rankings.
- Rejects malformed specifications, nonnumeric identifiers, empty/ambiguous numeric payloads, and configurations above 100 requests per run.
- Keeps API credentials out of reports and error text. Only HTTPS requests to `webapi.bps.go.id` are allowed.

Official documentation: https://webapi.bps.go.id/documentation/ . The BPS guide documents the dynamic data route and notes that the API is read-only JSON. Review current BPS API terms and rate limits before enabling scheduled calls.

## Configure

1. Register the MD V14 application through BPS and add the issued credential as GitHub Actions secret `BPS_API_KEY`. Never paste the key into the repository or chat.
2. Identify the exact BPS dynamic table, domain ID, variable ID, and period ID from current BPS metadata/API documentation. Do not guess these identifiers.
3. Create `examples/bps-regional-tables.json` based on `examples/bps-regional-tables.sample.json`, using one object per domain/variable/period cell.
4. Keep each run at or below 100 requests. A single indicator across hundreds of regions may need deliberate batches; do not increase the cap to bypass BPS rate limits.
5. Workflow calls the config only when the non-secret file `examples/bps-regional-tables.json` exists. The repository sample is a template and is not automatically queried.

Required fields per table item: `domain_id`, `region_name`, `level` (`province` or `regency_city`), `indicator_code`, `variable_id`, `period_id`, and `period`. Optional fields: `indicator_name`, `province_code`, and `unit`.

## Run manually

```bash
python -m mdv14 --bps-tables-config examples/bps-regional-tables.json \
  --bps-api-key-env BPS_API_KEY --output build/report.json
```

The report includes `bps_regional_tables` with request counts, status, errors, and fetched observations. These observations are merged with any `--regional-data` input before regional comparisons.

## Important limits

The API documentation's example establishes the route pattern, not the meaning of every table or its cell encoding. The adapter accepts a response only when it can identify exactly one numeric cell. If a selected table returns multiple cells, a different response shape, or requires additional dimensions, it is marked as an error rather than guessed. Confirm the returned values, metadata, unit, period and coverage against the original BPS table before interpretation.

The current implementation does not automatically discover indicator variables or enumerate all 548 regional domains. This is intentional: table selection and regional batching must be explicit, bounded and respectful of BPS rate limits. No national-to-regional estimation, missing-value filling, causal inference or forecast is performed.

When using BPS WebAPI data, display the attribution required by BPS: "Layanan ini menggunakan API Badan Pusat Statistik (BPS)." Do not imply that MD V14 is an official or endorsed BPS product.
