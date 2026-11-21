# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 1.7 — Source Intelligence & Provenance Assessment
- Python 3.11+; standard library only
- Tests: unittest; GitHub Actions workflow included

## Modules
- `mdv14/rss_collector.py` — configurable RSS/Atom feed collector
- `mdv14/cross_source.py` — exact-title grouping across source domains
- `mdv14/trend_registry.py` — signal normalization, stable IDs, and provenance preservation
- `mdv14/fact_check.py` — metadata and URL hygiene (not truth verification)
- `mdv14/source_intelligence.py` — source provenance checklist without fabricated reputation scores
- `mdv14/early_warning.py` — heuristic warning bands
- `mdv14/daily_brief.py` — daily brief generator
- `mdv14/pipeline.py` — end-to-end orchestration
- `mdv14/storage.py` — atomic JSON storage
- `mdv14/sqlite_store.py` — persistent SQLite trend history and ordered observations
- `mdv14/advanced_scoring.py` — explainable momentum, acceleration, anomaly and attention-potential indicators
- `mdv14/dashboard.py` — self-contained offline HTML analytics dashboard
- `mdv14/__main__.py` — CLI with optional history and dashboard output

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Generate report, persistent history, and dashboard
```bash
python -m mdv14 examples/signals.sample.json \
  --database build/mdv14-history.sqlite3 \
  --output build/history-report.json \
  --dashboard build/trend-dashboard.html
```

## Build 1.7 source assessment
Each signal includes a `source_intelligence` object with observable metadata checks: source name, URL, HTTPS, publication time, author, summary, supplied citations, primary-source declaration, and optional corrections/ownership/editorial-policy URLs. These are metadata observations only. The system deliberately does not assign a reputation score or automatic reliability/independence verdict. See [Build 1.7 documentation](docs/BUILD-1.7-SOURCE-INTELLIGENCE.md).

## Build 1.6 indicators
Momentum requires two observations; acceleration requires three; anomaly review requires at least five. The attention potential index is a heuristic, not a probability or forecast. See [Build 1.6 documentation](docs/BUILD-1.6-ADVANCED-TREND-INTELLIGENCE.md).

## Integrity and safety
Feed collection requires configured feeds and an internet connection. Distinct domains do not establish editorial independence. Source metadata checks do not verify factual truth or source reputation. Scores, momentum, anomaly flags and warning levels are heuristics, not verified predictions. Review original sources, dates, context and independent reporting before drawing conclusions. Dashboard output is local and static. No auto-publishing or external notifications are enabled.
