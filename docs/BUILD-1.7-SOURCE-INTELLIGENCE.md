# Build 1.7 — Source Intelligence & Reliability Assessment

## Delivered
Build 1.7 adds a transparent source-provenance checklist to every signal and includes it in JSON reports and daily brief entries.

### Observable checks
- Source name and article URL presence/shape
- HTTPS transport
- Publication timestamp format
- Author attribution
- Summary presence
- Supplied citation list
- Explicitly declared primary-source flag
- Supplied corrections, ownership, and editorial-policy URLs

Source-profile fields are optional input metadata. The system does not browse or independently validate those policies and links.

### Status labels
- `insufficient_source_metadata`: source name or article URL is missing/invalid
- `limited_metadata_human_review_required`: a small subset of metadata checks passed
- `partially_documented_human_review_required`: more provenance fields are present
- `metadata_rich_human_review_required`: many metadata fields are present, but human review remains required

### Independence and corroboration
Exact normalized-title grouping and distinct domains remain discovery context only. Domain counts do not establish editorial independence, independent sourcing, accuracy, or truth.

### Deliberate safeguards
- No automated source reputation score is issued.
- `reliability_verdict` and `independence_verdict` remain `not_assessed`.
- A larger metadata checklist is not a higher factual-truth score.
- Source profile claims and URLs are user-supplied and are not independently verified.
- Review original reporting, primary documents, dates, corrections, ownership, and independent evidence manually.

## Output
Each signal contains `source_intelligence`; the report contains `source_intelligence_summary`. The daily brief copies the assessment for each included signal.
