"""Tests for the RSS/Atom collector without external network access."""
import unittest
from mdv14.rss_collector import _validate_feed_url, parse_feed


class RSSCollectorTests(unittest.TestCase):
    def test_parse_rss(self):
        xml = b"""<rss version="2.0"><channel><item><title>Story A</title><link>https://news.example/a</link><description>Summary A</description><pubDate>Sat, 21 Nov 2026 08:00:00 GMT</pubDate><author>Reporter A</author><category>World</category></item></channel></rss>"""
        items = parse_feed(xml, "https://news.example/rss", "News Desk")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Story A")
        self.assertEqual(items[0]["source"], "News Desk")
        self.assertEqual(items[0]["url"], "https://news.example/a")
        self.assertEqual(items[0]["author"], "Reporter A")
        self.assertEqual(items[0]["topics"], ["World"])

    def test_parse_atom(self):
        xml = b"""<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Story B</title><link href="https://atom.example/b" rel="alternate"/><summary>Summary B</summary><updated>2026-11-21T08:00:00Z</updated><author><name>Reporter B</name></author><category term="Science"/></entry></feed>"""
        items = parse_feed(xml, "https://atom.example/feed")
        self.assertEqual(items[0]["title"], "Story B")
        self.assertEqual(items[0]["url"], "https://atom.example/b")
        self.assertEqual(items[0]["author"], "Reporter B")
        self.assertEqual(items[0]["topics"], ["Science"])

    def test_skip_entry_without_link(self):
        xml = b"""<rss><channel><item><title>No link</title></item></channel></rss>"""
        self.assertEqual(parse_feed(xml, "https://example.com/feed"), [])

    def test_reject_unsafe_article_links(self):
        xml = b"""<rss><channel>
        <item><title>Script</title><link>javascript:alert(1)</link></item>
        <item><title>File</title><link>file:///etc/passwd</link></item>
        <item><title>Credentials</title><link>https://user:pass@news.example/story</link></item>
        <item><title>Hostless</title><link>https:///missing-host</link></item>
        <item><title>Safe HTTP</title><link>http://news.example/story</link></item>
        <item><title>Safe HTTPS</title><link>https://news.example/story</link></item>
        </channel></rss>"""
        items = parse_feed(xml, "https://news.example/feed")
        self.assertEqual([item["title"] for item in items], ["Safe HTTP", "Safe HTTPS"])

    def test_reject_http_and_local_hosts(self):
        for url in ("http://example.com/rss", "https://localhost/feed", "https://127.0.0.1/feed"):
            with self.assertRaises(ValueError):
                _validate_feed_url(url)


if __name__ == "__main__":
    unittest.main()
