# Build 1.6 — Advanced Trend Intelligence

## Delivered
Build 1.6 extends persistent score history with deterministic indicators that explain how supplied trend scores are changing.

### Indicators
1. **Momentum** is the latest score minus the preceding score. Two observations are required.
2. **Acceleration** is the latest score delta minus the preceding delta. Three observations are required.
3. **Anomaly review** compares the latest delta with the median of at least three earlier deltas. A change is flagged when its absolute deviation exceeds the larger of 15 score points or three median absolute deviations. Five observations are therefore required.
4. **Attention potential index** adds half the latest momentum to the current score, limits the adjustment to ±10 points, and bounds the result to 0–100. It is not a probability, forecast, or claim that a trend will go viral.
5. **Data sufficiency and confidence labels** disclose whether there are enough observations. “Moderate” means the minimum history for momentum and acceleration exists; it is not a statistical confidence interval.

## CLI
```bash
python -m mdv14 examples/signals.sample.json \
  --database build/mdv14-history.sqlite3 \
  --output build/history-report.json \
  --dashboard build/trend-dashboard.html
```

Run the command repeatedly with the same database to accumulate observations. The first run cannot produce momentum. Acceleration becomes available on the third observation; anomaly evaluation begins on the fifth.

## Limitations and safeguards
- Indicators use supplied scores and ordered observations only. They do not establish causal effects, factual truth, editorial independence, or future outcomes.
- A flagged anomaly is a review prompt, not proof of manipulation or virality.
- Missing history is reported as insufficient; no synthetic observations or predictions are generated.
- Scores remain bounded and deterministic. The report preserves the existing source-review workflow.
- The dashboard remains static and local. No auto-publishing or outbound notifications are introduced.
