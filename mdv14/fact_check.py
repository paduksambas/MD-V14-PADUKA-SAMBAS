"""Evidence hygiene checks. This module does not establish factual truth."""
from __future__ import annotations

from typing import Any
from urllib.parse import urlparse


def assess_evidence(signal: dict[str, Any]) -> dict[str, Any]:
    title = str(signal.get("title") or signal.get("topic") or "").strip()
    source = str(signal.get("source") or "").strip()
    url = str(signal.get("url") or "").strip()
    parsed = urlparse(url)
    valid_url = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    missing = []
    if not title:
        missing.append("title")
    if not source:
        missing.append("source")
    if not url:
        missing.append("url")
    elif not valid_url:
        missing.append("valid_http_url")
    complete = not missing
    return {
        "evidence_complete": complete,
        "source_url_valid": valid_url,
        "missing_fields": missing,
        "verification_status": "ready_for_human_verification" if complete else "insufficient_evidence",
        "truth_verified": False,
        "notice": "Metadata completeness is not fact verification; inspect the original source and corroborate material claims.",
    }
