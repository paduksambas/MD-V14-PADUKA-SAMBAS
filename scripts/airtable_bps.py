#!/usr/bin/env python3
"""Synchronize official BPS regional observations with the PADUKA Airtable base.

The GitHub Actions runner uses a narrowly scoped Airtable PAT stored only in
AIRTABLE_API_TOKEN. The ChatGPT Airtable connection is not exposed to runners.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

AIRTABLE_API = "https://api.airtable.com/v0"
DEFAULT_BASE_ID = "appL6SjqOg5V1wQxy"
OBSERVATIONS_TABLE_ID = "tblLqOKctDBUIGPyC"
SYNC_LOG_TABLE_ID = "tbl1kM3ARXHE9aCVD"
TIMEOUT_SECONDS = 20
MAX_RECORDS = 1000
BATCH_SIZE = 10
PENDING_STATUS = "Belum ditinjau"
VALID_STATUS = "Valid"


def _api_request(
    token: str,
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    query: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Call Airtable without ever logging the bearer token or request headers."""
    if not token or not token.strip():
        raise ValueError("AIRTABLE_API_TOKEN is not configured")
    url = AIRTABLE_API + path
    if query:
        url += "?" + urllib.parse.urlencode(query)
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={
            "Authorization": "Bearer " + token.strip(),
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "PADUKA-BPS-Airtable-Sync/1.0",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read(2_000_001)
    except urllib.error.HTTPError as exc:
        # Do not include the request object, headers, or token in an error message.
        raise RuntimeError(f"Airtable API returned HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Airtable API request failed ({type(exc).__name__})") from None
    if len(raw) > 2_000_000:
        raise RuntimeError("Airtable API response exceeded the 2 MB safety limit")
    try:
        result = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise RuntimeError("Airtable API returned an invalid JSON response") from None
    if not isinstance(result, dict) or "error" in result:
        raise RuntimeError("Airtable API returned an error response")
    return result


def _list_all_records(token: str, base_id: str, table_id: str) -> list[dict[str, Any]]:
    path = f"/{base_id}/{table_id}"
    records: list[dict[str, Any]] = []
    offset: str | None = None
    for _ in range(10):
        query: dict[str, str] = {"pageSize": "100"}
        if offset:
            query["offset"] = offset
        payload = _api_request(token, "GET", path, query=query)
        page = payload.get("records")
        if not isinstance(page, list):
            raise RuntimeError("Airtable list response did not contain a records array")
        records.extend(item for item in page if isinstance(item, dict))
        if len(records) > MAX_RECORDS:
            raise RuntimeError("Airtable table exceeded the 1,000-record sync safety limit")
        offset = payload.get("offset")
        if not offset:
            return records
    raise RuntimeError("Airtable pagination exceeded the 10-page safety limit")


def _valid_number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    number = float(value)
    return number if math.isfinite(number) else None


def _observation_fields(item: dict[str, Any], value: float, validation: str) -> tuple[str, dict[str, Any]]:
    region_code = str(item.get("region_code") or "").strip()
    region_name = str(item.get("region_name") or "").strip()
    level = str(item.get("level") or "").strip()
    indicator_code = str(item.get("indicator_code") or "").strip()
    indicator_name = str(item.get("indicator_name") or indicator_code).strip()
    period = str(item.get("period") or "").strip()
    variable_id = str(item.get("bps_variable_id") or indicator_code).strip()
    period_id = str(item.get("bps_period_id") or "").strip()
    if not all((region_code, region_name, indicator_code, indicator_name, period, variable_id)):
        raise ValueError("required BPS observation metadata is missing")
    if level not in {"province", "regency_city"}:
        raise ValueError("BPS observation has an unsupported administrative level")
    key = "|".join((region_code, indicator_code, period))
    fields: dict[str, Any] = {
        "Kunci Observasi": key,
        "Kode Domain BPS": region_code,
        "Nama Wilayah": region_name,
        "Level Wilayah": level,
        "Kode Variabel BPS": variable_id,
        "Kode Indikator": indicator_code,
        "Nama Indikator": indicator_name,
        "Periode": period,
        "Nilai": value,
        "Satuan": str(item.get("unit") or ""),
        "Sumber": str(item.get("source") or "BPS WebAPI"),
        "URL Sumber": str(item.get("source_url") or "https://webapi.bps.go.id/documentation/"),
        "Tanggal Diambil": date.today().isoformat(),
        "Status Validasi": validation,
        "Catatan": (
            f"Domain API BPS {region_code}; variable ID {variable_id}; "
            f"period ID {period_id or 'not supplied'}. "
            "Periksa publikasi/tabel BPS asli sebelum memakai nilai untuk keputusan."
        ),
    }
    province_code = str(item.get("province_code") or "").strip()
    if province_code:
        fields["Kode Provinsi"] = province_code
    return key, fields


def sync_bps_observations(
    report: dict[str, Any],
    token: str,
    *,
    base_id: str = DEFAULT_BASE_ID,
) -> dict[str, Any]:
    bps = report.get("bps_regional_tables") or {}
    observations = bps.get("observations", [])
    if not isinstance(observations, list):
        raise ValueError("bps_regional_tables.observations must be an array")
    if len(observations) > 100:
        raise ValueError("BPS observation batch exceeds the 100-row safety limit")
    if not observations:
        return {
            "status": "no_data", "received": 0, "created": 0,
            "updated": 0, "unchanged": 0, "rejected": 0,
        }

    existing_rows = _list_all_records(token, base_id, OBSERVATIONS_TABLE_ID)
    existing: dict[str, dict[str, Any]] = {}
    for row in existing_rows:
        fields = row.get("fields") or {}
        key = str(fields.get("Kunci Observasi") or "")
        if key:
            if key in existing:
                raise RuntimeError("Airtable has duplicate Kunci Observasi values; manual cleanup is required")
            existing[key] = row

    creates: list[dict[str, Any]] = []
    updates: list[dict[str, Any]] = []
    unchanged = 0
    rejected = 0
    seen_input_keys: set[str] = set()
    for item in observations:
        if not isinstance(item, dict):
            rejected += 1
            continue
        value = _valid_number(item.get("value"))
        if value is None:
            rejected += 1
            continue
        try:
            key, base_fields = _observation_fields(item, value, PENDING_STATUS)
        except ValueError:
            rejected += 1
            continue
        if key in seen_input_keys:
            rejected += 1
            continue
        seen_input_keys.add(key)
        old = existing.get(key)
        if old:
            old_fields = old.get("fields") or {}
            old_value = _valid_number(old_fields.get("Nilai"))
            same_value = old_value is not None and math.isclose(old_value, value, rel_tol=1e-9, abs_tol=1e-9)
            comparable_fields = (
                "Kode Domain BPS", "Nama Wilayah", "Level Wilayah",
                "Kode Variabel BPS", "Kode Indikator", "Nama Indikator",
                "Periode", "Satuan",
            )
            same_metadata = all(
                str(old_fields.get(field) or "").strip() == str(base_fields.get(field) or "").strip()
                for field in comparable_fields
            )
            unchanged_observation = same_value and same_metadata
            old_status = str(old_fields.get("Status Validasi") or PENDING_STATUS)
            base_fields["Status Validasi"] = old_status if unchanged_observation else PENDING_STATUS
            if unchanged_observation:
                unchanged += 1
            updates.append({"id": old["id"], "fields": base_fields})
        else:
            creates.append({"fields": base_fields})

    path = f"/{base_id}/{OBSERVATIONS_TABLE_ID}"
    for start in range(0, len(creates), BATCH_SIZE):
        _api_request(token, "POST", path, payload={"records": creates[start:start + BATCH_SIZE]})
    for start in range(0, len(updates), BATCH_SIZE):
        _api_request(token, "PATCH", path, payload={"records": updates[start:start + BATCH_SIZE]})

    written = len(creates) + len(updates)
    status = "partial" if rejected else ("success" if written else "no_change")
    return {
        "status": status,
        "received": len(observations),
        "created": len(creates),
        "updated": len(updates),
        "unchanged": unchanged,
        "rejected": rejected,
    }


def export_validated_observations(
    token: str,
    output_path: str | Path,
    *,
    base_id: str = DEFAULT_BASE_ID,
) -> dict[str, Any]:
    records = _list_all_records(token, base_id, OBSERVATIONS_TABLE_ID)
    observations: list[dict[str, Any]] = []
    rejected = 0
    for row in records:
        fields = row.get("fields") or {}
        if fields.get("Status Validasi") != VALID_STATUS:
            continue
        value = _valid_number(fields.get("Nilai"))
        required = (
            fields.get("Kode Domain BPS"), fields.get("Nama Wilayah"),
            fields.get("Level Wilayah"), fields.get("Kode Indikator"),
            fields.get("Nama Indikator"), fields.get("Periode"),
        )
        if value is None or any(not str(part or "").strip() for part in required):
            rejected += 1
            continue
        observations.append({
            "region_code": str(fields["Kode Domain BPS"]),
            "region_name": str(fields["Nama Wilayah"]),
            "level": str(fields["Level Wilayah"]),
            "province_code": str(fields.get("Kode Provinsi") or ""),
            "indicator_code": str(fields["Kode Indikator"]),
            "indicator_name": str(fields["Nama Indikator"]),
            "period": str(fields["Periode"]),
            "value": value,
            "unit": str(fields.get("Satuan") or ""),
            "source": str(fields.get("Sumber") or "BPS WebAPI"),
            "source_url": str(fields.get("URL Sumber") or "https://webapi.bps.go.id/documentation/"),
        })
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"observations": observations}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"exported": len(observations), "rejected": rejected, "status": "available" if observations else "no_validated_records"}


def _write_sync_log(
    token: str,
    result: dict[str, Any],
    *,
    base_id: str = DEFAULT_BASE_ID,
) -> bool:
    started = os.environ.get("PADUKA_SYNC_STARTED_AT") or datetime.now(timezone.utc).isoformat()
    finished = datetime.now(timezone.utc).isoformat()
    run_id = os.environ.get("GITHUB_RUN_ID") or ("manual-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    repo = os.environ.get("GITHUB_REPOSITORY", "paduksambas/MD-V14-PADUKA-SAMBAS")
    server = os.environ.get("GITHUB_SERVER_URL", "https://github.com")
    run_url = f"{server}/{repo}/actions/runs/{os.environ['GITHUB_RUN_ID']}" if os.environ.get("GITHUB_RUN_ID") else ""
    status_map = {"success": "Berhasil", "partial": "Parsial", "no_data": "Gagal", "no_change": "Berhasil"}
    fields = {
        "Run ID": f"airtable-sync-{run_id}",
        "Waktu Mulai": started,
        "Waktu Selesai": finished,
        "Sumber": "BPS WebAPI → Airtable",
        "Status": status_map.get(str(result.get("status")), "Gagal"),
        "Jumlah Dibaca": int(result.get("received", 0)),
        "Jumlah Ditambahkan": int(result.get("created", 0)),
        "Jumlah Diperbarui": int(result.get("updated", 0)),
        "Jumlah Ditolak": int(result.get("rejected", 0)),
        "Ringkasan": (
            f"Status {result.get('status')}; received {result.get('received', 0)}, "
            f"created {result.get('created', 0)}, updated {result.get('updated', 0)}, "
            f"unchanged {result.get('unchanged', 0)}, rejected {result.get('rejected', 0)}."
        ),
    }
    if run_url:
        fields["Referensi Workflow"] = run_url
    path = f"/{base_id}/{SYNC_LOG_TABLE_ID}"
    _api_request(token, "POST", path, payload={"records": [{"fields": fields}]})
    return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync PADUKA BPS observations with Airtable.")
    parser.add_argument("--sync-report", help="Path to the private monitoring JSON report to sync to Airtable.")
    parser.add_argument("--export-valid", help="Write only Airtable records with Status Validasi=Valid to a JSON file.")
    args = parser.parse_args(argv)
    if bool(args.sync_report) == bool(args.export_valid):
        parser.error("choose exactly one of --sync-report or --export-valid")

    token = os.environ.get("AIRTABLE_API_TOKEN", "").strip()
    base_id = os.environ.get("AIRTABLE_BASE_ID", DEFAULT_BASE_ID)
    if not token:
        if args.export_valid:
            Path(args.export_valid).parent.mkdir(parents=True, exist_ok=True)
            Path(args.export_valid).write_text('{"observations": []}\n', encoding="utf-8")
        print(json.dumps({"status": "skipped", "reason": "AIRTABLE_API_TOKEN is not configured"}))
        return 0

    try:
        if args.sync_report:
            report_path = Path(args.sync_report)
            report = json.loads(report_path.read_text(encoding="utf-8"))
            result = sync_bps_observations(report, token, base_id=base_id)
            try:
                _write_sync_log(token, result, base_id=base_id)
                result["log_written"] = True
            except (RuntimeError, ValueError):
                result["log_written"] = False
            print(json.dumps(result, ensure_ascii=False))
        else:
            result = export_validated_observations(token, args.export_valid, base_id=base_id)
            print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, json.JSONDecodeError, RuntimeError, ValueError) as exc:
        print(f"Airtable BPS operation failed: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
