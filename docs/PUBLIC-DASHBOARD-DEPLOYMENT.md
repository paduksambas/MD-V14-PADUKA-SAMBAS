# Public Dashboard Deployment (Cloudflare Pages)

This guide publishes the generated static dashboard intentionally as a **public** site. Do not use Cloudflare Access, Zero Trust, or private deployment workflows for this public option.

## Cloudflare Pages settings

Connect this GitHub repository: `paduksambas/MD-V14-PADUKA-SAMBAS`, branch `main`.

- Framework preset: **None**
- Build command: `bash scripts/build_public_dashboard.sh`
- Build output directory: `public`
- Root directory: `/`
- Python: **3.11** (if the build environment exposes a Python version setting, set it to 3.11)

The build script creates only `public/index.html` for publication. The generated report JSON is stored in a temporary file outside the publish directory and deleted when the build finishes. The build validation workflow independently checks the same script on GitHub Actions.

## Public-data and safety note

A public dashboard can be viewed by anyone. The configured sample feeds and public macroeconomic observations are intended for display. Never add API keys, private feed URLs, confidential BPS exports, raw personal information, or private report files to the public build or repository.

## Validate before going live

1. Confirm the Pages build command and output directory exactly match the settings above.
2. Check the build log is successful.
3. Open the public Pages URL and verify the dashboard loads.
4. Verify that no secrets or private source data are shown.

This repository does not claim a public URL is live until a successful Pages deployment is confirmed.
