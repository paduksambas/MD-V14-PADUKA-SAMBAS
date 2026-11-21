"""Persistent SQLite history for MD V14 trend signals and score observations."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from .trend_registry import signal_id
from .daily_brief import normalize_signal


class SQLiteTrendStore:
    """Store current trend metadata and append-only observations in SQLite."""

    def __init__(self, path: str | Path = "mdv14-history.sqlite3") -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS trends (
                    signal_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT NOT NULL,
                    category TEXT NOT NULL,
                    first_seen TEXT NOT NULL,
                    last_seen TEXT NOT NULL,
                    observation_count INTEGER NOT NULL DEFAULT 0
                );
                CREATE TABLE IF NOT EXISTS observations (
                    observation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    signal_id TEXT NOT NULL REFERENCES trends(signal_id),
                    observed_at TEXT NOT NULL,
                    score REAL NOT NULL,
                    payload_json TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_observations_signal_time
                    ON observations(signal_id, observed_at, observation_id);
            """)

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        return db

    def record_signals(
        self, signals: Iterable[dict[str, Any]], observed_at: str | None = None
    ) -> list[str]:
        """Upsert signal metadata and append one score observation per input signal."""
        timestamp = observed_at or datetime.now(timezone.utc).isoformat()
        datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        recorded: list[str] = []
        with self._connect() as db:
            for raw in signals:
                item = normalize_signal(raw)
                if not item["title"]:
                    continue
                key = signal_id(item)
                payload = json.dumps(raw, ensure_ascii=False, sort_keys=True, default=str)
                db.execute("""
                    INSERT INTO trends
                        (signal_id, title, source, url, category, first_seen, last_seen, observation_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                    ON CONFLICT(signal_id) DO UPDATE SET
                        title=excluded.title, source=excluded.source, url=excluded.url,
                        category=excluded.category, last_seen=excluded.last_seen,
                        observation_count=trends.observation_count + 1
                """, (key, item["title"], item["source"], item["url"], item["category"], timestamp, timestamp))
                db.execute("""
                    INSERT INTO observations (signal_id, observed_at, score, payload_json)
                    VALUES (?, ?, ?, ?)
                """, (key, timestamp, item["score"], payload))
                recorded.append(key)
        return recorded

    def get_observations(self, signal_key: str) -> list[dict[str, Any]]:
        """Return ordered score observations for descriptive trend analysis."""
        with self._connect() as db:
            rows = db.execute("""
                SELECT observed_at, score FROM observations
                WHERE signal_id = ?
                ORDER BY observed_at ASC, observation_id ASC
            """, (signal_key,)).fetchall()
        return [{"observed_at": row["observed_at"], "score": float(row["score"])}
                for row in rows]

    def get_growth(self, signal_key: str) -> dict[str, Any] | None:
        """Compare earliest and latest recorded score; this is descriptive, not predictive."""
        with self._connect() as db:
            trend = db.execute(
                "SELECT * FROM trends WHERE signal_id = ?", (signal_key,)
            ).fetchone()
        if trend is None:
            return None
        rows = self.get_observations(signal_key)
        first, latest = rows[0], rows[-1]
        delta = round(float(latest["score"]) - float(first["score"]), 2)
        direction = "rising" if delta > 0 else "falling" if delta < 0 else "stable"
        return {
            "signal_id": signal_key,
            "title": trend["title"],
            "first_seen": trend["first_seen"],
            "last_seen": trend["last_seen"],
            "observation_count": len(rows),
            "first_score": float(first["score"]),
            "latest_score": float(latest["score"]),
            "score_delta": delta,
            "direction": direction if len(rows) > 1 else "insufficient_history",
            "history_sufficient": len(rows) > 1,
            "notice": "Descriptive change in supplied scores; not a probability or forecast.",
        }

    def list_trends(self) -> list[dict[str, Any]]:
        with self._connect() as db:
            rows = db.execute(
                "SELECT signal_id FROM trends ORDER BY last_seen DESC, signal_id"
            ).fetchall()
        return [self.get_growth(row["signal_id"]) for row in rows]
