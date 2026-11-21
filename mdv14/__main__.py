"""Run MD V14 from a JSON signal file."""
from __future__ import annotations

import argparse
import json

from .pipeline import run_pipeline
from .storage import load_signals, save_json_atomic


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the MD V14 intelligence pipeline.")
    parser.add_argument("input", help="Path to a JSON array of trend signals.")
    parser.add_argument("--output", default="mdv14-report.json", help="Output report path.")
    parser.add_argument("--limit", type=int, default=10, help="Maximum brief entries.")
    parser.add_argument("--date", default=None, help="Brief date in YYYY-MM-DD format.")
    args = parser.parse_args()

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    signals = load_signals(args.input)
    report = run_pipeline(signals, brief_date=args.date, limit=args.limit)
    save_json_atomic(args.output, report)
    print(json.dumps({
        "output": args.output,
        "signals_received": report["registry_size"],
        "signals_in_brief": report["daily_brief"]["signals_included"],
        "signals_needing_review": report["evidence_review_required"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
