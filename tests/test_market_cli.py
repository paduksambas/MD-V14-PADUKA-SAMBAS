import unittest
from unittest.mock import patch

from mdv14.__main__ import main


class PublicAssetCliTests(unittest.TestCase):
    def setUp(self):
        self.report = {
            "signals": [],
            "daily_brief": {"top_signals": [], "signals_included": 0},
            "registry_size": 0,
            "evidence_review_required": 0,
        }
        self.empty_market = {"observations": [], "observation_count": 0}

    def _run_with_patches(self, argv, asset_fetch):
        with patch("mdv14.__main__.run_pipeline", return_value=self.report), \
             patch("mdv14.__main__.fetch_public_market_data", return_value=self.empty_market), \
             patch("mdv14.__main__.fetch_fred_market_data", return_value=self.empty_market), \
             patch("mdv14.__main__.fetch_public_asset_data", asset_fetch), \
             patch("mdv14.__main__.save_json_atomic"), \
             patch("sys.argv", argv), \
             patch("builtins.print"):
            return main()

    def test_stooq_collection_is_disabled_by_default(self):
        with patch("mdv14.__main__.fetch_public_asset_data") as fetch:
            result = self._run_with_patches(["mdv14"], fetch)
            self.assertEqual(result, 0)
            fetch.assert_not_called()

    def test_stooq_collection_requires_and_honors_explicit_opt_in(self):
        fetch = patch("mdv14.__main__.fetch_public_asset_data",
                      return_value={"observations": [], "observation_count": 0}).start()
        self.addCleanup(patch.stopall)
        result = self._run_with_patches(["mdv14", "--enable-public-assets"], fetch)
        self.assertEqual(result, 0)
        fetch.assert_called_once()


if __name__ == "__main__":
    unittest.main()
