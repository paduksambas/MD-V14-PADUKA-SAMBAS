"""Tests for scheduled collection-cycle monitoring summaries."""
import unittest

from mdv14.monitoring import build_monitoring_status


class MonitoringTests(unittest.TestCase):
    def test_healthy_cycle_and_freshness_counts(self):
        result = build_monitoring_status(
            {"feed_results": [
                {"feed_url": "https://a.example/rss", "ok": True, "item_count": 2},
                {"feed_url": "https://b.example/rss", "ok": True, "item_count": 1},
            ]},
            [
                {"published_at": "2026-11-21T09:00:00Z"},
                {"published_at": "2026-11-20T01:00:00Z"},
                {"published_at": "not-a-date"},
            ],
            generated_at="2026-11-21T10:00:00Z",
        )
        self.assertEqual(result["cycle_status"], "healthy")
        self.assertEqual(result["feeds_succeeded"], 2)
        self.assertEqual(result["signals_published_within_window"], 1)
        self.assertEqual(result["signals_with_unknown_published_at"], 1)

    def test_degraded_and_unavailable_feed_states(self):
        degraded = build_monitoring_status(
            {"feed_results": [{"ok": True}, {"ok": False}]}, [], generated_at="2026-11-21T10:00:00Z"
        )
        unavailable = build_monitoring_status(
            {"feed_results": [{"ok": False}]}, [], generated_at="2026-11-21T10:00:00Z"
        )
        self.assertEqual(degraded["cycle_status"], "degraded")
        self.assertEqual(unavailable["cycle_status"], "unavailable")

    def test_no_feeds_is_not_configured(self):
        result = build_monitoring_status({}, [], generated_at="2026-11-21T10:00:00Z")
        self.assertEqual(result["cycle_status"], "not_configured")

    def test_future_publication_timestamp_is_reported(self):
        result = build_monitoring_status(
            {"feed_results": [{"ok": True}]},
            [{"published_at": "2026-11-22T10:00:00Z"}],
            generated_at="2026-11-21T10:00:00Z",
        )
        self.assertEqual(result["signals_with_future_published_at"], 1)
        self.assertEqual(result["signals_published_within_window"], 0)

    def test_invalid_window_and_timestamp_rejected(self):
        with self.assertRaises(ValueError):
            build_monitoring_status({}, [], freshness_hours=0)
        with self.assertRaises(ValueError):
            build_monitoring_status({}, [], generated_at="bad-date")


if __name__ == "__main__":
    unittest.main()
