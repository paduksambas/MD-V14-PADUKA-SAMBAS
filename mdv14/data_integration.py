"""Global intelligence data normalization and source-catalog validation."""
from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from typing import Any, Iterable
from urllib.parse import urlparse

DATA_SCHEMA_VERSION = "1.0"

def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""

def _string_list(value: Any) -> list[str]:
    values = value.split(",") if isinstance(value, str) else value if isinstance(value, (list, tuple, set)) else []
    result, seen = [], set()
    for item in values:
        label = _text(item)
        if label and label.casefold() not in seen:
            result.append(label)
            seen.add(label.casefold())
    return result

def _timestamp(value: Any) -> str | None:
    raw = _text(value)
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except ValueError:
        return raw

def validate_source_catalog(sources: Iterable[dict[str, Any]]) -> dict[str, Any]:
    source_list = list(sources)
    accepted, errors, seen = [], [], set()
    for index, source in enumerate(source_list):
        if not isinstance(source, dict):
            errors.append({"index": index, "error": "source entry must be an object"})
            continue
        source_id, name, url = _text(source.get("id")), _text(source.get("name")), _text(source.get("url"))
        if not source_id or not name or not url:
            errors.append({"index": index, "source_id": source_id or None, "error": "id, name, and url are required"})
            continue
        if source_id.casefold() in seen:
            errors.append({"index": index, "source_id": source_id, "error": "duplicate source id"})
            continue
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            errors.append({"index": index, "source_id": source_id, "error": "source URL must be HTTPS with hostname and no credentials"})
            continue
        seen.add(source_id.casefold())
        if source.get("enabled", True) is False:
            continue
        accepted.append({
            **source, "id": source_id, "name": name, "url": url,
            "country": _text(source.get("country")) or None,
            "region": _text(source.get("region")) or None,
            "language": _text(source.get("language")) or None,
            "publisher": _text(source.get("publisher")) or name,
            "source_type": _text(source.get("source_type")) or "news",
            "topics": _string_list(source.get("topics")),
        })
    return {"sources": accepted, "sources_configured": len(source_list),
            "sources_enabled": len(accepted), "configuration_errors": errors}

def normalize_global_signal(signal: dict[str, Any], source_metadata: dict[str, Any] | None = None,
                            collected_at: str | None = None) -> dict[str, Any]:
    metadata = source_metadata if isinstance(source_metadata, dict) else {}
    output = dict(signal)
    output.update({
        "data_schema_version": DATA_SCHEMA_VERSION,
        "source_id": _text(signal.get("source_id") or metadata.get("id")) or None,
        "publisher": _text(signal.get("publisher") or metadata.get("publisher")) or None,
        "country": _text(signal.get("country") or metadata.get("country")) or None,
        "region": _text(signal.get("region") or metadata.get("region")) or None,
        "language": _text(signal.get("language") or metadata.get("language")) or None,
        "source_type": _text(signal.get("source_type") or metadata.get("source_type")) or None,
        "topics": _string_list(signal.get("topics") or metadata.get("topics")),
        "published_at": _timestamp(signal.get("published_at")),
        "collected_at": _timestamp(signal.get("collected_at") or collected_at) or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "collection_method": _text(signal.get("collection_method")) or "manual",
        "feed_url": _text(signal.get("feed_url")) or None,
    })
    return output

def build_data_coverage(signals: Iterable[dict[str, Any]]) -> dict[str, Any]:
    items = list(signals)
    dimensions = {}
    for dimension in ("country", "region", "language", "source_type", "publisher"):
        counts = Counter(_text(item.get(dimension)) or "unknown" for item in items)
        dimensions[dimension] = {
            "known_records": sum(n for key, n in counts.items() if key != "unknown"),
            "unknown_records": counts.get("unknown", 0), "values": dict(sorted(counts.items())),
        }
    return {"schema_version": DATA_SCHEMA_VERSION, "records_total": len(items),
            "dimensions": dimensions,
            "notice": "Coverage reflects supplied metadata only; unknown values are not inferred."}
