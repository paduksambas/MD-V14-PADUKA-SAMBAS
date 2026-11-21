# Build 4.1 — BPS Public Export Import (No API Key)

Build 4.1 imports publicly downloaded BPS table exports without requiring a BPS WebAPI key. Supported inputs are CSV, XLSX and normalized JSON. CSV and XLSX parsing use Python's standard library; XLSX reads the first worksheet only.

## Usage

1. Open an official BPS statistics table or the [BPS Query Builder](https://www.bps.go.id/id/query-builder).
2. Select the indicator, geography, period and characteristics needed; download the table as CSV or Excel when that export option is offered.
3. Save the export in the repository or runner workspace, for example `data/bps-regional.csv`.
4. Copy `examples/bps-public-export.sample.json` to `examples/bps-public-export.json` and set the exact column headings used by the downloaded file. Set `defaults` for fixed metadata such as `level`, `indicator_code`, `period` only when those values apply to every row. Required fields are region_code, region_name, level, indicator_code, period and value.
5. Run:

```bash
python -m mdv14 --bps-public-export data/bps-regional.csv \
  --bps-public-config examples/bps-public-export.json \
  --output build/report.json --dashboard build/dashboard.html
```

No API key is read for this import. The optional Build 4.0 WebAPI connector remains separate and still requires a key and explicit domain/variable/period IDs.

## Provenance and validation

The report adds `bps_public_export` with file SHA-256, filename, format, source URL, rows read, accepted observations and rejected-row reasons. Imported observations are combined with any normalized `--regional-data` JSON and optional Build 4.0 API observations before regional analysis. A rejected row is not silently filled or guessed.

The importer enforces a 10 MB file limit and 100,000-row limit. XLSX reads the first worksheet and stored cell values; formulas are not recalculated. Column mapping is explicit—there is no assumption that every BPS download uses identical headers. The source URL and metadata must be reviewed against the actual table.

## Important limitations

- This is a public-file importer, not a universal automatic BPS table crawler. The user or a separately configured workflow must obtain the export file.
- Query Builder pages may require interactive table selection; do not treat the page URL itself as a downloadable CSV endpoint.
- Compare only identical indicator definitions, units, periods and administrative levels. Check missing regions, boundary changes and revisions.
- The importer does not infer regional values from national totals, generate forecasts, establish causal effects or make policy recommendations.

Official references: [BPS Query Builder](https://www.bps.go.id/id/query-builder), [BPS public data download guidance](https://ppid.bps.go.id/app/konten/0000/Layanan-BPS.html), [BPS WebAPI documentation](https://webapi.bps.go.id/documentation/).
