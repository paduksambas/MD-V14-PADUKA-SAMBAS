# Build 3.4 — Global Financial Markets Intelligence

## Scope

Adds a default no-key foreign-exchange reference data adapter using the public Frankfurter API, plus an optional adapter for the Federal Reserve Bank of St. Louis FRED API. FRED still requires a key, but it is no longer required for MD V14 market-data collection. The public FX adapter retrieves USD reference rates against IDR, EUR, and CNY. The existing World Bank Indicators integration independently supplies macroeconomic data.

## No-key public FX data

The default adapter calls `https://api.frankfurter.dev/v2/rates` over HTTPS, with USD as base and IDR, EUR, and CNY as quotes. The public service does not require an API key or account. Date windows are bounded to 367 calendar days; responses are size-limited, timeouts are bounded, missing observations remain missing, and provider failures are reported without stopping the intelligence pipeline. These are daily reference/mid-market rates blended from central-bank and official sources, not intraday executable quotes. See the [Frankfurter documentation](https://frankfurter.dev/).

## Optional FRED series allowlist

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

Without the key, the no-key Frankfurter adapter still populates `market_data` with public FX reference rates. The optional FRED adapter is reported separately as `fred_market_data.status=not_configured`; it does not block collection.

GitHub Actions attempts the public Frankfurter request on each monitoring cycle without credentials. If `FRED_API_KEY` is absent, only the optional FRED supplement is skipped; no manual key setup is needed for daily USD/IDR, USD/EUR, and USD/CNY reference rates.

## FRED attribution and terms

The dashboard displays the required attribution: "This product uses the FRED® API but is not endorsed or certified by the Federal Reserve Bank of St. Louis." It also links to the [FRED API Terms of Use](https://fred.stlouisfed.org/docs/api/terms_of_use.html). Users and operators remain responsible for compliance with the provider's current terms and applicable law.

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
