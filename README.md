## Build 4.2 Private Local Dashboard & Live WIB Clock

The dashboard HTML now includes a live WIB clock (Asia/Jakarta), the report-generation timestamp, collection-cycle health, and the status reported by each configured data source. The clock updates every second in the browser; the underlying intelligence report is refreshed only when a new collection cycle completes.

**Private delivery:** this repository is currently public. Therefore the scheduled workflow deliberately does not upload the report or dashboard as GitHub Actions artifacts and does not deploy GitHub Pages. The dashboard is generated as a standalone local HTML file. Generate it on a trusted machine using the normal CLI, then open the HTML file locally:

```bash
python -m mdv14 --feeds examples/feeds.sample.json \
  --output build/latest-report.json \
  --dashboard build/monitoring-dashboard.html \
  --economic-countries ID,US,CN
```

The HTML is self-contained and can be opened on a computer, tablet, or phone after transferring the file securely. Do not place private reports in a public repository or public hosting service. A remotely accessible password-protected dashboard requires a private repository/hosting arrangement and explicit access-control configuration; it is not enabled by this build.

The scheduled GitHub Actions collection remains every six hours. A live clock does not mean the underlying sources are real-time. Source statuses are displayed as reported by their adapters; missing or unconfigured providers are not presented as current data.
## Build 4.1 BPS Public Export Import (No API Key)
Regional intelligence can now ingest official BPS public table exports in CSV, XLSX or normalized JSON without a WebAPI key. Use `--bps-public-export` with `--bps-public-config` to supply an explicit column mapping and metadata; the report records file SHA-256, source URL, accepted rows and rejected rows. XLSX reads the first worksheet only. This is a file-import workflow, not an automatic crawler or a direct Query Builder download. See docs/BUILD-4.1-BPS-PUBLIC-EXPORT-IMPORT.md and examples/bps-public-export.sample.json.

# MD V14 — Paduka Sambas Global Trend Intelligence

Repositori pengembangan sistem riset tren global, intelijen strategis, analisis dampak, dan briefing.

## Status
- Build 4.0 — Automated BPS Regional Dynamic-Table Connector (bounded, configurable domain/variable/period requests)
- Build 3.9 — Indonesia Regional Intelligence (BPS region catalog + traceable province/regency indicator comparisons)
- Build 3.8 — Indonesia Strategic Economic Intelligence (World Bank macro indicators + global commodity review channels)
- Build 3.7 — Official Commodity Intelligence (World Bank Pink Sheet, no API key)
- Build 3.6 — Public Equity & Commodity Market Data (no-key Stooq daily observations)
- Build 3.5 — Cross-Asset Market Analytics (descriptive change and observed-step volatility)
- Build 3.4 — Global Financial Markets Intelligence (no-key Frankfurter FX + optional FRED API)
- Build 3.3 — Dedicated Economic Data Sources & Market Intelligence Integration (World Bank Indicators API)
- Build 3.2 — Global Economic Intelligence & Strategic Market Impact (keyword-based sector review cues)
- Build 3.1 — Global Geopolitical Intelligence Map & Interactive Country Risk Explorer (review-priority explorer)
- Build 3.0 — Global Strategic Intelligence Command Center
- Build 2.9 — AI Analyst & Autonomous Strategic Reporting (deterministic analyst report composer)
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
- mdv14/analyst_report.py — executive brief, traceable findings, uncertainty register, and human review actions
- mdv14/command_center.py — unified operational state, strategic posture, source coverage, and priority review queue
- mdv14/country_explorer.py — country-centroid plotting, explicit metadata aggregation, and traceable country-level review profiles
- mdv14/economic_intelligence.py — curated English/Indonesian sector cues for energy, commodities/mining, trade/supply chains, finance/macroeconomy, technology/semiconductors, agriculture/food, and transport/logistics
- mdv14/economic_data.py — bounded World Bank Indicators API client with country/year validation, allowlisted indicators, provenance, and missing-data preservation
- mdv14/market_data.py — no-key Frankfurter daily FX reference-rate adapter plus optional FRED market observations adapter with fixed allowlists, key redaction, request bounds, and explicit missing-data status
- mdv14/market_analytics.py — per-series retrospective change and observed-step volatility summaries without interpolation, cross-asset scoring, or forecasts
- mdv14/public_assets.py — bounded no-key Stooq daily close adapter for selected equity indices and commodity futures (opt-in)
- mdv14/commodity_data.py — dynamic World Bank Pink Sheet workbook discovery, standard-library XLSX parsing, and monthly benchmark normalization
- mdv14/indonesia_intelligence.py — Indonesia-only macro indicator summaries and qualitative global commodity review channels
- mdv14/regional_intelligence.py — BPS region-domain discovery, bounded dynamic-table retrieval, normalized regional indicator profiles, like-for-like rankings and descriptive spreads
- mdv14/dashboard.py — self-contained offline command-center dashboard with interactive country explorer, operational, strategic, analyst, and global coverage views
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

## Build 4.0 Automated BPS Regional Table Connector

Optional BPS dynamic-table retrieval is enabled by `--bps-tables-config`. The JSON configuration identifies each exact domain, variable and period ID; requests are restricted to the official HTTPS BPS WebAPI host and capped at 100 per run. Only unambiguous single numeric cells are normalized into the regional intelligence pipeline. Set the private `BPS_API_KEY` as a GitHub Actions secret and create `examples/bps-regional-tables.json` from the sample template after confirming table metadata in the official BPS documentation. The sample is not automatically queried. Build 4.0 does not discover indicators or enumerate all regions automatically; coverage must be configured in deliberate batches that respect BPS rate limits. See docs/BUILD-4.0-BPS-REGIONAL-TABLE-CONNECTOR.md.

## Build 3.7 Official Commodity Intelligence
The report now includes `commodity_data` from the official World Bank Commodity Price Data (Pink Sheet) monthly workbook. The current XLSX link is discovered from the World Bank Commodity Markets page on each run; parsing uses only the Python standard library and requires no API key. Selected series include crude oil, natural gas, coal, gold, silver, copper, aluminum, coffee, palm oil, wheat, maize, rice, and urea. Values are monthly nominal global benchmark averages with source units and attribution; missing cells remain missing. The data are not local Indonesian prices or live quotes. Build 3.5 analytics consumes each commodity series independently. See docs/BUILD-3.7-OFFICIAL-COMMODITY-INTELLIGENCE.md.

## Build 3.6 Public Equity & Commodity Market Data
The report now includes `public_asset_data`, available as an opt-in fetch without an API key from Stooq's daily CSV endpoint (`--enable-public-assets`). The fixed symbol allowlist covers the S&P 500, NASDAQ Composite, DAX, Nikkei 225, WTI crude-oil futures, and gold futures. It is disabled in scheduled monitoring because live GitHub Actions validation received non-CSV quota/challenge responses from Stooq. Each instrument is fetched independently; failed symbols are reported without suppressing successful instruments, and missing observations are not zero-filled. These are provider-supplied daily closes, not real-time or executable quotes. Futures values may depend on contract-roll conventions. This adapter does not include government-bond yields; optional FRED remains available only when configured. Build 3.5 analytics now includes these observations while keeping every series independent. See docs/BUILD-3.6-PUBLIC-ASSET-DATA.md.

## Build 3.5 Cross-Asset Market Analytics
The report now includes `market_analytics`, which combines returned no-key Frankfurter observations and any available optional FRED observations, then analyzes each series independently. It reports first-to-latest absolute and percentage changes, direction, and population standard deviation of observed-step percentage changes when enough observations exist. It does not annualize volatility, combine unlike units, interpolate missing dates, or produce trading signals or forecasts. The dashboard displays the same traceable summaries. The CLI defaults to a 30-day market-data window so that changes can be compared across observations; custom dates remain available. This is descriptive analysis of observations returned in the current run; irregular observation intervals and provider coverage remain limitations. See docs/BUILD-3.5-MARKET-ANALYTICS.md.

## Build 3.4 Global Financial Markets Intelligence
The default no-key market adapter retrieves daily USD reference rates for IDR, EUR, and CNY from the public Frankfurter API; it requires no account or API key. It reports reference/mid-market rates, not intraday trading quotes. World Bank macroeconomic observations remain available independently. An additional optional FRED adapter can retrieve selected FX series, equity indices, U.S. Treasury yields, WTI crude, and gold only when `FRED_API_KEY` is configured; FRED absence does not block market-data collection. CLI date bounds are `--market-start-date` and `--market-end-date` (public FX range is bounded to 367 days). Values are historical/reference observations—not guaranteed executable quotes, trading signals, forecasts, or investment advice. See docs/BUILD-3.4-FINANCIAL-MARKETS.md.

## Build 3.3 Dedicated Economic Data Sources & Market Intelligence Integration
The CLI accepts `--economic-countries ID,US,CN --economic-start-year 2020` to retrieve published macroeconomic observations from the official World Bank Indicators API. The scheduled monitoring workflow enables this for Indonesia, the United States, and China and adds the observations to the JSON report and HTML dashboard. Initial allowlisted series cover GDP growth, consumer-price inflation, trade as a share of GDP, net energy imports, and merchandise exports/imports. Requests are restricted to `api.worldbank.org`, response sizes and timeouts are bounded, country codes and years are validated, and missing values remain missing. The data are historical observations with reporting lags—not real-time market quotes, forecasts, or proof of causal market impact. See docs/BUILD-3.3-ECONOMIC-DATA-INTEGRATION.md.

## Build 3.2 Global Economic Intelligence & Strategic Market Impact
The pipeline emits `economic_intelligence` with traceable records grouped into energy, trade/supply chain, commodities, technology/semiconductors, financial markets, and macroeconomy. Matching uses a curated English-Indonesian token vocabulary across supplied titles and summaries. A signal may appear in multiple sectors. These are discovery cues—not live market prices, macroeconomic statistics, measured impact, causal attribution, financial advice, or forecasts. Input scores remain supplied heuristic scores; publisher labels do not prove independence. See docs/BUILD-3.2-ECONOMIC-INTELLIGENCE.md.

## Build 3.1 Global Geopolitical Intelligence Map & Country Explorer
The pipeline emits `country_explorer` with country-level signal counts, average supplied scores, review-priority counts, warning counts, and traceable source records. The dashboard includes an interactive longitude/latitude plot with approximate curated country-centroid references; selecting a marker or country label opens its associated signals. Countries without a supported centroid remain visible in the table but are not plotted. The explorer only groups explicitly supplied country labels; it does not infer event location or territorial boundaries. Review-priority counts are analyst triage cues, not geopolitical risk ratings, threat severity, or probabilities. See docs/BUILD-3.1-COUNTRY-EXPLORER.md.

## Build 3.0 Global Strategic Intelligence Command Center
The pipeline now emits `command_center`, consolidating the latest configured collection-cycle status, strategic review posture, warning indicators, evidence-review workload, country/topic coverage leaders, priority review queue, analyst-report counts, and decision gates. The dashboard places this command-center summary at the top and retains detailed global, source, knowledge-graph, and analyst sections. The command center is a deterministic view of existing report fields; it does not create new intelligence, assign an independent geopolitical risk rating, verify claims, or make decisions. A healthy feed cycle means endpoints responded, not that content is accurate. Scheduled collection is periodic, not continuous. See docs/BUILD-3.0-COMMAND-CENTER.md.

## Build 2.9 Analyst & Strategic Reporting
The pipeline emits `analyst_report` with an executive summary, traceable priority findings, metadata-coverage indicators, explicit uncertainty/gaps, strategic context, and recommended human review actions. The dashboard renders these sections. This is deterministic synthesis of existing MD V14 assessments—not a connected generative AI model, independent research, fact verification, or autonomous policy decision. Metadata completeness is not factual confidence. Human approval is required before escalation, publication, or action. See docs/BUILD-2.9-ANALYST-REPORTING.md.

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
