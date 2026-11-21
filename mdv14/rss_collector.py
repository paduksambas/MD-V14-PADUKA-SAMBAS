"""Fetch and parse configured RSS/Atom feeds with bounded network access."""
from __future__ import annotations

import ipaddress
import socket
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any
from urllib.parse import urlparse


MAX_FEED_BYTES = 2_000_000
DEFAULT_TIMEOUT = 12
USER_AGENT = "MDV14-ResearchBot/1.0 (+RSS feed reader)"


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def _validate_feed_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("feed URL must use HTTPS")
    if parsed.username or parsed.password:
        raise ValueError("credentials in feed URLs are not allowed")
    host = parsed.hostname.lower()
    if host in {"localhost"} or host.endswith(".localhost") or host.endswith(".local"):
        raise ValueError("local network feed hosts are not allowed")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address and not address.is_global:
        raise ValueError("non-public IP feed hosts are not allowed")
    if not address:
        try:
            resolved = socket.getaddrinfo(host, parsed.port or 443, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise ValueError(f"feed host could not be resolved: {exc}") from exc
        resolved_ips = {item[4][0].split("%", 1)[0] for item in resolved}
        if not resolved_ips or any(not ipaddress.ip_address(ip).is_global for ip in resolved_ips):
            raise ValueError("feed host must resolve only to public IP addresses")


def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def _child_text(element: ET.Element, names: tuple[str, ...]) -> str:
    for child in element.iter():
        tag = child.tag.rsplit("}", 1)[-1].lower()
        if tag in names and _text(child):
            return _text(child)
    return ""


def _entry_url(entry: ET.Element) -> str:
    for child in list(entry):
        tag = child.tag.rsplit("}", 1)[-1].lower()
        if tag == "link":
            href = child.attrib.get("href", "").strip()
            rel = child.attrib.get("rel", "alternate")
            if href and rel == "alternate":
                return href
            if _text(child):
                return _text(child)
    return ""


def parse_feed(xml_bytes: bytes, feed_url: str, source_name: str = "") -> list[dict[str, Any]]:
    """Parse common RSS 2.0 and Atom entries; skip entries without title/link."""
    root = ET.fromstring(xml_bytes)
    entries = [
        element for element in root.iter()
        if element.tag.rsplit("}", 1)[-1].lower() in {"item", "entry"}
    ]
    results = []
    for entry in entries:
        title = _child_text(entry, ("title",))
        link = _entry_url(entry)
        if not title or not link:
            continue
        summary = _child_text(entry, ("description", "summary", "content", "encoded"))
        published = _child_text(entry, ("pubdate", "published", "updated", "date"))
        results.append({
            "title": title,
            "source": source_name.strip() or urlparse(feed_url).hostname or "RSS feed",
            "url": link,
            "summary": summary,
            "published_at": published,
            "feed_url": feed_url,
            "category": "Unclassified",
            "score": 0,
            "collection_method": "rss_atom",
        })
    return results


def fetch_feed(
    feed_url: str,
    source_name: str = "",
    timeout: int = DEFAULT_TIMEOUT,
    max_bytes: int = MAX_FEED_BYTES,
) -> dict[str, Any]:
    """Fetch one HTTPS feed. Redirects are not followed; response size is bounded."""
    if timeout < 1 or max_bytes < 1:
        raise ValueError("timeout and max_bytes must be positive")
    try:
        _validate_feed_url(feed_url)
        request = urllib.request.Request(
            feed_url,
            headers={"User-Agent": USER_AGENT, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml"},
        )
        opener = urllib.request.build_opener(_NoRedirect)
        with opener.open(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ValueError("feed response exceeds configured size limit")
        entries = parse_feed(body, feed_url, source_name)
        return {"feed_url": feed_url, "ok": True, "items": entries, "item_count": len(entries)}
    except (urllib.error.URLError, TimeoutError, OSError, ET.ParseError, ValueError) as exc:
        return {"feed_url": feed_url, "ok": False, "items": [], "item_count": 0, "error": str(exc)}


def collect_feeds(feeds: list[dict[str, str]]) -> dict[str, Any]:
    """Collect configured feeds independently so one failure does not stop the batch."""
    results = []
    for feed in feeds:
        url = str(feed.get("url", "")).strip()
        name = str(feed.get("name", "")).strip()
        if not url:
            results.append({"feed_url": "", "ok": False, "items": [], "item_count": 0, "error": "missing feed URL"})
        else:
            try:
                results.append(fetch_feed(url, name))
            except (ValueError, OSError) as exc:
                results.append({"feed_url": url, "ok": False, "items": [], "item_count": 0, "error": str(exc)})
    items = [item for result in results for item in result["items"]]
    return {
        "collector": "MD V14 RSS/Atom",
        "feeds_attempted": len(results),
        "feeds_succeeded": sum(1 for result in results if result["ok"]),
        "feeds_failed": sum(1 for result in results if not result["ok"]),
        "items_collected": len(items),
        "feed_results": results,
        "signals": items,
    }
