# MD V14 — Build 1.2 Integrated Pipeline

## Stage flow
1. **Trend Registry** normalizes signals and deduplicates by stable hash of title + source URL.
2. **Evidence Hygiene** checks required metadata and HTTP(S) URL shape. It does not verify factual truth.
3. **Early Warning** classifies supplied 0–100 scores as normal, watch, elevated, or critical.
4. **Daily Intelligence Brief** ranks evidence-complete signals first, then score and title.
5. **JSON storage and CLI** load signal arrays and atomically save generated reports.
6. **Human review** remains mandatory for material claims and elevated/critical warnings.

## Input contract
Each signal may provide `title` (or `topic`), `source`, `url`, `summary`, `category`, and `score`. Missing titles are rejected by the registry. Missing source metadata or malformed URLs are preserved and flagged.

## Run
From the repository root:

```bash
python -m unittest discover -s tests -v
python -m mdv14 examples/signals.sample.json --output build/report.json
```

Replace the example placeholders with source-derived information before treating a report as intelligence output. The second sample item is deliberately incomplete to demonstrate the evidence-review path.

## Default warning bands
- Normal: below 40
- Watch: 40 to below 60
- Elevated: 60 to below 80
- Critical: 80 to 100

Thresholds are configurable. They are heuristics, not probabilities or verified forecasts.

## Operational boundaries
- This package does not collect live trends or scrape sources.
- URL validation checks syntax only; it does not fetch or authenticate the source.
- Scores are supplied by upstream systems and are not independently validated.
- The registry is in-memory for each run; JSON input/output provides file-based handoff, not concurrent multi-user storage.
- No external notifications or publication are triggered.
