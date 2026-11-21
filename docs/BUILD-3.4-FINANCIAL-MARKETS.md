# Build 3.4 — Global Financial Markets Intelligence

## Scope

Adds an optional market-observation adapter for the official Federal Reserve Bank of St. Louis FRED API. The provider requires a FRED API key. Configure it as the `FRED_API_KEY` environment variable locally or as a repository Actions secret with that exact name. No key is stored in source control.

## Initial series allowlist

| Series | Description | Unit |
|---|---|---|
| DEXIDUS | Indonesian Rupiah to U.S. Dollar | IDR per USD |
| DEXUSEU | U.S. Dollar to Euro | USD per EUR |
| DEXCHUS | Chinese Yuan to U.S. Dollar | CNY per USD |
| SP500 | S&P 500 | Index points |
| NASDAQCOM | NASDAQ Composite | Index points |
| DGS10 | 10-Year Treasury Constant Maturity Rate | Percent |
| DCOILWTICO | WTI Crude Oil Price | USD per barrel |
| GOLDPMGBD228NLBM | Gold Price, London Bullion Market | USD per troy ounce |

The FRED API series definitions and publication conventions remain authoritative. FX quote conventions must be checked carefully before comparing series.

## Usage

```bash
export FRED_API_KEY="your-key"
python -m mdv14 --market-start-date 2025-01-01 --market-end-date 2025-12-31 \
  --output build/report.json --dashboard build/dashboard.html
```

Without the key, the pipeline still completes and reports `market_data.status=not_configured`, zero requests, and zero observations. This is an explicit configuration state, not an API failure or a market value of zero.

GitHub Actions reads the optional `FRED_API_KEY` repository secret. Add it under repository Settings → Secrets and variables → Actions to enable market data in scheduled runs. If it is absent, the workflow continues without FRED requests.

## Safeguards and interpretation

- Requests use HTTPS and the fixed `api.stlouisfed.org/fred/series/observations` endpoint.
- Series IDs are allowlisted; dates, timeout, and response size are bounded.
- Provider failures are isolated per series; missing and "." observations are omitted, never zero-filled.
- The API key is not included in report URLs and is redacted from error text.
- Each observation includes series ID, date, unit, frequency, provider, source URL, and retrieval date.
- Data are published observations and may be delayed, revised, or absent on holidays.
- These are not guaranteed real-time or executable quotes. The system emits no trading signals, investment advice, causal attribution, or forecasts.

## Tests

```bash
python -m unittest discover -s tests -v
```
