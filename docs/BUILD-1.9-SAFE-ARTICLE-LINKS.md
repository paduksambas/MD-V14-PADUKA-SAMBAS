# Build 1.9 — Safe RSS/Atom Article Links

## Delivered
- RSS and Atom parsing now accepts article links only when they use HTTP or HTTPS, include a hostname, and contain no embedded username or password.
- Entries with unsafe or malformed links (including javascript:, file:, hostless URLs, and credential-bearing URLs) are skipped instead of entering the intelligence pipeline.
- Ordinary HTTP and HTTPS article links remain supported for compatibility with publishers that use HTTP URLs.
- Added offline unit coverage for unsafe schemes, missing hosts, embedded credentials, and valid HTTP/HTTPS links.

## Security boundary
This check validates link structure; it does not fetch article URLs, prove publisher identity, or establish factual accuracy. Feed fetching continues to require HTTPS and retains its existing public-host, no-redirect, timeout, and response-size controls.

## Validation
Run the full suite with:

```bash
python -m unittest discover -s tests -v
```
