# Build 2.6 — Live Global Intelligence Monitoring & Automated Dashboard

## What is delivered
- `mdv14/monitoring.py` summarizes each collection cycle, feed health, item counts, and publication-time freshness.
- `collect_and_run` adds a `monitoring` object to reports created from configured feeds.
- The dashboard adds the latest cycle health and the strategic decision review queue.
- `.github/workflows/monitoring.yml` schedules collection every six hours and supports manual dispatch.
- The workflow restores/saves the SQLite history cache and uploads JSON and HTML outputs as a 14-day artifact.

## Running manually
From the repository root:

```bash
python -m mdv14 --feeds examples/feeds.sample.json \
  --database build/mdv14-history.sqlite3 \
  --output build/latest-report.json \
  --dashboard build/monitoring-dashboard.html
```

Or open GitHub → Actions → Scheduled global intelligence monitoring → Run workflow.

## Retrieving outputs
Open the completed monitoring workflow run and download its `mdv14-monitoring-<run-number>` artifact. It contains:
- `latest-report.json`: signals, provenance, collection health, warning assessments, strategic impact and decision queue.
- `monitoring-dashboard.html`: a self-contained dashboard that can be opened locally in a browser.

Artifacts are retained for 14 days. SQLite history is cached between successful workflow runs; cache retention and availability are controlled by GitHub Actions.

## Schedule and source configuration
The default schedule is `17 */6 * * *` (UTC), approximately four cycles per day. Edit `examples/feeds.sample.json` to add, remove, or disable HTTPS RSS/Atom feeds. Keep only sources that the project is authorized to access and review feed terms and rate limits. The collector enforces HTTPS, public-host validation, no redirects, request timeouts, and response-size limits.

## Interpretation and limitations
- This is periodic scheduled collection, not continuous surveillance or a real-time alerting service.
- GitHub Actions scheduling can be delayed or disabled by platform/repository settings.
- Feed health means the endpoint was fetched and parsed; it does not establish accuracy, editorial independence, or source credibility.
- Freshness uses publisher-provided timestamps where parseable. Missing, malformed, future, or inaccurate timestamps are not silently corrected.
- Global coverage is limited to the configured feeds; the sample catalog is intentionally small and is not representative of all countries or languages.
- The HTML dashboard and report are workflow artifacts; this build does not deploy a public website, publish content, or send external notifications.
- Human review remains required before decisions or external communication.

## Tests
```bash
python -m unittest discover -s tests -v
```
