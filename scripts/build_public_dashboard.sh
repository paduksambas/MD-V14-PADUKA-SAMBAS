#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

OUTPUT_DIR="public"
mkdir -p "$OUTPUT_DIR"
find "$OUTPUT_DIR" -mindepth 1 -maxdepth 1 -exec rm -rf {} +

if [[ -n "${VERCEL:-}" ]]; then
  echo "Vercel build detected. Fetching latest verified dashboard from GitHub Pages..."
  if curl -fsSL "https://paduksambas.github.io/MD-V14-PADUKA-SAMBAS/" -o "$OUTPUT_DIR/index.html" && [[ -s "$OUTPUT_DIR/index.html" ]]; then
    echo "Successfully mirrored live dashboard to $OUTPUT_DIR/index.html"
    exit 0
  fi
  echo "Fallback to local build if mirror fetch failed."
fi
REPORT="$(mktemp -t mdv14-public-report-XXXXXX.json)"
AIRTABLE_EXPORT="$(mktemp -t mdv14-airtable-bps-XXXXXX.json)"
trap 'rm -f "$REPORT" "$AIRTABLE_EXPORT"' EXIT

AIRTABLE_ARGS=(--regional-data "$AIRTABLE_EXPORT")
if [[ -n "$(printenv AIRTABLE_API_TOKEN 2>/dev/null || true)" ]]; then
  python scripts/airtable_bps.py --export-dashboard "$AIRTABLE_EXPORT"
else
  cp examples/airtable-bps-dashboard.json "$AIRTABLE_EXPORT"
  echo "Airtable API token not configured in GitHub Actions; using the dated Airtable snapshot."
fi

# Optional Build 4.1 public-file importer. The file must be downloaded from an
# official BPS table/export and its exact column mapping must be configured.
BPS_PUBLIC_ARGS=()
BPS_PUBLIC_CONFIG="examples/bps-public-export.json"
BPS_PUBLIC_EXPORT=""
for candidate in \
  data/bps-public-export.csv \
  data/bps-public-export.xlsx \
  data/bps-public-export.json; do
  if [[ -f "$candidate" ]]; then
    BPS_PUBLIC_EXPORT="$candidate"
    break
  fi
done

if [[ -n "$BPS_PUBLIC_EXPORT" ]]; then
  if [[ ! -f "$BPS_PUBLIC_CONFIG" ]]; then
    echo "BPS public export file found, but $BPS_PUBLIC_CONFIG is missing." >&2
    echo "Copy examples/bps-public-export.sample.json, then map the exact exported column names and source table URL." >&2
    exit 1
  fi
  BPS_PUBLIC_ARGS=(--bps-public-export "$BPS_PUBLIC_EXPORT" --bps-public-config "$BPS_PUBLIC_CONFIG")
  echo "BPS public export import enabled: $BPS_PUBLIC_EXPORT"
else
  echo "BPS public export import not configured; no downloaded BPS export file found in data/."
fi

BPS_TABLE_ARGS=()
if [[ -f "examples/bps-regional-tables.json" && -n "$(printenv BPS_API_KEY 2>/dev/null || true)" ]]; then
  BPS_TABLE_ARGS=(--bps-tables-config "examples/bps-regional-tables.json")
  echo "BPS regional tables config enabled"
fi

python -m mdv14 \
  --feeds examples/feeds.sample.json \
  --output "$REPORT" \
  --dashboard "$OUTPUT_DIR/index.html" \
  --economic-countries ID,US,CN \
  --economic-start-year 2020 \
  "${AIRTABLE_ARGS[@]}" \
  "${BPS_TABLE_ARGS[@]}" \
  "${BPS_PUBLIC_ARGS[@]}"

test -s "$OUTPUT_DIR/index.html"
if find "$OUTPUT_DIR" -type f ! -name 'index.html' -print -quit | grep -q .; then
  echo "Unexpected files in public output directory" >&2
  exit 1
fi
echo "Public dashboard built: $OUTPUT_DIR/index.html"
