"""Load a reviewed Airtable snapshot of regional BPS observations.

The public static dashboard consumes a repository snapshot exported from the
connected Airtable base. Only rows explicitly marked "Valid" enter statistical
rankings. Pending rows remain visible for human review and are never treated as
validated observations.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

MAX_SNAPSHOT_BYTES = 2_000_000
VALID_STATUSES = {"valid"}
PENDING_STATUSES = {"belum ditinjau", "menunggu validasi", "pending", "pending validation"}
REJECTED_STATUSES = {"ditolak", "rejected", "invalid"}


def _normalize_row(item: Any, index: int) -> tuple[dict[str, Any] | None, str | None]:
    if not isinstance(item, dict):
        return None, f"row {index}: not an object"

    region_code = str(item.get("region_code") or "").strip()
    region_name = str(item.get("region_name") or "").strip()
    level = str(item.get("level") or "").strip().lower()
    indicator_code = str(item.get("indicator_code") or "").strip()
    indicator_name = str(item.get("indicator_name") or indicator_code).strip()
    period = str(item.get("period") or "").strip()
    validation_status = str(item.get("validation_status") or "").strip()

    try:
        value = float(item.get("value"))
    except (TypeError, ValueError):
        return None, f"row {index}: missing or invalid numeric value"

    if not region_code or not region_name or level not in {"province", "regency_city"}:
        return None, f"row {index}: invalid region code, name or level"
    if not indicator_code or not period or not validation_status:
        return None, f"row {index}: missing indicator, period or validation status"
    if not math.isfinite(value):
        return None, f"row {index}: non-finite value"

    return {
        "region_code": region_code,
        "region_name": region_name,
        "level": level,
        "province_code": str(item.get("province_code") or ""),
        "indicator_code": indicator_code,
        "indicator_name": indicator_name,
        "period": period,
        "value": value,
        "unit": str(item.get("unit") or ""),
        "source": str(item.get("source") or "BPS via Airtable"),
        "source_url": str(item.get("source_url") or ""),
        "validation_status": validation_status,
        "date_collected": str(item.get("date_collected") or ""),
    }, None


def load_airtable_regional_snapshot(path: str | Path) -> dict[str, Any]:
    """Load a bounded JSON snapshot exported from Airtable's Observasi Regional table."""
    file_path = Path(path)
    content = file_path.read_bytes()
    if len(content) > MAX_SNAPSHOT_BYTES:
        raise ValueError("Airtable regional snapshot exceeds 2 MB")
    payload = json.loads(content.decode("utf-8-sig"))
    if not isinstance(payload, dict) or not isinstance(payload.get("observations"), list):
        raise ValueError("Airtable snapshot must be an object with an observations array")

    valid_rows: list[dict[str, Any]] = []
    pending_rows: list[dict[str, Any]] = []
    rejected: list[str] = []
    for index, item in enumerate(payload["observations"], start=1):
        row, error = _normalize_row(item, index)
        if error:
            rejected.append(error)
            continue
        assert row is not None
        status = row["validation_status"].casefold()
        if status in VALID_STATUSES:
            valid_rows.append(row)
        elif status in PENDING_STATUSES:
            pending_rows.append(row)
        elif status in REJECTED_STATUSES:
            rejected.append(f"row {index}: rejected by Airtable validation status")
        else:
            rejected.append(f"row {index}: unrecognized validation status")

    total = len(payload["observations"])
    if valid_rows and (pending_rows or rejected):
        status = "partial"
    elif valid_rows:
        status = "available"
    elif pending_rows:
        status = "pending_validation"
    else:
        status = "no_data"

    return {
        "provider": "Airtable",
        "base_name": str(payload.get("base_name") or "Airtable"),
        "table_name": str(payload.get("table_name") or "Observasi Regional"),
        "snapshot_date": str(payload.get("snapshot_date") or ""),
        "status": status,
        "records_read": total,
        "valid_count": len(valid_rows),
        "pending_validation_count": len(pending_rows),
        "rejected_count": len(rejected),
        "observations": valid_rows,
        "pending_observations": pending_rows,
        "errors": rejected[:20],
    }


def apply_airtable_validation_status(
    regional_result: dict[str, Any], airtable_result: dict[str, Any]
) -> dict[str, Any]:
    """Avoid reporting no regional data when Airtable rows await human validation."""
    try:
        observation_count = int(regional_result.get("observation_count", 0))
        pending_count = int(airtable_result.get("pending_validation_count", 0))
    except (TypeError, ValueError):
        return regional_result
    if observation_count == 0 and pending_count > 0:
        regional_result["status"] = "pending_validation"
    return regional_result
