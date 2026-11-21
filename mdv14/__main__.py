"""Run MD V14 from local JSON signals and optional RSS/Atom feeds."""
from __future__ import annotations

import argparse
import json

from .pipeline import collect_and_run, run_pipeline
from .storage import load_signals, save_json_atomic
from .sqlite_store import SQLiteTrendStore
from .trend_registry import signal_id


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the MD V14 intelligence pipeline.")
    parser.add_argument("input", nargs="?", help="Optional JSON array of local trend signals.")
    parser.add_argument("--feeds", help="Optional JSON array of RSS/Atom feed definitions.")
    parser.add_argument("--output", default="mdv14-report.json", help="Output report path.")
    parser.add_argument("--database", help="Optional SQLite path for persistent trend history.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum brief entries.")
    parser.add_argument("--date", default=None, help="Brief date in YYYY-MM-DD format.")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    local_signals = load_signals(args.input) if args.input else []
    if args.feeds:
        with open(args.feeds, "r", encoding="utf-8") as handle:
            feeds = json.load(handle)
        if not isinstance(feeds, list) or any(not isinstance(item, dict) for item in feeds):
            parser.error("--feeds must contain a JSON array of objects")
        report = collect_and_run(
            feeds, extra_signals=local_signals, brief_date=args.date, limit=args.limit
        )
    else:
        report = run_pipeline(local_signals, brief_date=args.date, limit=args.limit)

    if args.database:
        store = SQLiteTrendStore(args.database)
        store.record_signals(report["signals"])
        history = {item["signal_id"]: item for item in store.list_trends()}
        for item in report["signals"]:
            item["history"] = history.get(signal_id(item))
        for item in report["daily_brief"]["top_signals"]:
            item["history"] = history.get(signal_id(item))
        report["history"] = {
            "database": args.database,
            "tracked_trends": len(history),
            "observations_recorded": len(report["signals"]),
            "method": "earliest-versus-latest supplied score",
            "notice": "Historical score movement is descriptive, not a forecast.",
        }

    save_json_atomic(args.output, report)
    print(json.dumps({
        "output": args.output,
        "signals_received": report["registry_size"],
        "signals_in_brief": report["daily_brief"]["signals_included"],
        "signals_needing_review": report["evidence_review_required"],
        "feeds_succeeded": report.get("collection", {}).get("feeds_succeeded", 0),
        "history_tracked": report.get("history", {}).get("tracked_trends", 0),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
