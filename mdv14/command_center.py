"""Unified command-center summary built from MD V14 report sections."""
from __future__ import annotations

from typing import Any


def build_command_center(report: dict[str, Any], *, limit: int = 10) -> dict[str, Any]:
    """Create an operational and strategic overview without adding new inferences."""
    if limit < 1:
        raise ValueError("limit must be at least 1")
    signals = report.get("signals", [])
    signals = [x for x in signals if isinstance(x, dict)] if isinstance(signals, list) else []
    monitoring = report.get("monitoring", {})
    monitoring = monitoring if isinstance(monitoring, dict) else {}
    decision = report.get("strategic_decision", {})
    decision = decision if isinstance(decision, dict) else {}
    queue = decision.get("review_queue", [])
    queue = [x for x in queue if isinstance(x, dict)] if isinstance(queue, list) else []
    warnings = report.get("warning_summary", {})
    warnings = warnings if isinstance(warnings, dict) else {}
    global_data = report.get("global_intelligence", {})
    global_data = global_data if isinstance(global_data, dict) else {}
    analyst = report.get("analyst_report", {})
    analyst = analyst if isinstance(analyst, dict) else {}
    collection = report.get("collection", {})
    collection = collection if isinstance(collection, dict) else {}

    feeds_attempted = int(monitoring.get("feeds_attempted", collection.get("feeds_attempted", 0)) or 0)
    feeds_succeeded = int(monitoring.get("feeds_succeeded", collection.get("feeds_succeeded", 0)) or 0)
    feeds_failed = int(monitoring.get("feeds_failed", collection.get("feeds_failed", 0)) or 0)
    cycle_status = str(monitoring.get("cycle_status") or ("not_configured" if not feeds_attempted else "unknown"))
    if cycle_status == "healthy":
        operational_state = "operational"
    elif cycle_status == "degraded":
        operational_state = "degraded"
    elif cycle_status == "unavailable":
        operational_state = "unavailable"
    else:
        operational_state = "not_assessed"

    priority_counts = decision.get("priority_band_counts", {})
    priority_counts = priority_counts if isinstance(priority_counts, dict) else {}
    priority_high = int(priority_counts.get("high", 0) or 0)
    priority_medium = int(priority_counts.get("medium", 0) or 0)
    critical = int(warnings.get("critical", 0) or 0)
    elevated = int(warnings.get("elevated", 0) or 0)
    evidence_gaps = int(report.get("evidence_review_required", 0) or 0)
    freshness_recent = int(monitoring.get("signals_published_within_window", 0) or 0)
    freshness_unknown = int(monitoring.get("signals_with_unknown_published_at", 0) or 0)

    if not signals:
        posture = "insufficient_data"
        posture_note = "Belum ada rekaman untuk membentuk gambaran strategis."
    elif critical or priority_high:
        posture = "priority_review_required"
        posture_note = "Terdapat indikator berprioritas tinggi yang perlu ditinjau manusia; ini bukan penetapan tingkat ancaman."
    elif elevated or priority_medium or evidence_gaps:
        posture = "watch_and_review"
        posture_note = "Ada indikator atau kesenjangan metadata yang memerlukan pemeriksaan lanjutan."
    else:
        posture = "routine_review"
        posture_note = "Tidak ada prioritas tinggi yang teridentifikasi oleh indikator saat ini; cakupan sumber tetap terbatas."

    top_queue = []
    for item in queue[:limit]:
        top_queue.append({
            "signal_id": str(item.get("signal_id") or ""),
            "title": str(item.get("title") or ""),
            "priority_band": str(item.get("priority_band") or "routine"),
            "priority_score": item.get("priority_score"),
            "warning_level": str(item.get("warning_level") or "not_assessed"),
            "source": str(item.get("source") or "unknown"),
            "url": str(item.get("url") or ""),
            "country": str(item.get("country") or "unknown"),
        })

    countries = global_data.get("country_analysis", [])
    topics = global_data.get("topic_analysis", [])
    countries = countries if isinstance(countries, list) else []
    topics = topics if isinstance(topics, list) else []
    countries = sorted(
        (x for x in countries if isinstance(x, dict)),
        key=lambda x: (-int(x.get("signal_count", 0) or 0), str(x.get("name", "")).casefold()),
    )
    topics = sorted(
        (x for x in topics if isinstance(x, dict)),
        key=lambda x: (-int(x.get("signal_count", 0) or 0), str(x.get("name", "")).casefold()),
    )

    return {
        "build": "3.0",
        "name": "MD V14 Global Strategic Intelligence Command Center",
        "generated_at": monitoring.get("generated_at") or report.get("generated_at"),
        "operational_state": operational_state,
        "collection_cycle": {
            "status": cycle_status,
            "feeds_attempted": feeds_attempted,
            "feeds_succeeded": feeds_succeeded,
            "feeds_failed": feeds_failed,
            "signals_collected": int(monitoring.get("signals_collected", collection.get("items_collected", len(signals))) or 0),
            "published_within_freshness_window": freshness_recent,
            "unknown_published_timestamp": freshness_unknown,
        },
        "strategic_posture": {
            "status": posture,
            "note": posture_note,
            "critical_warning_indicators": critical,
            "elevated_warning_indicators": elevated,
            "high_review_priority": priority_high,
            "medium_review_priority": priority_medium,
            "evidence_review_required": evidence_gaps,
        },
        "coverage": {
            "signals_analyzed": len(signals),
            "countries_represented": len(countries),
            "topics_represented": len(topics),
            "country_leaders": [{"name": x.get("name", "Unknown"), "signal_count": x.get("signal_count", 0)} for x in countries[:5]],
            "topic_leaders": [{"name": x.get("name", "Unknown"), "signal_count": x.get("signal_count", 0)} for x in topics[:5]],
        },
        "priority_review_queue": top_queue,
        "analyst_report": {
            "findings": len(analyst.get("key_findings", [])) if isinstance(analyst.get("key_findings", []), list) else 0,
            "uncertainties": len(analyst.get("uncertainties_and_gaps", [])) if isinstance(analyst.get("uncertainties_and_gaps", []), list) else 0,
            "human_actions": len(analyst.get("recommended_human_actions", [])) if isinstance(analyst.get("recommended_human_actions", []), list) else 0,
        },
        "decision_gates": [
            "Verify claims against original and, where possible, primary sources.",
            "Check source independence, publication time, geography, and missing metadata.",
            "Review alternative explanations and conflicting evidence.",
            "Require an authorized human decision before escalation, publication, or action.",
        ],
        "interpretation": "A consolidated view of supplied MD V14 assessments, not a live geopolitical risk rating, forecast, or autonomous decision.",
        "limitations": [
            "Collection status reflects configured feed requests only; scheduled collection is not continuous monitoring.",
            "Priority and warning indicators are heuristic triage cues, not threat severity or probability.",
            "Country and topic coverage reflects declared or recognized metadata, not global representativeness.",
            "No claim is independently verified by this command-center layer.",
        ],
    }
