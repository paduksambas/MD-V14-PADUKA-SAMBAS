import unittest
from unittest.mock import patch

from scripts import verify_cloudflare_access as verifier


OWNER = "owner@example.com"
APP_ID = "app-uuid"


def app_with_domain(domain="private.example.com"):
    return {"id": APP_ID, "domain": domain, "type": "self_hosted"}


def owner_policy(include=None, decision="allow"):
    return {
        "decision": decision,
        "include": include if include is not None else [{"email": {"email": OWNER}}],
        "exclude": [],
    }


class CloudflareAccessVerifierTests(unittest.TestCase):
    def run_verifier(self, app=None, policies=None, access_url="https://private.example.com/dashboard"):
        env = {
            "CLOUDFLARE_API_TOKEN": "test-token",
            "CLOUDFLARE_ACCOUNT_ID": "account",
            "CLOUDFLARE_ACCESS_APP_ID": APP_ID,
            "PADUKA_ACCESS_URL": access_url,
            "PADUKA_OWNER_EMAIL": OWNER,
        }
        responses = [
            {"success": True, "result": [app or app_with_domain()]},
            {"success": True, "result": policies if policies is not None else [owner_policy()]},
        ]
        with patch.dict("os.environ", env, clear=True), patch.object(
            verifier, "api_get", side_effect=responses
        ) as api:
            verifier.main()
        return api

    def test_exact_owner_policy_passes_using_dedicated_endpoint(self):
        api = self.run_verifier()
        self.assertIn("/access/apps/app-uuid/policies", api.call_args_list[1].args[0])

    def test_everyone_allow_rule_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(policies=[owner_policy(include=[{"everyone": {}}])])

    def test_extra_allow_identity_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(policies=[owner_policy(include=[
                {"email": {"email": OWNER}},
                {"email": {"email": "other@example.com"}},
            ])])

    def test_host_mismatch_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(app=app_with_domain("public.example.com"))

    def test_bypass_policy_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(policies=[owner_policy(decision="bypass")])

    def test_non_allow_policy_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(policies=[owner_policy(decision="deny")])

    def test_unprotected_path_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(
                app=app_with_domain("private.example.com/private"),
                access_url="https://private.example.com/dashboard",
            )

    def test_access_url_query_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(access_url="https://private.example.com/dashboard?share=1")

    def test_access_url_custom_port_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(access_url="https://private.example.com:8443/dashboard")

    def test_access_app_custom_port_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(app=app_with_domain("private.example.com:8443"))

    def test_multiple_owner_allow_policies_are_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(policies=[owner_policy(), owner_policy()])

    def test_email_rule_with_extra_condition_is_rejected(self):
        with self.assertRaises(SystemExit):
            self.run_verifier(policies=[owner_policy(include=[
                {"email": {"email": OWNER, "domain": "example.com"}}
            ])])


if __name__ == "__main__":
    unittest.main()
