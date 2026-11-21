"""Transparent source and evidence assessment from supplied metadata only.

This module deliberately does not assign a reputation score or declare sources
reliable. Unknown profile fields remain unknown until independently reviewed.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any
from urllib.parse import urlparse


def _valid_http_url(value: Any) -> bool:
    try:
        parsed = urlparse(str(value or "").strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.hostname)
    except ValueError:
        return False


def _valid_timestamp(value: Any) -> bool:
    if not value:
        return False
    raw = str(value).strip()
    try:
        datetime.fromisoformat(raw.replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def assess_source_intelligence(signal: dict[str, Any]) -> dict[str, Any]:
    """Describe observable provenance fields without claiming factual reliability."""
    url = str(signal.get("url") or "").strip()
    parsed = urlparse(url) if url else None
    domain = (parsed.hostname or "").lower().rstrip(".") if parsed else ""
    secure_transport = bool(parsed and parsed.scheme.lower() == "https" and domain)
    profile = signal.get("source_profile")
    profile = profile if isinstance(profile, dict) else {}

    checks = {
        "source_name_present": bool(str(signal.get("source") or "").strip()),
        "article_url_valid": _valid_http_url(url),
        "https_transport": secure_transport,
        "publication_time_present": _valid_timestamp(signal.get("published_at")),
        "author_attribution_present": bool(str(signal.get("author") or "").strip()),
        "summary_present": bool(str(signal.get("summary") or "").strip()),
        "citations_declared": isinstance(signal.get("citations"), list) and bool(signal.get("citations")),
        "primary_source_declared": signal.get("is_primary_source") is True,
        "corrections_policy_url_valid": _valid_http_url(profile.get("corrections_policy_url")),
        "ownership_information_url_valid": _valid_http_url(profile.get("ownership_url")),
        "editorial_policy_url_valid": _valid_http_url(profile.get("editorial_policy_url")),
    }
    unknown_profile = [
        field for field in ("corrections_policy_url", "ownership_url", "editorial_policy_url")
        if not profile.get(field)
    ]
    positive = sum(1 for value in checks.values() if value)
    if not checks["source_name_present"] or not checks["article_url_valid"]:
        status = "insufficient_source_metadata"
    elif positive >= 8:
        status = "metadata_rich_human_review_required"
    elif positive >= 5:
        status = "partially_documented_human_review_required"
    else:
        status = "limited_metadata_human_review_required"

    return {
        "status": status,
        "source_domain": domain or None,
        "checks": checks,
        "metadata_checks_passed": positive,
        "metadata_checks_total": len(checks),
        "unknown_profile_fields": unknown_profile,
        "reputation_score": None,
        "reliability_verdict": "not_assessed",
        "independence_verdict": "not_assessed",
        "notice": (
            "This is a metadata and provenance checklist, not a source reputation score or "
            "fact-check. HTTPS, author fields, policies, citations, and source counts do not "
            "prove accuracy, editorial independence, or authenticity. Human review is required."
        ),
    }
