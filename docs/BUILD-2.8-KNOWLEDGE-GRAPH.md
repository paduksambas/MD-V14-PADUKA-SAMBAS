# Build 2.8 — Advanced Entity Recognition & Cross-Language Knowledge Graph

## Implemented
- Deterministic matching against a curated alias catalog with selected English and Indonesian names for countries, intergovernmental organizations, international organizations, and companies.
- Explicit `entities`, `topics`, and country metadata are represented as graph nodes and linked to source-record events.
- Related records are linked when they share a recognized entity, supplied topic, or explicitly supplied country.
- Each node records whether its evidence came from an explicit metadata field, a title/summary alias match, or a source record. Edges retain supporting record IDs.
- The report exposes total node/edge counts and bounded node/edge lists.

## Limitations
This is a curated alias matcher, not general-purpose machine-learning NER. Alias collisions can produce false positives. The graph does not prove causality, influence, alliances, source independence, or factual truth. It does not translate articles or infer unknown entities, countries, or topics. Human review of matches and source records is mandatory.

## Validation
Run `python -m unittest discover -s tests -v`. GitHub Actions provides the authoritative runtime test result.
