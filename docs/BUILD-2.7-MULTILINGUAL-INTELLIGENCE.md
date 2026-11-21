# Build 2.7 — Global Source Expansion & Multilingual Intelligence

## Implemented
- Expanded the active sample catalog from two to four HTTPS feeds: BBC World and NPR World (English), ANTARA News Terkini and CNA Indonesia (Indonesian). The two Indonesian feed URLs are published in the publishers' RSS documentation. The monitoring workflow now runs when this catalog changes.
- Explicit source-language coverage in pipeline reports and the offline dashboard.
- Language labels normalize common forms such as `en-GB` and `id-ID`; missing language remains unknown.
- Research relevance supports a small deterministic English–Indonesian synonym vocabulary for selected concepts.
- Research candidates retain their declared language, publisher/source, country, URL, and evidence status.
- Unknown and unsupported language metadata remains visible rather than being guessed.

## Scope and limitations
The new feed entries are configured in `examples/feeds.sample.json` and will be checked by the scheduled monitoring workflow. A source endpoint's published RSS URL does not guarantee every later request will succeed. This build does not translate articles, detect language from article text, perform semantic/vector search, or discover and subscribe to arbitrary feeds. The bilingual vocabulary is intentionally small and auditable; it is not a general translation dictionary. Coverage counts reflect declared metadata and do not establish global representativeness. Feed endpoints should be reviewed and explicitly configured by the repository owner before being added.

## Validation
Run `python -m unittest discover -s tests -v`. CI is the authoritative runtime test environment for this repository.
