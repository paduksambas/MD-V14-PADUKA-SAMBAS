# Build 1.4 — Persistent trend history

Build 1.4 adds a standard-library SQLite store for durable trend metadata and append-only score observations.

## Run

```bash
python -m mdv14 examples/signals.sample.json --database build/mdv14-history.sqlite3 --output build/history-report.json
python -m unittest discover -s tests -v
```

The CLI database option records each run's normalized signals, then attaches historical growth summaries to the report. Repeated runs must use the same database path to build history.

## Interpretation

- The stable signal key is derived from normalized title and URL.
- Every observation is retained; the trend row is upserted and tracks first/last seen and observation count.
- Growth compares the earliest and latest supplied scores. One observation is explicitly marked `insufficient_history`.
- A rising/falling label describes score movement only. It is not a forecast, probability, virality claim, or truth assessment.
- Existing JSON reports and the Build 1.3 pipeline remain usable without a database.
- SQLite history is local to the machine/path where the CLI runs. No cloud sync or automatic publishing is enabled.
