# Public Dashboard Deployment (GitHub Pages)

This repository deploys the public static dashboard automatically to GitHub Pages from branch `main` using GitHub Actions.

## Deployment workflow

Workflow: `.github/workflows/pages-deploy.yml`

- Builds the dashboard with `bash scripts/build_public_dashboard.sh`
- Publishes only `public/index.html`
- Deploys to GitHub Pages after successful artifact validation
- Runs on relevant changes to `main` and via manual workflow dispatch

Expected public URL:

`https://paduksambas.github.io/MD-V14-PADUKA-SAMBAS/`

The URL is not considered live until the GitHub Pages deployment job succeeds and the page can be opened.

## If the first deployment requires Pages activation

In repository Settings → Pages, set **Build and deployment → Source** to **GitHub Actions**. Then open Actions → **Deploy PADUKA public dashboard to GitHub Pages** and run it with **Run workflow** if it has not automatically deployed.

## Privacy and output

The generated report JSON is stored in a temporary file outside the publish directory and removed at build completion. The build validation checks that the Pages artifact contains only the generated HTML file.

A public dashboard is visible to everyone. Do not include API keys, private feed URLs, confidential BPS exports, personal information, or private report files in the public build.
