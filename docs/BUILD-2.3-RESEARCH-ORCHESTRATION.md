# Build 2.3 — Autonomous Research & Multi-Source Intelligence

## Delivered
Build 2.3 adds an auditable research orchestration layer over configured RSS/Atom feeds and manually supplied records. It produces a question-framed research report with literal keyword relevance, source and country diversity, collection health, evidence completeness, candidate records, research gaps, and suggested review steps.

## How to use
Run the existing feed-enabled CLI with your own JSON feed catalog (an array of objects with `id`, `name`, and HTTPS `url`) and local signals as needed:
```bash
python -m mdv14 --feeds path/to/your-feeds.json --output build/research-report.json
```
The Python API is:
```python
from mdv14.pipeline import collect_and_run
report = collect_and_run(feeds, extra_signals=signals, research_question="semiconductor supply chain")
```
The report includes `research` when a research question is provided.

## Boundaries
- Sources are limited to the configured feed catalog; no autonomous website discovery is claimed.
- Relevance is literal token overlap against titles and summaries, not semantic search.
- Feed collection remains HTTPS-only and subject to existing public-host, redirect, timeout, and response-size protections.
- Evidence completeness is metadata hygiene, not truth verification.
- Publisher and country diversity are based on supplied labels and do not establish editorial independence.
- No auto-publishing, external notifications, or autonomous consequential actions are enabled.

## Validation
Run `python -m unittest discover -s tests -v` from the repository root. Report runtime status only after executing the suite.
