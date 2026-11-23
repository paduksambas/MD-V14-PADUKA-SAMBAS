#!/usr/bin/env bash
set -euo pipefail

# Build a public, static dashboard. Only the HTML is published; the report JSON
# is kept in a temporary file outside the Pages output directory.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

OUTPUT_DIR="public"  # Fixed publish path; never let environment variables redirect cleanup.
mkdir -p "$OUTPUT_DIR"
# Publish only the generated dashboard. Clean the output directory to prevent
# accidental publication of leftover reports, databases, or previous build files.
find "$OUTPUT_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
REPORT="$(mktemp -t mdv14-public-report-XXXXXX.json)"
AIRTABLE_EXPORT="$(mktemp -t mdv14-airtable-bps-XXXXXX.json)"
trap 'rm -f "$REPORT" "$AIRTABLE_EXPORT"' EXIT

AIRTABLE_ARGS=(--regional-data "$AIRTABLE_EXPORT")
if [[ -n "${AIRTABLE_API_TOKEN:-}" ]]; then
  python scripts/airtable_bps.py --export-dashboard "$AIRTABLE_EXPORT"
else
  # The connected ChatGPT Airtable app is not available inside GitHub Actions.
  # Use the last reviewed Airtable snapshot as a safe fallback; refresh it from
  # Airtable when the repository PAT is not configured.
  cp examples/airtable-bps-dashboard.json "$AIRTABLE_EXPORT"
  echo "Airtable API token not configured in GitHub Actions; using the dated Airtable snapshot."
fi

python -m mdv14 \
  --feeds examples/feeds.sample.json \
  --output "$REPORT" \
  --dashboard "$OUTPUT_DIR/index.html" \
  --economic-countries ID,US,CN \
  --economic-start-year 2020 \
  "${AIRTABLE_ARGS[@]}"

test -s "$OUTPUT_DIR/index.html"
# Keep report JSON and databases out of the publishable directory.
if find "$OUTPUT_DIR" -type f ! -name 'index.html' -print -quit | grep -q .; then
  echo "Unexpected files in public output directory" >&2
  exit 1
fi
echo "Public dashboard built: $OUTPUT_DIR/index.html"
