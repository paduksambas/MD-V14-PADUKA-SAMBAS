"""Run MD V14 from local JSON signals and optional RSS/Atom feeds."""
from __future__ import annotations

import argparse
import json
import os
from datetime import date, timedelta
from pathlib import Path

from .pipeline import collect_and_run, run_pipeline
from .storage import load_signals, save_json_atomic
from .sqlite_store import SQLiteTrendStore
from .trend_registry import signal_id
from .dashboard import build_dashboard_html
from .advanced_scoring import assess_advanced_trend
from .economic_data import fetch_world_bank_indicators
from .market_data import fetch_fred_market_data, fetch_public_market_data
from .market_analytics import build_market_analytics
from .public_assets import fetch_public_asset_data
from .commodity_data import fetch_world_bank_commodity_data


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
    parser.add_argument("--economic-countries", default="", help="Optional comma-separated ISO alpha-2 country codes for World Bank indicators, e.g. ID,US,CN.")
    parser.add_argument("--economic-start-year", type=int, default=2020, help="First World Bank observation year (default: 2020).")
    parser.add_argument("--economic-end-year", type=int, default=None, help="Last World Bank observation year (default: current year).")
    parser.add_argument("--fred-api-key-env", default="FRED_API_KEY", help="Environment variable holding an optional FRED API key (default: FRED_API_KEY).")
    parser.add_argument("--market-start-date", default=None, help="First public FX/asset/FRED observation date (YYYY-MM-DD; default: 30 days before today).")
    parser.add_argument("--market-end-date", default=None, help="Last public-market observation date (default: today).")
    parser.add_argument("--enable-public-assets", action="store_true", help="Opt in to Stooq daily equity/commodity history; disabled by default because the free endpoint may rate-limit automated runners.")
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

    if args.economic_countries.strip():
        try:
            report["economic_data"] = fetch_world_bank_indicators(
                args.economic_countries, start_year=args.economic_start_year,
                end_year=args.economic_end_year,
            )
        except ValueError as exc:
            parser.error(str(exc))
    market_start_date = args.market_start_date or (date.today() - timedelta(days=30)).isoformat()
    market_end_date = args.market_end_date or date.today().isoformat()
    report["market_data"] = fetch_public_market_data(
        start_date=market_start_date, end_date=market_end_date,
    )
    if args.enable_public_assets:
        report["public_asset_data"] = fetch_public_asset_data(
            start_date=market_start_date, end_date=market_end_date,
        )
    else:
        report["public_asset_data"] = {
            "build": "3.6", "provider": "Stooq public daily CSV",
            "status": "not_requested", "request_count": 0,
            "requests_succeeded": 0, "requests_failed": 0,
            "observation_count": 0, "observations": [], "errors": [],
            "limitations": [
                "Stooq collection is opt-in via --enable-public-assets because its free endpoint may rate-limit automated runner IPs.",
                "No public asset observations were requested in this run.",
            ],
        }
    report["commodity_data"] = fetch_world_bank_commodity_data(
        start_date=(date.today().replace(year=date.today().year - 2)).isoformat(),
        end_date=market_end_date,
    )
    try:
        report["fred_market_data"] = fetch_fred_market_data(
            os.environ.get(args.fred_api_key_env), start_date=market_start_date,
            end_date=market_end_date,
        )
    except ValueError as exc:
        parser.error(str(exc))
    report['market_analytics'] = build_market_analytics(report.get('market_data', {}), report.get('fred_market_data', {}), report.get('public_asset_data', {}), report.get('commodity_data', {}))
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
        "command_center_build": report.get("command_center", {}).get("build"),
        "command_center_posture": report.get("command_center", {}).get("strategic_posture", {}).get("status"),
        "command_center_operational_state": report.get("command_center", {}).get("operational_state"),
        "country_explorer_build": report.get("country_explorer", {}).get("build"),
        "countries_mapped": report.get("country_explorer", {}).get("countries_mapped", 0),
        "countries_unmapped": report.get("country_explorer", {}).get("countries_unmapped", 0),
        "economic_intelligence_build": report.get("economic_intelligence", {}).get("build"),
        "economic_signals_classified": report.get("economic_intelligence", {}).get("signals_assessed", 0),
        "economic_sectors_represented": report.get("economic_intelligence", {}).get("sector_count", 0),
        "economic_data_build": report.get("economic_data", {}).get("build"),
        "economic_data_observations": report.get("economic_data", {}).get("observation_count", 0),
        "economic_data_requests_succeeded": report.get("economic_data", {}).get("requests_succeeded", 0),
        "economic_data_requests_failed": report.get("economic_data", {}).get("requests_failed", 0),
        "market_data_build": report.get("market_data", {}).get("build"),
        "market_data_status": report.get("market_data", {}).get("status"),
        "market_data_observations": report.get("market_data", {}).get("observation_count", 0),
        "market_data_requests_succeeded": report.get("market_data", {}).get("requests_succeeded", 0),
        "market_data_requests_failed": report.get("market_data", {}).get("requests_failed", 0),
        "fred_market_data_status": report.get("fred_market_data", {}).get("status"),
        "fred_market_data_observations": report.get("fred_market_data", {}).get("observation_count", 0),
        "public_asset_data_build": report.get("public_asset_data", {}).get("build"),
        "public_asset_data_status": report.get("public_asset_data", {}).get("status"),
        "public_asset_data_observations": report.get("public_asset_data", {}).get("observation_count", 0),
        "public_asset_data_requests_succeeded": report.get("public_asset_data", {}).get("requests_succeeded", 0),
        "public_asset_data_requests_failed": report.get("public_asset_data", {}).get("requests_failed", 0),
        "public_asset_data_errors": report.get("public_asset_data", {}).get("errors", [])[:6],
        "market_analytics_build": report.get("market_analytics", {}).get("build"),
        "market_analytics_status": report.get("market_analytics", {}).get("status"),
        "market_analytics_series": report.get("market_analytics", {}).get("series_analyzed", 0),
        "commodity_data_build": report.get("commodity_data", {}).get("build"),
        "commodity_data_status": report.get("commodity_data", {}).get("status"),
        "commodity_data_observations": report.get("commodity_data", {}).get("observation_count", 0),
        "commodity_data_requests_failed": report.get("commodity_data", {}).get("requests_failed", 0),
        "commodity_data_errors": report.get("commodity_data", {}).get("errors", []),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
