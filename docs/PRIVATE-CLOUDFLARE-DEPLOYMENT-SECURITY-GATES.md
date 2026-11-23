# Private deployment security gate addendum

This addendum supersedes the older run instructions in the private deployment checklist for the updated workflow.

## Preflight

Run **PADUKA private dashboard deploy (manual)** with both inputs left false:

- `deploy_now = false`
- `alternate_hostnames_confirmed = false`

This mode builds the single-file dashboard and checks the configured custom-domain Cloudflare Access application and its policies. It does not publish anything.

## Publishing gate

Before publishing, manually inspect the Cloudflare Pages project settings. Confirm that the default `pages.dev` hostname and every preview deployment URL are disabled or separately protected by an owner-only Cloudflare Access policy.

Only if that inspection is complete, run the workflow with both inputs true:

- `deploy_now = true`
- `alternate_hostnames_confirmed = true`

The second input is a human attestation, not an API-backed check. If the alternate hostnames cannot be verified, do not publish.

The workflow continues to upload only `build/index.html`. It does not deploy automatically from pushes or pull requests.
