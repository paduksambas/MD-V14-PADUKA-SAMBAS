# Build 1.1 — Daily Intelligence Brief

## Purpose
Turn collected trend signals into a compact, repeatable daily editorial brief. This stage consumes signals supplied by the existing radar/early-warning workflow; it does not pretend to collect live data itself.

## Output
- Brief date and title
- Number of received and included signals
- Prioritized top signals
- Evidence completeness flag for each signal
- Count of signals requiring source review
- Category summary
- Explicit methodology note

## Ranking
1. Signals with a title, source name, and URL rank before signals with incomplete evidence.
2. Within the same evidence tier, the supplied score ranks descending.
3. Title is the deterministic tie-breaker.
4. The supplied score is clamped to 0–100 and is not represented as independently verified.

## Required signal fields
- `title` (or `topic`)
- `source`
- `url`
- `summary`
- `category`
- `score`

Only title is required for inclusion. Missing source or URL is surfaced for editorial review, not silently repaired.

## Run locally
From the repository root:

```bash
python -m unittest discover -s tests -v
```

## Scope and safety
This module is deterministic and uses only Python's standard library. It does not fetch websites, fabricate citations, publish content, or claim that a trend is verified. Live collection and fact-checking remain separate workflow stages.
