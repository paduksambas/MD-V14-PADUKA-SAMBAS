"""Fetch and parse configured RSS/Atom feeds with bounded network access."""
from __future__ import annotations

import ipaddress
import re
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


def _valid_article_url(value: str) -> bool:
    """Accept navigable web links only; reject script, file, credential and hostless URLs."""
    try:
        parsed = urlparse(str(value or "").strip())
        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
        )
    except ValueError:
        return False


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


TOPIC_EDITORIAL_IMAGES = {
    "geopolitics": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?w=1200&q=80",
    "politics": "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=1200&q=80",
    "economy": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=1200&q=80",
    "business": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=1200&q=80",
    "transport": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=1200&q=80",
    "law": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1200&q=80",
    "sports": "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=1200&q=80",
    "default": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=1200&q=80",
}


def get_fallback_editorial_image(title: str, topics: list[str]) -> str:
    """Mengembalikan foto jurnalistik kurasi sesuai topik jika RSS/OpenGraph tidak menyediakan foto."""
    text = (title + " " + " ".join(topics)).lower()
    if any(k in text for k in ["china", "as", "amerika", "rusia", "perang", "dunia", "global", "pbb", "geopolitics"]):
        return TOPIC_EDITORIAL_IMAGES["geopolitics"]
    if any(k in text for k in ["ekonomi", "saham", "rupiah", "inflasi", "pasar", "ihsg", "komoditas", "bisnis"]):
        return TOPIC_EDITORIAL_IMAGES["economy"]
    if any(k in text for k in ["kereta", "lrt", "mrt", "jalan", "tol", "pesawat", "transportasi"]):
        return TOPIC_EDITORIAL_IMAGES["transport"]
    if any(k in text for k in ["sidang", "polisi", "jaksa", "hakim", "hukum", "etik", "tersangka", "korupsi"]):
        return TOPIC_EDITORIAL_IMAGES["law"]
    if any(k in text for k in ["bola", "timnas", "liga", "stadion", "gol", "olahraga"]):
        return TOPIC_EDITORIAL_IMAGES["sports"]
    if any(k in text for k in ["presiden", "menteri", "dpr", "pemilu", "pilkada", "politik"]):
        return TOPIC_EDITORIAL_IMAGES["politics"]
    return TOPIC_EDITORIAL_IMAGES["default"]


def extract_opengraph_image(article_url: str, timeout: int = 5) -> str:
    """Mengekstrak tag og:image atau twitter:image langsung dari HTML artikel asli."""
    if not _valid_article_url(article_url):
        return ""
    try:
        req = urllib.request.Request(
            article_url,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html,application/xhtml+xml"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            chunk = resp.read(32768).decode("utf-8", errors="ignore")
            m = re.search(r'<meta[^>]+property=["\']og:image["\'][^>]+content=["\']([^"\']+)["\']', chunk, re.IGNORECASE)
            if not m:
                m = re.search(r'<meta[^>]+content=["\']([^"\']+)["\'][^>]+property=["\']og:image["\']', chunk, re.IGNORECASE)
            if not m:
                m = re.search(r'<meta[^>]+name=["\']twitter:image["\'][^>]+content=["\']([^"\']+)["\']', chunk, re.IGNORECASE)
            if m:
                candidate = m.group(1).strip()
                if _valid_article_url(candidate):
                    return candidate
    except Exception:
        pass
    return ""


def parse_feed(xml_bytes: bytes, feed_url: str, source_name: str = "") -> list[dict[str, Any]]:
    """Parse common RSS 2.0 and Atom entries; skip entries without safe title/link."""
    root = ET.fromstring(xml_bytes)
    entries = [
        element for element in root.iter()
        if element.tag.rsplit("}", 1)[-1].lower() in {"item", "entry"}
    ]
    results = []
    for entry in entries:
        title = _child_text(entry, ("title",))
        link = _entry_url(entry)
        if not title or not _valid_article_url(link):
            continue
        summary = _child_text(entry, ("description", "summary", "content", "encoded"))
        published = _child_text(entry, ("pubdate", "published", "updated", "date"))
        author = _child_text(entry, ("author", "creator", "name"))
        topics = []
        for child in list(entry):
            if child.tag.rsplit("}", 1)[-1].lower() == "category":
                term = child.attrib.get("term", "").strip() or _text(child)
                if term and term not in topics:
                    topics.append(term)

        # Ekstraksi foto pers/gambar (media:content, media:thumbnail, enclosure, img src)
        image_url = ""
        for child in list(entry):
            ctag = child.tag.rsplit("}", 1)[-1].lower()
            if ctag in {"content", "thumbnail", "enclosure"}:
                u = child.attrib.get("url", "").strip()
                if u and _valid_article_url(u):
                    image_url = u
                    break
        if not image_url and summary:
            m = re.search(r'src=["\']([^"\']+\.(?:jpg|jpeg|png|webp)[^"\']*)["\']', summary, re.IGNORECASE)
            if m and _valid_article_url(m.group(1)):
                image_url = m.group(1)

        # Fallback bertingkat jika foto belum ada di tag RSS standar
        image_source = "rss_feed" if image_url else "none"
        if not image_url:
            image_url = get_fallback_editorial_image(title, topics)
            image_source = "editorial_curated"

        results.append({
            "title": title,
            "source": source_name.strip() or urlparse(feed_url).hostname or "RSS feed",
            "url": link,
            "image_url": image_url,
            "image_source": image_source,
            "has_image": bool(image_url),
            "summary": summary,
            "published_at": published,
            "author": author,
            "topics": topics,
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
        handlers: list[Any] = [_NoRedirect]
        try:
            import ssl
            ctx = ssl.create_default_context()
            try:
                import certifi
                ctx.load_verify_locations(certifi.where())
            except Exception:
                pass
            handlers.append(urllib.request.HTTPSHandler(context=ctx))
        except Exception:
            pass
        opener = urllib.request.build_opener(*handlers)
        with opener.open(request, timeout=timeout) as response:
            body = response.read(max_bytes + 1)
            if len(body) > max_bytes:
                raise ValueError("feed response exceeds configured size limit")
        entries = parse_feed(body, feed_url, source_name)
        # Live enrichment: Coba cari og:image asli dari portal berita jika gambar masih fallback kurasi
        for it in entries:
            if it.get("image_source") == "editorial_curated":
                og_img = extract_opengraph_image(it["url"])
                if og_img:
                    it["image_url"] = og_img
                    it["image_source"] = "opengraph_media"

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
