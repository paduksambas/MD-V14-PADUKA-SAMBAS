# MD V14 — Global Intelligence & Public Data Analytics Framework

An open research and public data intelligence framework for monitoring macro-economic signals, regional statistics, commodity trends, and structured news syndication models.

---

## 🌐 Official Network & Publications

This repository powers data modeling and syndicated feeds for the **Paduka Sambas** information network. Official verified publications and digital media channels:

* **Official News Portal:** [Paduka Sambas Media](https://padukasambas.blogspot.com/)
* **Official Facebook Channel:** [Paduka Sambas on Facebook](https://www.facebook.com/128057603730117)
* **Public Trend Dashboard:** [MD-V14 Live Dashboard](https://paduksambas.github.io/MD-V14-PADUKA-SAMBAS/)

---

## 🔬 Framework Architecture

MD V14 provides modular Python data adapters and deterministic analytic pipelines designed for:
- **Macroeconomic & Regional Intelligence:** Standardized connectors for BPS (Badan Pusat Statistik) regional dynamic tables, World Bank Indicators, and Frankfurter FX mid-market daily observations.
- **Commodity Price Discovery:** Nominal benchmark tracking from official World Bank Commodity Price Data (Pink Sheet).
- **Public Feed Normalization:** Schema version 1.0 JSON event registry with traceable provenance, URL hygiene, and multi-source corroboration metrics.
- **Offline Analytic Synthesis:** Deterministic knowledge graph linking and summary generation without unverified algorithmic assertions.

---

## 📁 Core Modules

- `mdv14/rss_collector.py` — Configurable RSS/Atom collection with URL hygiene and provenance validation.
- `mdv14/data_integration.py` — Versioned global record schema, source catalog validation, and metadata coverage.
- `mdv14/cross_source.py` — Exact-title grouping and entity tracking across source domains.
- `mdv14/trend_registry.py` — Signal normalization, stable IDs, and provenance preservation.
- `mdv14/economic_data.py` — Bounded World Bank Indicators API client with indicator allowlists.
- `mdv14/regional_intelligence.py` — BPS regional dynamic-table ingestion, indicator normalization, and descriptive spreads.
- `mdv14/commodity_data.py` — Monthly commodity benchmark parsing and normalization.
- `mdv14/dashboard.py` — Self-contained static HTML dashboard for data exploration.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Standard library dependencies only (no mandatory third-party runtime frameworks required for core pipeline).

### Running Unit Tests
```bash
python -m unittest discover -s tests -v
```

### Running Local Pipeline
```bash
python -m mdv14 examples/signals.sample.json \
  --output build/latest-report.json \
  --dashboard build/monitoring-dashboard.html
```

---

## 📄 License & Attribution

Distributed under the [MIT License](LICENSE). Maintained for academic research, data verification, and public feed syndication.
