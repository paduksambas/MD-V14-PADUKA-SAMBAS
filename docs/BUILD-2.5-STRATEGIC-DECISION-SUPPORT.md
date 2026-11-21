# Build 2.5 — Global Intelligence Fusion & Strategic Decision Support

## Objective
Unify the existing MD V14 intelligence stages into a traceable queue that helps a human analyst decide which supplied records to review first.

## Implementation
- New module: `mdv14/strategic_decision.py`.
- Pipeline output: `strategic_decision`.
- Optional research context is fused after `--research-question` processing in `collect_and_run`.
- Every queue item retains the signal ID, title, source, original URL, country label, warning level, trend outlook, momentum, impact-dimension cues, evidence-completeness state, and scoring component breakdown.
- The report summarizes evidence/coverage gaps and counts existing global rising, predictive early-warning, and cross-border review candidates.

## Transparent prioritization
The priority indicator is a weighted mean of available components:
- Supplied score: 55%.
- Observed score momentum indicator: 20%, mapped to a bounded scale using `50 + momentum`.
- Existing keyword impact-dimension cues: 15%, capped at four dimensions.
- Evidence-gap review cue: 10%.

Weights are renormalized when a component is unavailable. This makes the result deterministic and explainable, but it does not make the score a measurement of event severity, probability, or strategic importance. The score ranks analyst review order only. Existing warning and impact labels are shown as context rather than counted again as independent evidence.

## Safety and limitations
- No new web discovery, external fact verification, causal inference, geopolitical forecasting, or autonomous decision/action is performed.
- Momentum and warning indicators may share underlying score inputs; they are not independent corroboration.
- Keyword impact dimensions can miss context or produce false matches.
- Missing geography and evidence remain explicit gaps; they are not inferred.
- Human analysts must review original sources, dates, primary documents, uncertainty, and affected stakeholders before acting.

## Verification
Run the full suite with:

```bash
python -m unittest discover -s tests -v
```

GitHub Actions runs the same command on Python 3.11 for pushes and pull requests to `main`.
