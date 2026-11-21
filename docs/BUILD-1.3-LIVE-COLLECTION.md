# MD V14 — Build 1.3 Live Collection and Cross-Source Analysis

## Capabilities
- Configurable RSS 2.0 and Atom feed collection over HTTPS.
- Feed-level failure isolation, request timeout and response-size cap.
- RSS/Atom title, link, summary and publication-date extraction.
- Exact normalized-title grouping across distinct URL domains.
- Collected signals enter the existing registry, evidence hygiene, warning and daily-brief pipeline.

## Configure feeds
Edit `examples/feeds.sample.json` or create a private feed list:

```json
[
  {"name": "Example News", "url": "https://news.example/rss.xml"}
]
```

Only HTTPS feed URLs are accepted. Redirects are not followed. Localhost and non-public literal IP addresses are rejected. Feed endpoints should be trusted and reviewed before use.

## Run live collection
```bash
python -m mdv14 --feeds examples/feeds.sample.json --output build/live-report.json
```

Combine local signal JSON with RSS feeds:

```bash
python -m mdv14 examples/signals.sample.json --feeds examples/feeds.sample.json --output build/combined-report.json
```

## Cross-source interpretation
The engine groups exact normalized titles and counts distinct URL domains. It does not perform semantic matching, establish editorial independence, or verify the underlying claim. A matching headline across domains is an investigative lead, not proof.

## Limits
- Feed availability and content depend on publishers and network access at runtime.
- Some feeds may block automated clients, return malformed XML, or use nonstandard formats.
- RSS summaries may be publisher excerpts; open and inspect original articles for material claims.
- Scores from RSS collection default to zero until a separately validated scoring model is configured.
- No automatic publishing or outbound alerting is performed.
