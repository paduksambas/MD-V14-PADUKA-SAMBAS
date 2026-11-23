# Security Policy

## Scope

MD V14 is published as a public, static dashboard. Treat all repository contents, generated Pages output, workflow logs, and issue or pull-request discussions as public.

## Reporting a vulnerability

Please do not publish credentials, API keys, personal information, or exploit details in a public issue. Contact the repository owner privately through GitHub's private vulnerability reporting feature when it is enabled, or use GitHub's private contact options. Include the affected component, impact, and reproducible steps without including live secrets.

## Operational safeguards

- Store API keys and deployment credentials only in GitHub Actions secrets.
- Treat repository users with write, maintain, or admin access as trusted with Actions secrets; do not grant write access to untrusted contributors.
- The private Cloudflare deployment workflow defaults to preflight-only; an actual deployment requires an explicit manual `deploy_now=true` confirmation after the live Access policy check.
- Pin third-party deployment Actions to immutable commit SHAs and review dependency updates before merging.
- Never commit `.env` files, databases, raw monitoring reports, or private dashboards.
- Keep the public Pages artifact limited to the generated static HTML dashboard.
- Do not publish private monitoring outputs, raw provider responses, or SQLite history as workflow artifacts or caches.
- Review third-party Actions and dependency update pull requests before merging.
- Rotate any credential that may have been exposed; deleting it from a commit is not sufficient.

## Public-data notice

The public dashboard is a snapshot for informational purposes. Do not include confidential, personal, or access-controlled data in its source feeds or report inputs.
