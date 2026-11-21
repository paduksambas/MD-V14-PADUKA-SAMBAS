# Build 3.6 — Public Equity & Commodity Market Data

## Purpose

Build 3.6 expands no-key market coverage beyond the USD reference FX rates provided by Frankfurter. It adds a bounded adapter for daily CSV observations from Stooq and feeds the normalized rows into Build 3.5 per-series analytics.

## Configured instruments

| Symbol | Instrument | Category | Unit |
|---|---|---|---|
| `^spx` | S&P 500 | Equity index | Index points |
| `^ndq` | NASDAQ Composite | Equity index | Index points |
| `^dax` | DAX | Equity index | Index points |
| `^nkx` | Nikkei 225 | Equity index | Index points |
| `cl.f` | WTI crude oil futures | Commodity | USD per barrel |
| `gc.f` | Gold futures | Commodity | USD per troy ounce |

The adapter uses a fixed symbol allowlist, HTTPS and an exact provider host/path check, a 15-second per-request timeout, a 2 MB response limit, and a maximum 367-calendar-day date range. Each symbol request is isolated so one unavailable symbol does not discard successful results. Collection is opt-in via `--enable-public-assets`; it is disabled in the six-hour scheduled workflow because the free Stooq endpoint returned non-CSV quota/challenge responses from the GitHub Actions runner during live validation.

## Output and dashboard

When `--enable-public-assets` is supplied, the CLI adds `public_asset_data` to the JSON report and the dashboard renders instrument, date, close, unit, provider, request metrics, and errors. Build 3.5 market analytics consumes Frankfurter, optional FRED, and any Stooq observations actually returned. Without the flag, the report records `not_requested` and makes no Stooq requests. Series remain separate and are never combined into a composite asset score.

## Limitations and safeguards

- No API key or account is required for the Stooq adapter; service and symbol availability can change. The live scheduled runner returned non-CSV responses for all six configured symbols, so this source is not treated as reliable scheduled coverage.
- Values are daily provider-supplied closes, not guaranteed real-time, executable, or exchange-certified quotes.
- Futures prices can be affected by contract-roll and provider symbol conventions.
- The current no-key allowlist covers equity indices and two commodity futures; it does not provide government-bond yields.
- Missing dates and values are not interpolated or zero-filled. Provider failures are preserved per symbol.
- No trading signals, forecasts, causal findings, or investment advice are produced.
- Optional FRED integration remains separate and still requires a user-supplied API key.

## Tests

Run `python -m unittest discover -s tests -v`. To opt in locally, add `--enable-public-assets` to the normal `python -m mdv14` command; the provider may reject requests due to IP-based limits. The Build 3.6 adapter tests cover normalization, symbol/date/range/timeout validation, per-symbol failure isolation, malformed CSV handling, and HTML escaping.
