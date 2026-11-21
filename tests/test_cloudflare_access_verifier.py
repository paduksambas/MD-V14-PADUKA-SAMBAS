import unittest
from unittest.mock import patch

from scripts import verify_cloudflare_access as verifier


OWNER = "owner@example.com"
APP_ID = "app-uuid"


def app_with_policy(include=None, decision="allow", domain="private.example.com"):
    return {
        "id": APP_ID,
        "domain": domain,
        "type": "self_hosted",
        "policies": [{
            "decision": decision,
            "include": include if include is not None else [{"email": {"email": OWNER}}],
            "exclude": [],
        }],
    }


class CloudflareAccessVerifierTests(unittest.TestCase):
    def run_verifier(self, app, access_url="https://private.example.com/dashboard"):
        env = {
            "CLOUDFLARE_API_TOKEN": "test-token",
            "CLOUDFLARE_ACCOUNT_ID": "account",
            "CLOUDFLARE_ACCESS_APP_ID": APP_ID,
            "PADUKA_ACCESS_URL": access_url,
            "PADUKA_OWNER_EMAIL": OWNER,
        }
        with patch.dict("os.environ", env, clear=True), patch.object(
            verifier, "api_get", return_value={"success": True, "result": [app]}
        ):
            verifier.main()

    def test_exact_owner_policy_passes(self):
        self.run_verifier(app_with_policy())

    def test_everyone_allow_rule_is_rejected(self):
        app = app_with_policy(include=[{"everyone": {}}])
        with self.assertRaises(SystemExit):
            self.run_verifier(app)

    def test_extra_allow_identity_is_rejected(self):
        app = app_with_policy(include=[
            {"email": {"email": OWNER}},
            {"email": {"email": "other@example.com"}},
        ])
        with self.assertRaises(SystemExit):
            self.run_verifier(app)

    def test_host_mismatch_is_rejected(self):
        app = app_with_policy(domain="public.example.com")
        with self.assertRaises(SystemExit):
            self.run_verifier(app)

    def test_bypass_policy_is_rejected(self):
        app = app_with_policy(decision="bypass")
        with self.assertRaises(SystemExit):
            self.run_verifier(app)

    def test_non_allow_policy_is_rejected(self):
        app = app_with_policy(decision="deny")
        with self.assertRaises(SystemExit):
            self.run_verifier(app)

    def test_unprotected_path_is_rejected(self):
        app = app_with_policy(domain="private.example.com/private")
        with self.assertRaises(SystemExit):
            self.run_verifier(app, access_url="https://private.example.com/dashboard")

    def test_access_url_query_is_rejected(self):
        app = app_with_policy()
        with self.assertRaises(SystemExit):
            self.run_verifier(app, access_url="https://private.example.com/dashboard?share=1")

    def test_email_rule_with_extra_condition_is_rejected(self):
        app = app_with_policy(include=[{"email": {"email": OWNER, "domain": "example.com"}}])
        with self.assertRaises(SystemExit):
            self.run_verifier(app)


if __name__ == "__main__":
    unittest.main()
