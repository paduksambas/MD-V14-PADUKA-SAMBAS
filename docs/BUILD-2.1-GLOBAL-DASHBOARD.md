# Build 2.1 — Global Intelligence Dashboard

## Delivered

The existing offline HTML dashboard now presents the Build 2.0 analysis output:
- Global overview metrics: signals analyzed, represented countries/topics, rising signals, and related-event candidates.
- Country activity: signal count, average score, and a compact score profile.
- Topic activity: signal count, average score, and a compact score profile.
- Rising signals: country, topics, score, and historical momentum.
- Related-event discovery: both event titles, country labels, and the relationship basis.

## Usage

Generate a dashboard from the CLI:

```bash
python -m mdv14 examples/signals.sample.json \
  --database build/mdv14-history.sqlite3 \
  --output build/history-report.json \
  --dashboard build/trend-dashboard.html
```

Open the generated `build/trend-dashboard.html` locally in a browser. The dashboard is static and self-contained.

## Safety and interpretation

- All displayed report values and labels are HTML-escaped.
- Country and topic groupings use supplied metadata only.
- Momentum requires supplied/persisted historical observations.
- Related-event candidates are based on shared metadata or title terms and do not prove causality, truth, or independent corroboration.
- The dashboard does not fetch external data, transmit reports, or auto-publish content.

## Validation

Dashboard tests cover global sections, empty reports, and escaping of untrusted text. Run the full suite:

```bash
python -m unittest discover -s tests -v
```

A test commit is not proof of a passing runtime suite; consult the GitHub Actions run for an actual execution result.
