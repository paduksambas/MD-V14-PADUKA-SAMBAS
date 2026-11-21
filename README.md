# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 1.5 — Offline Trend Intelligence Dashboard + SQLite persistent history
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
- `mdv14/sqlite_store.py` — persistent SQLite trend history
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

Open `build/trend-dashboard.html` in a browser. Reuse the same database path on later runs to build score history. A single observation is not labeled as a rising or falling trend.

See [Build 1.5 documentation](docs/BUILD-1.5-TREND-DASHBOARD.md) and [Build 1.4 persistent history](docs/BUILD-1.4-PERSISTENT-HISTORY.md).

## Run live RSS/Atom collection
```bash
python -m mdv14 --feeds examples/feeds.sample.json --output build/live-report.json
```

Optional local signals can be combined with feeds:
```bash
python -m mdv14 examples/signals.sample.json --feeds examples/feeds.sample.json --output build/combined-report.json
```

## Integrity and safety
Feed collection uses HTTPS, bounded response size and timeout, and does not follow redirects. Cross-source counts are not proof of truth or editorial independence. Metadata checks are not fact verification. Scores and warning levels are heuristics, not verified predictions. Review original sources, dates, context and independent reporting before drawing conclusions. Dashboard output is local and static. No auto-publishing or external notifications are enabled.
