# Build 3.7 — Official Commodity Intelligence

## Purpose

Build 3.7 adds the World Bank Commodity Price Data (Pink Sheet) as a no-key, official public source for monthly global commodity benchmark prices. The collector discovers the current workbook URL from the World Bank Commodity Markets landing page because the release directory changes over time.

## Coverage

The adapter extracts a curated set of named series from the workbook's "Monthly Prices" sheet: Brent, WTI and average crude oil; U.S. natural gas; Australian coal; gold, silver, copper and aluminum; Arabica and Robusta coffee; palm oil; U.S. HRW wheat; maize; Thai 5% rice; and urea. It retains the workbook's units row and missing cells. It does not imply local Indonesian market prices.

## Engineering safeguards

- Standard-library-only XLSX parsing (ZIP/XML); no new Python dependency or API key.
- HTTPS and exact host allowlists for the landing page and workbook, including redirect validation.
- Dynamic release-link discovery, bounded 3 MB HTML / 20 MB workbook responses, 20-second timeout.
- Maximum 120-month requested range; malformed rows and missing values are skipped, never zero-filled.
- Provider failure is isolated into an explicit `unavailable` status and does not abort the intelligence pipeline.
- Values are monthly nominal benchmark averages, not real-time/executable quotes. Source series may be revised.
- Attribution is retained in the report and dashboard (World Bank Pink Sheet, CC BY 4.0).

## Output

The report adds `commodity_data`, and Build 3.5 market analytics consumes its observations as independent `WB:` series. The dashboard renders the official source, monthly observations, units, status and attribution. Stooq remains opt-in and is not treated as a verified source for scheduled collection.

## Verification

Tests use a synthetic XLSX workbook fixture to verify workbook relationship resolution, shared strings, date filtering, missing-value handling, attribution, failure reporting and HTML escaping. The scheduled monitoring workflow also exercises the current official workbook endpoint; successful live retrieval must be confirmed from its run log before treating the provider as operational.
