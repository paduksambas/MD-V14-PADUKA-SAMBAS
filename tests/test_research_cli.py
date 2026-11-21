"""Regression tests for the Build 2.3 research CLI integration."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from mdv14.__main__ import main


class ResearchCLITests(unittest.TestCase):
    def test_cli_passes_question_and_reports_review_count(self):
        report = {
            "signals": [],
            "registry_size": 0,
            "daily_brief": {"signals_included": 0, "top_signals": []},
            "evidence_review_required": 0,
            "collection": {"feeds_succeeded": 1},
            "research": {"records_reviewed": 3},
        }
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "research.json"
            feeds = Path(directory) / "feeds.json"
            feeds.write_text('[{"id":"desk","name":"Desk","url":"https://example.com/rss"}]', encoding="utf-8")
            argv = ["mdv14", "--feeds", str(feeds), "--research-question", "AI chip supply", "--output", str(output)]
            with patch.object(sys, "argv", argv), patch("mdv14.__main__.collect_and_run", return_value=report) as collect:
                self.assertEqual(main(), 0)
            self.assertEqual(collect.call_args.kwargs["research_question"], "AI chip supply")
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["research"]["records_reviewed"], 3)

    def test_cli_requires_feeds_for_research_question(self):
        with patch.object(sys, "argv", ["mdv14", "--research-question", "AI chip supply"]):
            with self.assertRaises(SystemExit) as raised:
                main()
        self.assertEqual(raised.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
