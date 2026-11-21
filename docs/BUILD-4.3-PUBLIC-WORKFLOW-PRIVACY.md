# Build 4.3 — Public Workflow Privacy Hardening

## Purpose
Keep the MD V14 source repository public for continued GitHub-based development without exposing generated intelligence reports through routine scheduled workflow outputs.

## Changes
- Removed Actions cache restore/save steps so the scheduled workflow does not persist generated trend-history databases.
- Suppressed routine CLI JSON metrics from the public workflow log.
- Replaced detailed monitoring metrics in the GitHub Actions job summary with a generic execution/privacy notice.
- Kept report and dashboard files transient on the hosted runner only.
- Continued to avoid artifact uploads and GitHub Pages deployment.

## What this does and does not mean
- The source code repository remains public and can still be updated through the authorized GitHub connection.
- This is a reduction of report exposure through normal workflow outputs, not a guarantee that all execution metadata is private.
- The runner is temporary execution infrastructure, not authenticated dashboard hosting.
- No password-protected remote dashboard has been deployed.
- Do not add confidential source files, personal records, API keys, or private reports to tracked files, workflow summaries, or public issues.
- API keys belong only in GitHub Actions Secrets; never place them in JSON configuration files or commit history.

## Schedule and data freshness
The workflow continues on its existing six-hour schedule. It does not retain generated reports or trend history between scheduled runs. A live WIB clock in a locally generated dashboard is independent of report freshness: report data changes only when a new report is generated.

## Validation
The workflow itself is the validation mechanism for this change. Review the latest GitHub Actions run after commit and confirm that it succeeds, that its summary is generic, and that no report/dashboard artifacts are produced.
