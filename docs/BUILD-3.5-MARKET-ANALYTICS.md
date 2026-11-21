# Build 3.5 — Cross-Asset Market Analytics

## Purpose

Build 3.5 adds deterministic retrospective analytics to the market observations already collected by Build 3.4. It requires no additional API key and does not introduce another data provider.

## Inputs

- Public Frankfurter daily reference rates for USD/IDR, USD/EUR, and USD/CNY.
- Stooq daily equity-index and commodity-futures observations from Build 3.6.
- Optional FRED observations when `FRED_API_KEY` is configured.

Only valid observations with a recognized series identifier, ISO date, and numeric value are processed. Each series is analyzed independently. If providers supply overlapping dates for a series, the last supplied row for that date is retained; values are not blended.

## Metrics

For each series, `market_analytics` reports:

- First and latest observed values and dates.
- Absolute and percentage change over the observed window.
- Retrospective direction: rising, falling, or unchanged.
- Population standard deviation of observed-step percentage changes when at least two steps are available.
- Provider names, unit, observation count, and category.

Percentage change is unavailable if the first observed value is zero. Volatility is not annualized and does not correct for irregular date intervals, weekends, holidays, or provider publication gaps.

## Output

The CLI defaults to a 30-day market-data window (overridable with `--market-start-date` and `--market-end-date`) and writes `market_analytics` into the JSON report. The offline dashboard includes a Build 3.5 section with the series summaries. The monitoring workflow runs the same analysis as part of its normal collection cycle.

## Interpretation and safeguards

- No missing values or dates are interpolated or zero-filled.
- Unlike units and asset classes are not merged into a composite score.
- Direction and observed-step volatility are descriptive only, not trading signals, forecasts, investment advice, causal findings, or proof of market impact.
- Provider publication delays, revisions, market closures, and incomplete coverage remain relevant limitations.

## Tests

Run `python -m unittest discover -s tests -v`. Build 3.5 tests cover change calculations, series separation, zero starting values, invalid/missing rows, insufficient volatility history, and dashboard escaping/rendering.
