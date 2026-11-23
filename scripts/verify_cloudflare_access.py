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


def api_list(url: str, token: str) -> list[dict]:
    """Read a paginated Cloudflare list endpoint; reject malformed responses."""
    items: list[dict] = []
    page = 1
    while page <= 100:
        separator = "&" if "?" in url else "?"
        payload = api_get(f"{url}{separator}per_page=100&page={page}", token)
        result = payload.get("result")
        if not isinstance(result, list) or any(not isinstance(item, dict) for item in result):
            fail("Cloudflare API returned a malformed list response.")
        items.extend(result)
        info = payload.get("result_info") or {}
        total_pages = info.get("total_pages", page) if isinstance(info, dict) else page
        if not isinstance(total_pages, int) or total_pages < page:
            fail("Cloudflare API returned invalid pagination metadata.")
        if page >= total_pages:
            return items
        page += 1
    fail("Cloudflare API pagination exceeded the safety limit.")
    return []


def main() -> None:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "").strip()
    app_id = os.environ.get("CLOUDFLARE_ACCESS_APP_ID", "").strip()
    access_url = os.environ.get("PADUKA_ACCESS_URL", "").strip()
    owner_email = os.environ.get("PADUKA_OWNER_EMAIL", "").strip().lower()
    if not all((token, account_id, app_id, access_url, owner_email)):
        fail("Required verification inputs are missing.")
    parsed = urllib.parse.urlparse(access_url)
    try:
        access_port = parsed.port
    except ValueError:
        fail("PADUKA_ACCESS_URL contains an invalid port.")
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or access_port is not None or parsed.query or parsed.fragment:
        fail("PADUKA_ACCESS_URL must be a clean HTTPS URL without credentials, port, query, or fragment.")

    target_host = parsed.hostname.lower()
    account_path = (
        "https://api.cloudflare.com/client/v4/accounts/"
        + urllib.parse.quote(account_id, safe="")
        + "/access/apps"
    )
    apps = api_list(account_path, token)
    app = next((item for item in apps if str(item.get("id", "")) == app_id), None)
    if not app:
        fail("Configured Access application ID was not found.")

    app_domain = str(app.get("domain", "")).strip()
    domain_url = urllib.parse.urlparse("https://" + app_domain.lstrip("/"))
    try:
        app_port = domain_url.port
    except ValueError:
        fail("Cloudflare Access application domain contains an invalid port.")
    if domain_url.hostname is None or domain_url.username or domain_url.password or app_port is not None or domain_url.query or domain_url.fragment:
        fail("Cloudflare Access application domain is malformed or contains a port.")
    if domain_url.hostname.lower() != target_host:
        fail("Access application hostname does not match the deployment target URL.")
    protected_path = domain_url.path.rstrip("/")
    target_path = parsed.path.rstrip("/")
    if protected_path and not (target_path == protected_path or target_path.startswith(protected_path + "/")):
        fail("Deployment URL path is outside the Access application protected path.")
    if app.get("type") != "self_hosted":
        fail("Target Access application is not a self-hosted application.")

    # Policies are fetched from their documented per-application endpoint rather
    # than assuming the applications-list response embeds a complete policy set.
    policy_path = account_path + "/" + urllib.parse.quote(app_id, safe="") + "/policies"
    policies = api_list(policy_path, token)
    if not policies:
        fail("Access application has no policies to verify.")

    allowed_owner_policies = 0
    for policy in policies:
        decision = str(policy.get("decision", "")).lower()
        if decision != "allow":
            fail("A non-Allow policy exists on the target application; manual review required.")
        includes = policy.get("include") or []
        if not isinstance(includes, list) or len(includes) != 1:
            fail("An allow policy is not restricted to a single owner identity.")
        rule = includes[0]
        if not isinstance(rule, dict) or set(rule.keys()) != {"email"}:
            fail("An allow policy contains a broad or non-email identity rule.")
        email_rule = rule.get("email")
        if not isinstance(email_rule, dict) or set(email_rule.keys()) != {"email"} or str(email_rule.get("email", "")).strip().lower() != owner_email:
            fail("An allow policy does not match the configured owner email.")
        if policy.get("exclude"):
            fail("Owner-only allow policy has exclusions; manual review required.")
        allowed_owner_policies += 1
    if allowed_owner_policies != 1:
        fail("Expected exactly one allow policy for the owner and no other allow policies.")
    print("Cloudflare Access verification passed: matching hostname and exactly one owner-only allow policy.")


if __name__ == "__main__":
    main()
