from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "paduka-private-deploy.yml"


class PrivateDeployWorkflowSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow = WORKFLOW.read_text(encoding="utf-8")

    def test_manual_dispatch_defaults_to_preflight_only(self):
        self.assertIn("deploy_now:", self.workflow)
        self.assertIn("default: false", self.workflow)
        self.assertIn("if: ${{ !inputs.deploy_now }}", self.workflow)

    def test_deployment_requires_explicit_opt_in(self):
        self.assertIn("if: ${{ inputs.deploy_now }}", self.workflow)

    def test_cloudflare_action_is_pinned_to_full_commit_sha(self):
        self.assertIn(
            "uses: cloudflare/wrangler-action@953926a2e2182532811c01a25e53647d93bf07c0 # v4",
            self.workflow,
        )

    def test_access_verification_precedes_deployment(self):
        verify = self.workflow.index("Verify Cloudflare Access owner-only policy")
        deploy = self.workflow.index("Deploy behind verified Cloudflare Access")
        self.assertLess(verify, deploy)


if __name__ == "__main__":
    unittest.main()
