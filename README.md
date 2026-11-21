# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 1.3 — RSS/Atom collection + cross-source analysis + integrated brief
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
- `mdv14/storage.py`, `mdv14/__main__.py` — JSON storage and CLI
- `examples/` — sample feeds and signals
- `tests/` — automated tests

## Run tests
```bash
python -m unittest discover -s tests -v
```

## Run live RSS/Atom collection
```bash
python -m mdv14 --feeds examples/feeds.sample.json --output build/live-report.json
```

Optional local signals can be combined with feeds:
```bash
python -m mdv14 examples/signals.sample.json --feeds examples/feeds.sample.json --output build/combined-report.json
```

## Integrity and safety
Feed collection uses HTTPS, bounded response size and timeout, and does not follow redirects. Cross-source counts are not proof of truth or editorial independence. Metadata checks are not fact verification. Review original sources, dates, context and independent reporting before drawing conclusions. No auto-publishing or external notifications are enabled.
