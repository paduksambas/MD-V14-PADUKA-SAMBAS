# Build 1.5 — Trend Intelligence Dashboard

Build 1.5 creates a self-contained, offline HTML dashboard from a standard MD V14 JSON report.

## Run

```bash
python -m mdv14 examples/signals.sample.json \
  --database build/mdv14-history.sqlite3 \
  --output build/history-report.json \
  --dashboard build/trend-dashboard.html
python -m unittest discover -s tests -v
```

Open the generated HTML file in a browser. It includes signal counts, average supplied score, source-review count, history coverage, warning distribution, category distribution, and a trend table with historical score movement when available.

## Security and interpretation

- The dashboard is static and self-contained; it loads no external scripts, fonts, stylesheets, or tracking resources.
- Dynamic report text is HTML-escaped before rendering.
- The dashboard is local output and is not automatically uploaded or published.
- Scores and warning levels are heuristic inputs, not verified predictions.
- Historical score movement is descriptive, not a forecast or probability.
- Source metadata checks do not establish factual truth.
