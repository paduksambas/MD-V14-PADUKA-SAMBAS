# Build 4.6 — Private Online Deployment (Access policy verification)

## Deployment architecture
- Public GitHub repository stores source and workflows only.
- Manual GitHub Actions build creates a transient report/dashboard in runner storage.
- Cloudflare Pages hosts the dashboard.
- Cloudflare Access must restrict the hostname to the owner's exact email.
- Deployment is blocked unless the workflow reads and verifies the Access application policy before deploying.

## GitHub repository secrets
Configure only after Cloudflare Pages and Access have been set up:

- `CLOUDFLARE_API_TOKEN`: scoped token with Cloudflare Pages deployment permissions and Access Apps/Policies read permissions.
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_PAGES_PROJECT`
- `CLOUDFLARE_ACCESS_APP_ID`: UUID of the Access application protecting PADUKA.
- `PADUKA_ACCESS_URL`: the owner-protected HTTPS URL.
- `PADUKA_OWNER_EMAIL`: the exact owner identity allowed to access.
- `PADUKA_ACCESS_PROTECTION_CONFIRMED`: exact value `YES`; manual operator confirmation.
- `FRED_API_KEY` and `BPS_API_KEY`: optional private data credentials.

## Automated fail-closed checks
The workflow validates required secrets and then runs `scripts/verify_cloudflare_access.py` before deployment. The verifier checks:
1. Access application ID exists in the Cloudflare account.
2. Application is a self-hosted Access app.
3. The Access application's hostname matches the deployment URL hostname.
4. Exactly one Allow policy exists, and its sole Include rule is the exact owner email.
5. Bypass/non-identity policies, broad Allow rules, extra Include rules, and Exclude rules cause a failure.

This is a policy-shape check, not an end-to-end login test. Before declaring the dashboard private and operational, test an anonymous/incognito request is blocked and the owner's authenticated login succeeds. Cloudflare API verification depends on a token with Access Apps and Policies read permission.

## Deployment status
No Cloudflare account/project/policies or repository secrets are configured by this change. The dashboard remains offline until setup and deployment succeed. Reports are not committed or uploaded as Actions artifacts.
