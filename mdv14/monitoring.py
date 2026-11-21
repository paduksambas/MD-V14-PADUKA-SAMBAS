"""Operational status summary for scheduled RSS/Atom monitoring cycles."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import Any


def _parse_timestamp(value: Any) -> datetime | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    try:
        parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(raw)
        except (TypeError, ValueError, OverflowError):
            return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def build_monitoring_status(
    collection: dict[str, Any],
    signals: list[dict[str, Any]],
    *,
    generated_at: str | None = None,
    freshness_hours: int = 24,
) -> dict[str, Any]:
    """Summarize one collection cycle; freshness is based on publisher timestamps."""
    if freshness_hours < 1:
        raise ValueError("freshness_hours must be at least 1")
    now = _parse_timestamp(generated_at) if generated_at else datetime.now(timezone.utc)
    if now is None:
        raise ValueError("generated_at must be a valid timestamp")
    results = collection.get("feed_results", []) if isinstance(collection, dict) else []
    results = [item for item in results if isinstance(item, dict)] if isinstance(results, list) else []
    succeeded = sum(1 for item in results if item.get("ok") is True)
    failed = sum(1 for item in results if item.get("ok") is False)
    dated = [_parse_timestamp(item.get("published_at")) for item in signals]
    known = [stamp for stamp in dated if stamp is not None]
    cutoff = now - timedelta(hours=freshness_hours)
    recent = sum(1 for stamp in known if cutoff <= stamp <= now)
    future = sum(1 for stamp in known if stamp > now)
    if not results:
        state = "not_configured"
    elif failed == 0 and succeeded:
        state = "healthy"
    elif succeeded:
        state = "degraded"
    else:
        state = "unavailable"
    return {
        "engine": "MD V14 Scheduled Global Monitoring",
        "build": "2.6",
        "generated_at": now.isoformat().replace("+00:00", "Z"),
        "cycle_status": state,
        "freshness_window_hours": freshness_hours,
        "feeds_attempted": len(results),
        "feeds_succeeded": succeeded,
        "feeds_failed": failed,
        "signals_collected": len(signals),
        "signals_with_parseable_published_at": len(known),
        "signals_published_within_window": recent,
        "signals_with_future_published_at": future,
        "signals_with_unknown_published_at": len(signals) - len(known),
        "feed_health": [
            {
                "feed_url": str(item.get("feed_url") or ""),
                "ok": bool(item.get("ok")),
                "item_count": int(item.get("item_count", 0) or 0),
                "error": str(item.get("error") or ""),
            }
            for item in results
        ],
        "notice": "This is one scheduled collection cycle, not continuous surveillance. Publisher timestamps may be missing or inaccurate; feed health does not establish content truth or global coverage.",
    }
