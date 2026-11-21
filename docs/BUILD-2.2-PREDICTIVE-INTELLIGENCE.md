# Build 2.2 — Predictive Intelligence & Early Warning

## Scope
Build 2.2 adds an explainable short-horizon scenario indicator using only supplied score history. It calculates a recent average change from up to three score deltas, extends that change over a configurable number of future observations, clamps the result to 0–100, and maps the scenario to existing warning bands.

## Output
Each signal receives `predictive_outlook` with:
- history sufficiency and trend direction (stable, rising, accelerating rise, declining);
- current and scenario score;
- observation horizon (not days or dates);
- current and projected warning bands;
- an early-warning flag when the scenario crosses the elevated threshold;
- an estimated number of observations to the elevated threshold when the trend is positive.

## Guardrails
- Fewer than two valid observations produce no projection.
- Invalid and non-finite observations are ignored.
- Projection is a simple heuristic scenario, not a probability, dated forecast, causal finding, or guarantee.
- Observation intervals may be irregular; the system does not assume daily cadence.
- Human review remains required for elevated or critical scenarios.
- No autonomous notifications or external actions are enabled.

## Validation
Run `python -m unittest discover -s tests -v` from the repository root. Runtime test results must be reported only after actual execution.
