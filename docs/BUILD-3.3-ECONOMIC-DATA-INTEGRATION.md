# Build 3.3 — Dedicated Economic Data Sources & Market Intelligence Integration

## Scope

Build 3.3 adds an optional official macroeconomic data connector using the public World Bank Indicators API. The scheduled monitoring workflow requests observations for Indonesia (ID), United States (US), and China (CN), starting in 2020 through the current year.

Initial indicator allowlist:

| Indicator | World Bank code | Unit |
|---|---|---|
| GDP growth | NY.GDP.MKTP.KD.ZG | Annual % |
| Consumer price inflation | FP.CPI.TOTL.ZG | Annual % |
| Trade | NE.TRD.GNFS.ZS | % of GDP |
| Net energy imports | EG.IMP.CONS.ZS | % of energy use |
| Merchandise exports | TX.VAL.MRCH.CD.WT | Current US$ |
| Merchandise imports | TM.VAL.MRCH.CD.WT | Current US$ |

## Usage

```bash
python -m mdv14 --feeds examples/feeds.sample.json \
  --economic-countries ID,US,CN \
  --economic-start-year 2020 \
  --output build/latest-report.json \
  --dashboard build/monitoring-dashboard.html
```

The economic observations are stored in the report's `economic_data` section and rendered separately in the dashboard. This keeps official macroeconomic values distinct from article-derived sector cues and heuristic news scores.

## Reliability and security

- Only HTTPS requests to the fixed `api.worldbank.org` host are accepted.
- Indicator codes are allowlisted; country codes and year windows are validated.
- Request timeouts and response byte limits are enforced.
- Failed requests are reported individually; unavailable or null observations are not converted to zero.
- Every observation retains provider, indicator code, country code, year, unit, and source URL.

## Interpretation

These are published historical observations, not live market prices, high-frequency exchange rates, or forecasts. Reporting periods differ by indicator and country; revisions and publication lags apply. Merchandise trade values are current US dollars and are not inflation-adjusted. Macroeconomic series provide context but do not establish that a news event caused an economic or market movement. Human review and primary-source verification remain necessary.

## Tests

```bash
python -m unittest discover -s tests -v
```
