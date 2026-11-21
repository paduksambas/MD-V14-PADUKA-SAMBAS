# Build 3.8 — Indonesia Strategic Economic Intelligence

## Scope

Build 3.8 adds an Indonesia-focused view that uses published World Bank observations for country code ID and global monthly commodity benchmarks already collected by Build 3.7. It does not claim to be an official Government of Indonesia product.

## Indonesia indicators

The World Bank allowlist now includes GDP growth, consumer inflation, trade openness, merchandise exports/imports, agriculture/industry/services value added, unemployment, FDI net inflows, total reserves, and current-account balance. The default monitoring configuration requests ID, US and CN for comparison; Build 3.8 summarizes only ID observations in the national panel.

## Commodity channels

Available global benchmark prices are organized into qualitative analyst-review channels: energy, agriculture/food, metals/manufacturing, precious metals, and fertilizers. The module displays the latest available benchmark observation per series and links it to a transparent review prompt. It does not estimate Indonesia's trade exposure, price pass-through, import dependency, or causal impact.

## Safeguards

- Uses the existing unauthenticated World Bank Indicators API and the official World Bank Pink Sheet collector; no FRED or BPS API key is required.
- BPS WebAPI requires registration/credentials and is not silently assumed to be available. A future BPS integration must be explicitly configured and comply with BPS terms, attribution, and rate limits.
- Missing data remain missing; latest observation years differ by indicator.
- Units, source URLs and year windows are retained.
- Output is descriptive decision support, not a forecast, risk probability, policy recommendation, or investment advice.

## Output

The pipeline adds `indonesia_economic_intelligence`, the dashboard renders national macro indicators and qualitative commodity channels, and CLI summary reports the Build 3.8 status and coverage. See README and this document for limitations.
