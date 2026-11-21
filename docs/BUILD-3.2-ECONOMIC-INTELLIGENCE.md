# Build 3.2 — Global Economic Intelligence & Strategic Market Impact

## Scope

Build 3.2 adds a deterministic economic-sector review layer to the existing MD V14 pipeline. It classifies supplied signal titles and summaries into seven review sectors:

- Energy
- Commodities & Mining
- Trade & Supply Chains
- Finance & Macroeconomy
- Technology & Semiconductors
- Agriculture & Food
- Transport & Logistics

The classifier uses a curated English/Indonesian token vocabulary. A record may appear in more than one sector. Each review candidate preserves its signal ID, title, source, URL, supplied score, explicitly named countries/entities/topics, warning level, and evidence metadata.

## Pipeline and dashboard

The pipeline emits `economic_intelligence` with sector summaries, potential review channels, country mentions, coverage counts, methodology, limitations, and a traceable priority review queue. The offline dashboard renders sector coverage and source-linked records. CLI output includes the build version, number of classified signals, and represented sectors.

The monitoring workflow is configured to rerun when `mdv14/economic_intelligence.py`, pipeline, dashboard, or sample feeds change.

## Interpretation and limitations

- Sector assignment is a keyword-based discovery cue, not semantic classification or a verified economic finding.
- Keyword matching can miss relevant items and produce false positives.
- A sector's average score is the average of supplied MD V14 signal scores; it is not a measured market return, economic impact, risk, or severity.
- Country labels and entity names are copied from supplied metadata and are not independently verified.
- The module does not ingest live asset prices, exchange rates, yields, company fundamentals, trade statistics, or commodity benchmarks.
- Sector association does not prove causality or demonstrate that an event moved a market.
- No forecasts, investment recommendations, financial advice, or automated trading signals are produced.
- Human review against primary sources and appropriate market/economic datasets is required before drawing conclusions.

## Tests

Run the full suite with:

```bash
python -m unittest discover -s tests -v
```
