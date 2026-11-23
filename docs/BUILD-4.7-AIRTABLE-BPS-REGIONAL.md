# PADUKA Regional BPS Data via Airtable

## Airtable source

- Base: **PADUKA — Data Regional BPS Sambas**
- Table: **Observasi Regional**
- Base ID: `appL6SjqOg5V1wQxy`
- Table ID: `tblLqOKctDBUIGPyC`
- Repository snapshot: `examples/airtable-bps-regional.json`

The snapshot in this repository was read from the connected Airtable base on 2026-11-23. It contains the two records that were present in **Observasi Regional** at that time.

## Validation policy

Airtable is the structured source of record. Each row retains its `Status Validasi`:

- `Valid`: eligible for regional profiles, rankings and spread calculations.
- `Belum ditinjau` or `Menunggu validasi`: displayed in the Airtable review table, excluded from statistics.
- `Ditolak` or an unknown validation state: excluded and counted as rejected.

A value is never promoted to `Valid` by the import process. A human reviewer must update **Status Validasi** in Airtable after checking the original BPS table, period, definition and unit.

## Current snapshot

As of 2026-11-23, the connected base contained:

| Region | Indicator | Period | Value | Airtable validation |
|---|---|---:|---:|---|
| Kabupaten Sambas | TPT (variable 163) | 2024 | 4.99 Persen | Belum ditinjau |
| Kabupaten Sambas | EPR (variable 168) | 2024 | 69.15 Persen | Belum ditinjau |

The values are sourced from BPS WebAPI, but the Airtable observation records explicitly say they still need to be checked against the original BPS publication/table. They therefore appear in the dashboard review table and do not contribute to rankings yet.

## Refreshing the repository snapshot

The GitHub Actions runner cannot use the Airtable app connection installed in a ChatGPT session. The connected Airtable tool can read the base, but that connection is not automatically available to GitHub Pages or GitHub Actions.

To refresh the static dashboard snapshot:
1. Read the latest rows from the Airtable **Observasi Regional** table.
2. Replace the observations in `examples/airtable-bps-regional.json` using the field mapping documented by the file's existing keys.
3. Preserve the exact Airtable validation status; do not infer or default it to `Valid`.
4. Commit the updated snapshot. The public dashboard build and scheduled monitoring workflows will consume it.

Only the static JSON snapshot is committed; Airtable credentials and tokens must never be committed. The snapshot contains public regional statistical values and their validation labels, not credentials or private notes.

## Dashboard behavior

The dashboard reports both **Data regional BPS** and **Airtable BPS** source status. When all available Airtable observations are pending review, the status is `pending_validation`, rather than incorrectly claiming that no Airtable data exists. Pending records are shown separately from validated rankings.
