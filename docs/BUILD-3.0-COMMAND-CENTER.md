# Build 3.0 — Global Strategic Intelligence Command Center

## Purpose
Build 3.0 consolidates existing MD V14 pipeline outputs into one command-center object and places it at the top of the offline HTML dashboard.

## Command-center output
- Operational state: operational, degraded, unavailable, or not_assessed, based on the configured collection-cycle status.
- Strategic posture: insufficient_data, priority_review_required, watch_and_review, or routine_review, based only on existing warning and strategic review indicators.
- Collection cycle: attempted/succeeded/failed feed counts, collected items, publisher timestamp freshness and unknown timestamps.
- Coverage: analyzed records and the leading declared country/topic groupings.
- Priority queue: traceable signal ID, title, country, source, URL, warning and review priority.
- Analyst summary: finding, uncertainty and human-action counts.
- Decision gates: source verification, independence/timing/metadata checks, alternative explanations, and human authorization.

## Dashboard and CLI
The offline dashboard presents the Build 3.0 command center before detailed monitoring, multilingual coverage, knowledge graph, analyst report, strategic review queue, and global trend views. CLI JSON summary includes command-center build, posture, and operational state. The full report JSON includes the complete `command_center` object.

## Limitations and safeguards
This is deterministic aggregation of existing MD V14 outputs, not new research, an independent geopolitical risk rating, a generative AI model, fact verification, or autonomous decision-making. Priority and warning bands are triage cues, not threat severity or probability. Country/topic coverage is not globally representative. Feed health indicates endpoint collection only. Scheduled collection is periodic, not continuous. Human authorization is required before escalation, publication, or action.

## Validation
Run `python -m unittest discover -s tests -v`. The GitHub Actions Python 3.11 workflow is the authoritative test result.
