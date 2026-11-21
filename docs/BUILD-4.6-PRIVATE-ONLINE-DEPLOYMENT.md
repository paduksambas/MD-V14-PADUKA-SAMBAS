# Build 4.6 — Private Online Deployment Foundation

## Current architecture
The source repository remains public. It is used for code, automated tests, and builds. Private dashboard output must never be committed or uploaded as a normal GitHub Actions artifact.

## Intended deployment
- GitHub Actions: manual deployment workflow only (`.github/workflows/paduka-private-deploy.yml`).
- Cloudflare Pages: serves the generated static dashboard.
- Cloudflare Access: authentication gate in front of the Pages hostname; policy must allow only the owner's email identity.
- No dashboard deployment is considered secure until Access is enabled and verified with both a denied anonymous request and an allowed owner login.

## Required repository secrets
Set these only after creating the Pages project and configuring the Access policy:
- `CLOUDFLARE_API_TOKEN`: token scoped to Pages deployment permissions.
- `CLOUDFLARE_ACCOUNT_ID`: Cloudflare account identifier.
- `CLOUDFLARE_PAGES_PROJECT`: existing Pages project name.
- `PADUKA_ACCESS_PROTECTION_CONFIRMED`: exact value `YES`; deployment gate only, not proof of Access configuration.
- `FRED_API_KEY`, `BPS_API_KEY`: optional provider credentials; never placed in dashboard HTML.

## Deployment safety gate
The manual workflow refuses to run unless the Access confirmation gate and Cloudflare credentials/project are present. The confirmation secret is a human-controlled guard and **does not configure or verify Cloudflare Access**.

## Required operator steps before first deployment
1. Create a Cloudflare Pages project for PADUKA.
2. Configure Cloudflare Access to require identity authentication and allow only the owner's email. Use a deny-by-default policy.
3. Test Access on the Pages hostname: logged-out/incognito must be denied; the owner account must be allowed.
4. Add the deployment secrets listed above to GitHub repository settings.
5. Only then set `PADUKA_ACCESS_PROTECTION_CONFIRMED=YES` and run the workflow manually.
6. Re-test Access after deployment. Do not share the hostname as proof of privacy.

## Status and limitations
This build adds deployment preparation only. It does not create a Cloudflare account/project, configure an Access policy, add secrets, or publish the site. No private dashboard is online yet. Dashboard HTML is a snapshot of data at build time; it is not a live-updating backend.
