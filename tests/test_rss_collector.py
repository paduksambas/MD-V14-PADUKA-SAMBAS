"""Tests for the RSS/Atom collector without external network access."""
import unittest

from mdv14.rss_collector import _validate_feed_url, parse_feed


class RSSCollectorTests(unittest.TestCase):
    def test_parse_rss(self):
        xml = b"""<rss version="2.0"><channel><item><title>Story A</title><link>https://news.example/a</link><description>Summary A</description><pubDate>Sat, 21 Nov 2026 08:00:00 GMT</pubDate></item></channel></rss>"""
        items = parse_feed(xml, "https://news.example/rss", "News Desk")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Story A")
        self.assertEqual(items[0]["source"], "News Desk")
        self.assertEqual(items[0]["url"], "https://news.example/a")

    def test_parse_atom(self):
        xml = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Story B</title><link href="https://atom.example/b" rel="alternate"/><summary>Summary B</summary><updated>2026-11-21T08:00:00Z</updated></entry></feed>"""
        items = parse_feed(xml, "https://atom.example/feed")
        self.assertEqual(items[0]["title"], "Story B")
        self.assertEqual(items[0]["url"], "https://atom.example/b")

    def test_skip_entry_without_link(self):
        xml = b"""<rss><channel><item><title>No link</title></item></channel></rss>"""
        self.assertEqual(parse_feed(xml, "https://example.com/feed"), [])

    def test_reject_http_and_local_hosts(self):
        for url in ("http://example.com/rss", "https://localhost/feed", "https://127.0.0.1/feed"):
            with self.assertRaises(ValueError):
                _validate_feed_url(url)


if __name__ == "__main__":
    unittest.main()
