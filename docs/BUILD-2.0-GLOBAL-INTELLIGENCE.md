# Build 2.0 — Global Intelligence Engine

## Delivered

- Country and topic summaries based only on supplied metadata.
- Per-signal momentum assessment using optional `score_history`.
- Rising-signal candidates when historical momentum is positive.
- Related-event discovery based on explicit shared entities/topics or at least two meaningful shared title terms.
- Relationship explanations, cross-country indicator, and explicit non-causality notice.
- Integration into `run_pipeline()` under the `global_intelligence` report key.

## Data contract

Each input signal may include:
- `country`, `region`, `topics`, `category`
- `entities` (explicitly supplied entity labels)
- `score` and optional `score_history` (list of objects containing `score`)

Unknown geography remains `unknown`. Topic analysis uses explicit topics, then category, then `Unclassified`. The engine does not infer country, entities, or historical scores.

## Interpretation safeguards

- Group averages and scores are descriptive summaries, not forecasts.
- Momentum requires at least two valid historical score observations.
- Related-event links are discovery candidates; shared terms or metadata do not establish causality, independent reporting, or truth.
- The engine analyzes records already supplied to the pipeline; it does not perform live collection itself.

## Tests

Run the complete suite from the repository root:

```bash
python -m unittest discover -s tests -v
```

Build 2.0 adds `tests/test_global_intelligence.py` and extends the pipeline integration test. Runtime execution must be confirmed by the test runner or CI; committing tests is not evidence that they passed.
