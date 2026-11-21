"""Runtime tests for persistent SQLite trend history."""
import tempfile
import unittest
from pathlib import Path

from mdv14.sqlite_store import SQLiteTrendStore


class SQLiteTrendStoreTests(unittest.TestCase):
    def test_persists_across_instances_and_tracks_score_delta(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "history.sqlite3"
            first = SQLiteTrendStore(path)
            signal = {"title": "AI regulation update", "source": "Desk",
                      "url": "https://example.org/story", "score": 25}
            keys = first.record_signals([signal], "2026-11-20T10:00:00+00:00")
            second = SQLiteTrendStore(path)
            updated = {**signal, "score": 68}
            second.record_signals([updated], "2026-11-21T10:00:00+00:00")
            store = SQLiteTrendStore(path)
            growth = store.get_growth(keys[0])
            self.assertEqual(growth["observation_count"], 2)
            self.assertEqual(growth["score_delta"], 43.0)
            self.assertEqual(growth["direction"], "rising")
            self.assertTrue(growth["history_sufficient"])
            self.assertEqual([row["score"] for row in store.get_observations(keys[0])], [25.0, 68.0])

    def test_first_observation_is_not_called_a_trend(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteTrendStore(Path(directory) / "history.sqlite3")
            key = store.record_signals([{
                "title": "Single observation", "source": "Desk",
                "url": "https://example.org/one", "score": 50,
            }], "2026-11-21T10:00:00+00:00")[0]
            growth = store.get_growth(key)
            self.assertEqual(growth["direction"], "insufficient_history")
            self.assertFalse(growth["history_sufficient"])

    def test_invalid_timestamp_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            store = SQLiteTrendStore(Path(directory) / "history.sqlite3")
            with self.assertRaises(ValueError):
                store.record_signals([{"title": "X", "url": "https://x.test"}], "not-a-date")
            self.assertEqual(store.list_trends(), [])


if __name__ == "__main__":
    unittest.main()
