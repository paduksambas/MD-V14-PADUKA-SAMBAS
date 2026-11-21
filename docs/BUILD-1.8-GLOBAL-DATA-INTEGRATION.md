# Build 1.8 — Global Intelligence Data Integration

## Delivered
Build 1.8 introduces a versioned normalized record schema and structured source catalog metadata for RSS/Atom and manually supplied JSON signals.

### Standard record fields
- data_schema_version, source_id, publisher, source_type
- country, region, language, topics
- published_at, collected_at
- collection_method, feed_url

Existing title, source, URL, summary, category, and score fields remain intact. Missing geography, language, and publisher values remain unknown. No country, language, or source identity is inferred from a domain.

### Source catalog
Definitions can declare stable ID, name, HTTPS feed URL, country, region, language, publisher, source type, topics, and enabled state. Invalid or duplicate IDs and non-HTTPS URLs are reported as configuration errors. Disabled sources are not fetched.

### Coverage reporting
Reports include coverage by country, region, language, source type, and publisher, including unknown counts. Coverage is descriptive metadata, not proof of global representativeness.

### RSS/Atom enrichment
RSS and Atom parsing preserves author and category/topic metadata where available. Existing HTTPS-only, public-host, no-redirect, response-size, and timeout safeguards remain.

### Limitations
- No paid data-provider API integration or claim of broad global coverage.
- Feed content and source metadata are not fact-checked by normalization.
- Source country is publisher/source metadata, not necessarily the event location.
- RSS availability depends on configured feeds and network access.
- No auto-publication or outbound notifications are enabled.
