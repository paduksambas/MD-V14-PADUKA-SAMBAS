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
trap 'rm -f "$REPORT"' EXIT

python -m mdv14 \
  --feeds examples/feeds.sample.json \
  --output "$REPORT" \
  --dashboard "$OUTPUT_DIR/index.html" \
  --economic-countries ID,US,CN \
  --economic-start-year 2020

test -s "$OUTPUT_DIR/index.html"
# Keep report JSON and databases out of the publishable directory.
if find "$OUTPUT_DIR" -type f ! -name 'index.html' -print -quit | grep -q .; then
  echo "Unexpected files in public output directory" >&2
  exit 1
fi
echo "Public dashboard built: $OUTPUT_DIR/index.html"
