# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 1.4 — SQLite persistent trend history + score-growth tracking (alongside Build 1.3 collection and cross-source analysis)
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
- `mdv14/storage.py` — atomic JSON storage\n- `mdv14/sqlite_store.py` — persistent SQLite trend metadata and append-only score observations\n- `mdv14/__main__.py` — CLI with optional database history
- `examples/` — sample feeds and signals
- `tests/` — automated tests

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Run with persistent trend history\n\n```bash\npython -m mdv14 examples/signals.sample.json --database build/mdv14-history.sqlite3 --output build/history-report.json\n```\n\nUse the same database path on later runs to build score history. A single observation is not labeled as a rising or falling trend.\n\nSee [Build 1.4 documentation](docs/BUILD-1.4-PERSISTENT-HISTORY.md).\n\n## Run live RSS/Atom collection
```bash
python -m mdv14 --feeds examples/feeds.sample.json --output build/live-report.json
```

Optional local signals can be combined with feeds:
```bash
python -m mdv14 examples/signals.sample.json --feeds examples/feeds.sample.json --output build/combined-report.json
```

## Integrity and safety
Feed collection uses HTTPS, bounded response size and timeout, and does not follow redirects. Cross-source counts are not proof of truth or editorial independence. Metadata checks are not fact verification. Review original sources, dates, context and independent reporting before drawing conclusions. No auto-publishing or external notifications are enabled.
