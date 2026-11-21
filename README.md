# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 2.8 — Advanced Entity Recognition & Cross-Language Knowledge Graph
- Build 2.7 — Global Source Expansion & Multilingual Intelligence
- Build 2.6 — Live Global Intelligence Monitoring & Automated Intelligence Dashboard
- Build 2.5 — Global Intelligence Fusion & Strategic Decision Support
- Build 2.4 — Strategic Impact Analysis & Geopolitical Intelligence
- Build 2.3 — Autonomous Research & Multi-Source Intelligence
- Build 2.2 — Predictive Intelligence & Early Warning
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
- mdv14/predictive_intelligence.py — bounded observation-horizon scenarios and threshold-crossing early-warning candidates
- mdv14/research_orchestrator.py — question-framed multi-source relevance, collection health, source diversity, evidence gaps, and audit steps
- mdv14/strategic_impact.py — keyword-based impact dimensions, explicit-metadata cross-border review candidates, attention bands, and human review prompts
- mdv14/strategic_decision.py — unified explainable review queue combining supplied scores, observed momentum, impact cues, evidence gaps, and source traceability
- mdv14/monitoring.py — collection-cycle health, feed status, and publisher-timestamp freshness indicators
- mdv14/language_intelligence.py — explicit language metadata coverage and supported-language declarations
- mdv14/knowledge_graph.py — curated multilingual entity aliases and traceable event/entity/topic/country graph
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

## Build 2.8 Advanced Entity Recognition & Cross-Language Knowledge Graph
The pipeline now emits knowledge_graph with curated English/Indonesian aliases for selected countries, organizations, and companies; explicit entity/topic/country metadata; event nodes; and shared-entity/topic/country discovery links. Nodes preserve evidence basis and edges preserve supporting record IDs. This is deterministic alias matching, not general-purpose AI named-entity recognition. Ambiguous matches require human review; graph links do not prove truth, causality, influence, or source independence. See docs/BUILD-2.8-KNOWLEDGE-GRAPH.md.

## Build 2.7 Global Source Expansion & Multilingual Intelligence
The pipeline now reports language coverage from explicitly declared source/record metadata, including unknown values. Research relevance supports a small deterministic English–Indonesian lexical map for selected terms, while preserving each candidate's declared language and provenance. This is not article translation, automatic language detection, semantic search, or arbitrary source discovery. The active sample catalog now includes BBC World and NPR World (English), plus ANTARA News Terkini and CNA Indonesia (Indonesian); each source remains explicitly configured with language and country metadata. The monitoring workflow reruns when this feed catalog changes. See docs/BUILD-2.7-MULTILINGUAL-INTELLIGENCE.md.

## Build 2.6 Live Global Intelligence Monitoring & Automated Intelligence Dashboard
The scheduled GitHub Actions workflow `.github/workflows/monitoring.yml` runs RSS/Atom collection every six hours and can also be started manually from the Actions tab. It uses the explicitly configured `examples/feeds.sample.json`, persists SQLite trend history between successful runs through GitHub Actions cache, and uploads a JSON report plus offline HTML dashboard as a 14-day artifact. The report includes feed health and publisher-timestamp freshness indicators, while the dashboard exposes the latest collection cycle and strategic review queue. This is periodic collection—not continuous surveillance. Workflow execution depends on GitHub Actions availability and repository settings; publisher timestamps and feed responses may be incomplete. Feed health does not verify article truth. See docs/BUILD-2.6-LIVE-MONITORING.md.

## Build 2.5 Global Intelligence Fusion & Strategic Decision Support
The pipeline now emits `strategic_decision`, a unified human-review queue that fuses existing signal scores, observed momentum, keyword impact dimensions, and evidence-completeness gaps. Each item retains its signal ID, source, URL, country, warning/outlook labels, and transparent scoring components. Weights are renormalized when an input component is unavailable. Global, predictive, research, and strategic-impact summaries are context indicators—not independent confirmations. The priority score ranks review order only; it is not severity, probability, a forecast, or an automated policy recommendation. Optional research gaps from `--research-question` are included after collection. See docs/BUILD-2.5-STRATEGIC-DECISION-SUPPORT.md.

## Build 2.4 Strategic Impact Analysis & Geopolitical Intelligence
The pipeline now emits `strategic_impact` with keyword-based potential impact dimensions (economic, security, diplomatic, societal, technology, environmental), score-based attention bands, metadata-completeness labels, and cross-border review candidates. Cross-border candidates require different explicitly supplied country labels plus a shared supplied entity or topic. These are analyst triage cues only: they do not establish causality, alliances, conflicts, impact probabilities, forecasts, source independence, or truth. Missing geography and actors are not inferred. Human verification is required. See docs/BUILD-2.4-STRATEGIC-IMPACT.md.

## Build 2.3 Autonomous Research & Multi-Source Intelligence
For configured RSS/Atom sources, pass `--research-question` with `--feeds` to add an auditable `research` section to the JSON report. Example: `python -m mdv14 --feeds path/to/your-feeds.json --research-question "semiconductor supply chain" --output build/research-report.json`. The report ranks records using literal keyword overlap in titles and summaries, summarizes feed health and metadata coverage, and lists research gaps and human review steps. It does not discover arbitrary websites, perform semantic search, verify truth, or publish findings. The feed JSON must be an array of source objects containing `id`, `name`, and HTTPS `url` fields; include optional publisher, country, language, topics, and enabled metadata. The Python API accepts `research_question` in `collect_and_run`. See docs/BUILD-2.3-RESEARCH-ORCHESTRATION.md.

## Build 2.2 Predictive Intelligence & Early Warning
The pipeline now attaches a `predictive_outlook` to each signal and reports evaluated histories, insufficient histories, and threshold-crossing candidates in `predictive_summary`. It extends the mean of up to three latest supplied score changes over a configurable number of future observations; observation units are not calendar days. Fewer than two valid observations yield no projection. These are bounded heuristic scenarios, not probabilities, dated forecasts, causal findings, or guarantees. Elevated and critical scenarios require human review. No autonomous notifications are enabled. See docs/BUILD-2.2-PREDICTIVE-INTELLIGENCE.md.

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
