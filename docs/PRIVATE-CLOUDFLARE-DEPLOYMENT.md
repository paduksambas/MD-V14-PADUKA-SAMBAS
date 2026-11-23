# PADUKA private Cloudflare Pages deployment checklist

This workflow is separate from the public GitHub Pages snapshot. The public GitHub Pages site remains public. The Cloudflare workflow is intended only for an owner-only private dashboard.

## Required GitHub Actions secrets

Create these repository Actions secrets. Enter their values directly in GitHub Settings; never paste them into issues, pull requests, workflow logs, or chat.

- `PADUKA_ACCESS_PROTECTION_CONFIRMED` — exact value `YES`, confirming that owner-only Cloudflare Access is configured
- `CLOUDFLARE_API_TOKEN` — token used by the verifier and Wrangler
- `CLOUDFLARE_ACCOUNT_ID`
- `CLOUDFLARE_PAGES_PROJECT` — Pages project name (1–58 lowercase letters, digits, or hyphens)
- `CLOUDFLARE_ACCESS_APP_ID` — ID of the self-hosted Access application
- `PADUKA_ACCESS_URL` — clean HTTPS URL on the protected custom domain
- `PADUKA_OWNER_EMAIL` — exact email allowed by the Access policy

Optional data-provider secrets: `FRED_API_KEY` and `BPS_API_KEY`. The preflight requires the seven configuration secrets above; data-provider keys are optional.

Only trusted maintainers should have write access to this public repository. A user who can run a workflow that has access to repository secrets must be trusted with those secrets.

## Safe preflight (does not deploy)

1. Open **Actions** in the GitHub repository.
2. Select **PADUKA private dashboard deploy (manual)**.
3. Choose **Run workflow** on the `main` branch.
4. Leave **deploy_now** set to **false**.
5. Run the workflow and confirm all steps succeed, especially **Verify Cloudflare Access owner-only policy before deployment**.

Preflight checks that the required secrets are present, the Pages project name is syntactically valid, the configured Access application is a self-hosted app on the configured hostname/path, and it has exactly one Allow policy for the owner email. The verifier rejects bypass/non-Allow policies, broad identity rules, extra allow identities, exclusions, and non-default URL ports.

A successful preflight verifies the configured custom-domain Access application only. It does **not** verify the privacy of the Pages default `pages.dev` hostname or preview deployment URLs.

## Before any real deployment

In Cloudflare Pages, confirm that the project's default `pages.dev` address and all preview deployment URLs are disabled or independently protected by an owner-only Cloudflare Access policy. Do not proceed on the assumption that protecting the custom domain automatically protects these alternate hostnames.

The build creates its JSON report in a temporary file outside the deployment directory and removes it at the end of the build step. The Cloudflare upload is restricted to the single self-contained `build/index.html` file. That HTML still contains the dashboard's rendered information, so the hostname serving it must remain owner-only.

After the first safe preflight passes and the Cloudflare alternate-hostname exposure has been checked, run the workflow again and deliberately set **deploy_now** to **true** only when you intend to publish the private dashboard.

## Important separation

- GitHub Pages: public static dashboard; do not put confidential inputs into it.
- Cloudflare Pages: separate private dashboard; owner-only access must remain enforced.
- Scheduled monitoring: report and SQLite history remain transient on the GitHub Actions runner and are not deployed as artifacts.
