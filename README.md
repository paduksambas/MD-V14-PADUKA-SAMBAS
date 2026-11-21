# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 2.1 — Global Intelligence Dashboard
- Build 2.0 — Global Intelligence Engine
- Build 1.9 — Safe RSS/Atom Article Links
- Python 3.11+; standard library only
- Tests: unittest; GitHub Actions workflow included

## Modules
- mdv14/rss_collector.py — configurable RSS/Atom collection with provenance extraction and safe article-link validation
- mdv14/data_integration.py — versioned global record schema, source catalog validation, metadata coverage
- mdv14/cross_source.py — exact-title grouping across source domains
- mdv14/trend_registry.py — signal normalization, stable IDs, provenance preservation
- mdv14/fact_check.py — metadata and URL hygiene (not truth verification)
- mdv14/source_intelligence.py — source provenance checklist without fabricated reputation scores
- mdv14/early_warning.py — heuristic warning bands
- mdv14/daily_brief.py — daily brief generator
- mdv14/pipeline.py — end-to-end orchestration
- mdv14/storage.py — atomic JSON storage
- mdv14/sqlite_store.py — persistent SQLite trend history and ordered observations
- mdv14/advanced_scoring.py — momentum, acceleration, anomaly and attention-potential indicators
- mdv14/global_intelligence.py — cross-country/topic summaries, history-based momentum, and explainable related-event discovery
- mdv14/dashboard.py — self-contained offline HTML analytics dashboard with global country/topic, rising-signal, and related-event views
- mdv14/__main__.py — CLI with optional history and dashboard output

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

## Build 2.1 Global Intelligence Dashboard
The offline HTML dashboard now includes global intelligence summary metrics, country and topic activity tables with average-score profiles, rising signals with history-based momentum, and related-event discovery candidates with their matching basis. All untrusted labels are HTML-escaped. The dashboard remains a static local report and does not publish or transmit data. See docs/BUILD-2.1-GLOBAL-DASHBOARD.md.

## Build 2.0 Global Intelligence Engine
The pipeline now emits `global_intelligence` with country and topic summaries, per-signal momentum when `score_history` is supplied, rising-signal candidates, and explainable related-event links based on explicit entities/topics or shared title terms. Missing geography remains `unknown`; no geography or topics are inferred. Related-event links are discovery hints, not causal findings or verified corroboration. Momentum is unavailable without historical score observations. This build analyzes supplied records and does not itself perform live global collection.

## Build 1.9 safe article links
RSS/Atom entries are retained only when their article URL uses HTTP or HTTPS, has a hostname, and contains no embedded credentials. Unsafe schemes and malformed links are skipped. This is URL hygiene, not publisher authentication or fact-checking. See docs/BUILD-1.9-SAFE-ARTICLE-LINKS.md.

## Build 1.8 global data integration
Source catalogs define stable IDs, publisher, source type, country, region, language, topics, and enabled state. Records use schema version 1.0 and preserve publication/collection timestamps and collection method. Reports include metadata coverage, including unknown fields. RSS/Atom records preserve author and category fields where available. See docs/BUILD-1.8-GLOBAL-DATA-INTEGRATION.md.

## Build 1.7 source assessment
Each signal includes a source_intelligence object with observable metadata checks. These are metadata observations only; no source reputation or automatic reliability/independence verdict is issued. See docs/BUILD-1.7-SOURCE-INTELLIGENCE.md.

## Integrity and safety
Feed collection requires configured feeds and an internet connection. Distinct domains do not establish editorial independence. Source metadata checks do not verify factual truth. Country and language are never inferred from domain names. Coverage describes supplied metadata, not representativeness. Scores, momentum, anomaly flags and warning levels are heuristics, not verified predictions. Dashboard output is local and static. No auto-publishing or external notifications are enabled.
