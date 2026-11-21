# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 1.6 — Advanced Trend Intelligence (momentum, acceleration, anomaly review)
- Python 3.11+; standard library only
- Tests: unittest; GitHub Actions workflow included

## Modules
- `mdv14/rss_collector.py` — configurable RSS/Atom feed collector
- `mdv14/cross_source.py` — exact-title grouping across source domains
- `mdv14/trend_registry.py` — signal normalization and deduplication
- `mdv14/fact_check.py` — metadata and URL hygiene (not truth verification)
- `mdv14/early_warning.py` — heuristic warning bands
- `mdv14/daily_brief.py` — daily brief generator
- `mdv14/pipeline.py` — end-to-end orchestration
- `mdv14/storage.py` — atomic JSON storage
- `mdv14/sqlite_store.py` — persistent SQLite trend history and ordered observations
- `mdv14/advanced_scoring.py` — explainable momentum, acceleration, anomaly and attention-potential indicators
- `mdv14/dashboard.py` — self-contained offline HTML analytics dashboard
- `mdv14/__main__.py` — CLI with optional history and dashboard output
- `examples/` — sample feeds and signals
- `tests/` — automated tests

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Generate JSON report, persistent history, and dashboard
```bash
python -m mdv14 examples/signals.sample.json \
  --database build/mdv14-history.sqlite3 \
  --output build/history-report.json \
  --dashboard build/trend-dashboard.html
```

Open `build/trend-dashboard.html` in a browser. Reuse the same database path on later runs to build score history. Momentum needs two observations; acceleration needs three; anomaly review needs at least five. Without enough observations, the report states that history is insufficient rather than inventing a direction.

## Build 1.6 indicator definitions
- **Momentum:** latest supplied score minus the previous supplied score.
- **Acceleration:** latest score delta minus the preceding delta; requires at least three observations.
- **Anomaly review:** compares the latest delta against the median of at least three prior deltas; flags deviations beyond the larger of 15 score points or three median absolute deviations.
- **Attention potential index:** current score plus half the latest momentum, with the adjustment capped at ±10 points and the final index bounded to 0–100. It is a heuristic indicator, not a probability or forecast.
- **Confidence/data sufficiency:** explicitly reports insufficient, low, or moderate history; it is not a statistical confidence interval.

All indicators operate on supplied scores and observation order. They do not prove causation, virality, factual truth, or future outcomes. Distinct source domains do not establish editorial independence. Review original sources and context before drawing conclusions.

See [Build 1.6 documentation](docs/BUILD-1.6-ADVANCED-TREND-INTELLIGENCE.md), [Build 1.5 dashboard](docs/BUILD-1.5-TREND-DASHBOARD.md), and [Build 1.4 persistent history](docs/BUILD-1.4-PERSISTENT-HISTORY.md).

## Run live RSS/Atom collection
```bash
python -m mdv14 --feeds examples/feeds.sample.json --output build/live-report.json
```

Optional local signals can be combined with feeds:
```bash
python -m mdv14 examples/signals.sample.json --feeds examples/feeds.sample.json --output build/combined-report.json
```

## Integrity and safety
Feed collection uses HTTPS, bounded response size and timeout, and does not follow redirects. Cross-source counts are not proof of truth or editorial independence. Metadata checks are not fact verification. Scores, momentum, anomaly flags and warning levels are heuristics, not verified predictions. Review original sources, dates, context and independent reporting before drawing conclusions. Dashboard output is local and static. No auto-publishing or external notifications are enabled.
