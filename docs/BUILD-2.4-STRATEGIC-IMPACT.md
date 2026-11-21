# Build 2.4 — Strategic Impact Analysis & Geopolitical Intelligence

## Scope
Build 2.4 adds transparent strategic-impact triage to records already collected and normalized by MD V14. It labels potential economic, security, diplomatic, societal, technology, and environmental dimensions using deterministic keyword matches in supplied titles and summaries.

It also surfaces cross-border review candidates only when two records have different explicitly supplied country labels and share an explicitly supplied entity or topic. This is a research queue, not evidence of causality, alliance, conflict, influence, or editorial independence.

## Output
- `strategic_impact` in pipeline reports
- Per-signal impact dimensions, supplied country/entity/topic labels, score-based attention band, metadata completeness label, and human review questions
- Aggregated dimension and attention counts
- Cross-border review candidates with their shared metadata basis

## Method and safeguards
- No missing country, actor, or topic is inferred.
- Attention bands use the existing supplied score: 0–39 monitor, 40–69 moderate, 70–100 high attention.
- Metadata confidence describes completeness only, not truth or publisher credibility.
- Keyword matches can miss context or produce false positives.
- No live external collection, causal inference, probability, forecast, or autonomous decision is performed.
- Human verification against primary sources is required before decisions.

## Tests
Run `python -m unittest discover -s tests -v`.
