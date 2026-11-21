#!/usr/bin/env python3
"""Fail closed unless the target Cloudflare Access app is owner-only."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request


def fail(message: str) -> None:
    print(f"Access verification failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def api_get(url: str, token: str) -> dict:
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        fail(f"Cloudflare API request could not be verified ({type(exc).__name__}).")
    if not isinstance(payload, dict) or payload.get("success") is not True:
        fail("Cloudflare API did not return a successful response.")
    return payload


def main() -> None:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    app_id = os.environ.get("CLOUDFLARE_ACCESS_APP_ID", "").strip()
    access_url = os.environ.get("PADUKA_ACCESS_URL", "").strip()
    owner_email = os.environ.get("PADUKA_OWNER_EMAIL", "").strip().lower()
    if not all((token, account_id, app_id, access_url, owner_email)):
        fail("Required verification inputs are missing.")
    parsed = urllib.parse.urlparse(access_url)
    if parsed.scheme != "https" or not parsed.hostname:
        fail("PADUKA_ACCESS_URL must be a valid HTTPS URL.")
    target_host = parsed.hostname.lower()
    api_base = f"https://api.cloudflare.com/client/v4/accounts/{urllib.parse.quote(account_id, safe='')}/access/apps"
    apps = api_get(api_base + "?per_page=1000", token).get("result", [])
    app = next((item for item in apps if str(item.get("id", "")) == app_id), None)
    if not app:
        fail("Configured Access application ID was not found.")
    app_domain = str(app.get("domain", "")).strip()
    domain_url = urllib.parse.urlparse("https://" + app_domain.lstrip("/"))
    if domain_url.hostname is None or domain_url.hostname.lower() != target_host:
        fail("Access application hostname does not match the deployment target URL.")
    if app.get("type") != "self_hosted":
        fail("Target Access application is not a self-hosted application.")
    policies = app.get("policies")
    if not isinstance(policies, list) or not policies:
        fail("Access application has no embedded policies to verify.")
    allowed_owner_policies = 0
    for policy in policies:
        decision = str(policy.get("decision", "")).lower()
        if decision in ("bypass", "non_identity"):
            fail("A bypass/non-identity policy exists on the target application.")
        if decision != "allow":
            continue
        includes = policy.get("include") or []
        if not isinstance(includes, list) or len(includes) != 1:
            fail("An allow policy is not restricted to a single owner identity.")
        rule = includes[0]
        if not isinstance(rule, dict) or set(rule.keys()) != {"email"}:
            fail("An allow policy contains a broad or non-email identity rule.")
        email_rule = rule.get("email")
        if not isinstance(email_rule, dict) or str(email_rule.get("email", "")).strip().lower() != owner_email:
            fail("An allow policy does not match the configured owner email.")
        if policy.get("exclude"):
            fail("Owner-only allow policy has exclusions; manual review required.")
        allowed_owner_policies += 1
    if allowed_owner_policies != 1:
        fail("Expected exactly one allow policy for the owner and no other allow policies.")
    print("Cloudflare Access verification passed: matching hostname and exactly one owner-only allow policy.")


if ____ == "__main__":
    main()
