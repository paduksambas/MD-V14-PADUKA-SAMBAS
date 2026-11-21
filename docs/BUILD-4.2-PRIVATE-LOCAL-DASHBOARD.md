# Build 4.2 — Private Local Dashboard & Live WIB Clock

## What changed
- Adds a browser clock using the `Asia/Jakarta` time zone, refreshed every second.
- Shows the latest report-generation timestamp and collection-cycle status.
- Shows the status field for configured World Bank, market, commodity, BPS, and FRED data adapters.
- Keeps the dashboard as a self-contained HTML file suitable for local viewing on desktop, tablet, or phone.
- The scheduled workflow no longer uploads report/dashboard artifacts or deploys a public site, because this repository is public.

## Important privacy boundary
This repository is public. Build 4.2 does not turn the repository private and does not create authenticated remote hosting. The workflow therefore does not publish generated reports as artifacts. To use the dashboard privately, generate it on a trusted machine and transfer the HTML securely. For remote access with authentication, first arrange a private repository or private hosting provider and configure access control there.

## Generate locally
```bash
python -m mdv14 --feeds examples/feeds.sample.json \
  --output build/latest-report.json \
  --dashboard build/monitoring-dashboard.html \
  --economic-countries ID,US,CN
```

Open `build/monitoring-dashboard.html` in a browser. The WIB clock continues to update while the page is open. The report contents remain a snapshot until a new report is generated.

## Data freshness
The scheduled collector runs every six hours. The dashboard distinguishes browser clock time from report generation time and source adapter status. It does not claim continuous collection, real-time quotes, or current BPS regional observations when no source data has been configured.