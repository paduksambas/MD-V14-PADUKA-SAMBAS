import os
import unittest
from unittest.mock import patch

from scripts import verify_cloudflare_access as verifier


APP = {
    "id": "app-123",
    "domain": "private.example.com/dashboard",
    "type": "self_hosted",
}
OWNER_POLICY = {
    "id": "policy-123",
    "decision": "allow",
    "include": [{"email": {"email": "owner@example.com"}}],
    "exclude": [],
}


class CloudflareAccessVerifierTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict(os.environ, {
            "CLOUDFLARE_API_TOKEN": "test-token",
            "CLOUDFLARE_ACCOUNT_ID": "account-123",
            "CLOUDFLARE_ACCESS_APP_ID": "app-123",
            "PADUKA_ACCESS_URL": "https://private.example.com/dashboard",
            "PADUKA_OWNER_EMAIL": "owner@example.com",
        })
        self.env.start()
        self.addCleanup(self.env.stop)

    @patch("scripts.verify_cloudflare_access.api_get")
    def test_uses_dedicated_policy_endpoint_and_accepts_owner_only_policy(self, api_get):
        api_get.side_effect = [
            {"success": True, "result": [APP]},
            {"success": True, "result": [OWNER_POLICY]},
        ]
        with patch("builtins.print") as output:
            verifier.main()
        self.assertIn("/access/apps/app-123/policies", api_get.call_args_list[1].args[0])
        self.assertIn("owner-only allow policy", output.call_args.args[0])

    @patch("scripts.verify_cloudflare_access.api_get")
    def test_rejects_broad_identity_policy(self, api_get):
        broad_policy = {
            **OWNER_POLICY,
            "include": [{"everyone": {}}],
        }
        api_get.side_effect = [
            {"success": True, "result": [APP]},
            {"success": True, "result": [broad_policy]},
        ]
        with self.assertRaises(SystemExit):
            verifier.main()

    @patch("scripts.verify_cloudflare_access.api_get")
    def test_rejects_additional_non_allow_policy(self, api_get):
        api_get.side_effect = [
            {"success": True, "result": [APP]},
            {"success": True, "result": [OWNER_POLICY, {
                "id": "policy-456", "decision": "bypass",
                "include": [{"everyone": {}}],
            }]},
        ]
        with self.assertRaises(SystemExit):
            verifier.main()

    @patch("scripts.verify_cloudflare_access.api_get")
    def test_rejects_url_outside_protected_path_before_policy_lookup(self, api_get):
        os.environ["PADUKA_ACCESS_URL"] = "https://private.example.com/other"
        api_get.return_value = {"success": True, "result": [APP]}
        with self.assertRaises(SystemExit):
            verifier.main()
        api_get.assert_not_called()

    @patch("scripts.verify_cloudflare_access.api_get")
    def test_rejects_empty_policy_list(self, api_get):
        api_get.side_effect = [
            {"success": True, "result": [APP]},
            {"success": True, "result": []},
        ]
        with self.assertRaises(SystemExit):
            verifier.main()


if __name__ == "__main__":
    unittest.main()
