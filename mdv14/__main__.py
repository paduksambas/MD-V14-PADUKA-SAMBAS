"""Run MD V14 from local JSON signals and optional RSS/Atom feeds."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .pipeline import collect_and_run, run_pipeline
from .storage import load_signals, save_json_atomic
from .sqlite_store import SQLiteTrendStore
from .trend_registry import signal_id
from .dashboard import build_dashboard_html
from .advanced_scoring import assess_advanced_trend


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the MD V14 intelligence pipeline.")
    parser.add_argument("input", nargs="?", help="Optional JSON array of local trend signals.")
    parser.add_argument("--feeds", help="Optional JSON array of RSS/Atom feed definitions.")
    parser.add_argument("--output", default="mdv14-report.json", help="Output report path.")
    parser.add_argument("--database", help="Optional SQLite path for persistent trend history.")
    parser.add_argument("--dashboard", help="Optional path for a self-contained HTML dashboard.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum brief entries.")
    parser.add_argument("--date", default=None, help="Brief date in YYYY-MM-DD format.")
    parser.add_argument("--research-question", default=None, help="Optional question for the auditable multi-source research report (requires --feeds).")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    local_signals = load_signals(args.input) if args.input else []
    if args.research_question and not args.feeds:
        parser.error("--research-question requires --feeds")
    if args.feeds:
        with open(args.feeds, "r", encoding="utf-8") as handle:
            feeds = json.load(handle)
        if not isinstance(feeds, list) or any(not isinstance(item, dict) for item in feeds):
            parser.error("--feeds must contain a JSON array of objects")
        report = collect_and_run(
            feeds, extra_signals=local_signals, brief_date=args.date, limit=args.limit,
            research_question=args.research_question
        )
    else:
        report = run_pipeline(local_signals, brief_date=args.date, limit=args.limit)

    store = SQLiteTrendStore(args.database) if args.database else None
    if store:
        store.record_signals(report["signals"])
        history = {item["signal_id"]: item for item in store.list_trends()}
        report["history"] = {
            "database": args.database,
            "tracked_trends": len(history),
            "observations_recorded": len(report["signals"]),
            "method": "earliest-versus-latest supplied score",
            "notice": "Historical score movement is descriptive, not a forecast.",
        }
    for item in report["signals"]:
        key = signal_id(item)
        observations = store.get_observations(key) if store else []
        item["advanced_intelligence"] = assess_advanced_trend(
            observations, current_score=item.get("score", 0)
        )
        if store:
            item["history"] = store.get_growth(key)
    for item in report["daily_brief"]["top_signals"]:
        key = signal_id(item)
        match = next((entry for entry in report["signals"] if signal_id(entry) == key), None)
        if match:
            item["advanced_intelligence"] = match["advanced_intelligence"]
            if store:
                item["history"] = match.get("history")

    save_json_atomic(args.output, report)
    if args.dashboard:
        dashboard_path = Path(args.dashboard)
        dashboard_path.parent.mkdir(parents=True, exist_ok=True)
        dashboard_path.write_text(build_dashboard_html(report), encoding="utf-8")

    print(json.dumps({
        "output": args.output,
        "dashboard": args.dashboard,
        "signals_received": report["registry_size"],
        "signals_in_brief": report["daily_brief"]["signals_included"],
        "signals_needing_review": report["evidence_review_required"],
        "feeds_succeeded": report.get("collection", {}).get("feeds_succeeded", 0),
        "history_tracked": report.get("history", {}).get("tracked_trends", 0),
        "research_records_reviewed": report.get("research", {}).get("records_reviewed", 0),
        "analyst_report_findings": len(report.get("analyst_report", {}).get("key_findings", [])),
        "analyst_report_actions": len(report.get("analyst_report", {}).get("recommended_human_actions", [])),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
