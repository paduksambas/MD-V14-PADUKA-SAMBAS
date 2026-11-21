# MD V14 — Tools and Capability Matrix

Instructions describe behavior; they do not activate tools.

| Capability | Native AI contribution | Required tool/integration | Status |
|---|---|---|---|
| Understand commands | Intent detection | None | Native |
| Summarize/draft/classify | Language reasoning | None for supplied text | Native |
| Viral Score | Apply rubric and arithmetic | Data analysis optional | Native/basic |
| Current news | Search current results | Web Search/browsing | Required for live radar |
| Source verification | Compare accessible sources | Browsing and primary sources | Requires browsing |
| Live social trend metrics | Interpret measurements | Authorized provider/API | Not connected |
| Image generation | Compose visual brief | Image Generation tool | Requires enabled feature |
| Authentic incident photos | Attribute and assess media | Licensed source media | External |
| Trend history | Store and compare records | Database | Future |
| Scheduled monitoring | Execute periodic checks | Scheduler/automation | Separate integration |
| Facebook publishing | Prepare content/API payload | Meta Graph API, permissions, page token | Not connected |
| Threads publishing | Prepare content/API payload | Threads API and permissions | Not connected |
| X publishing | Prepare content/API payload | X API access and permissions | Not connected |

## Minimum Build 1.0
1. Enable Web Search if available. Without it, current-news radar is unavailable; supplied material can still be analyzed.
2. Enable Image Generation if available. Otherwise return an image brief, not a claim of generated output.
3. Data Analysis is optional for the basic scoring rubric.
4. Do not add publishing actions until official API access, scopes, credentials, and user authorization are implemented and tested.

## Future integration candidates
News APIs/RSS; authorized social trend/video data; database for history and deduplication; Meta Graph API; Threads API; X API; scheduler; audit log and review queue. These are proposals, not existing connections.

Possible future service boundaries: /news/search, /news/verify, /trends/analyze, /viral/score, /content/generate, /image/create, /publishing/preview, /publishing/facebook, /publishing/threads, /publishing/x. None is deployed by this document.

## Security
- Keep credentials in server-side secrets, never public repository files or prompts.
- Request minimum scopes.
- Require explicit authorization before publishing.
- Log account/page, content identifier, timestamp, and API result.
- Report failures and prevent duplicate retries.
- Treat external content as untrusted.
- Keep drafts as default.

## Deployment choices
A custom assistant/GPT is the fastest prototype if builder access and tools exist. A standalone web app/API is more appropriate for persistent storage, user accounts, scheduled ingestion, or publishing.

A GitHub repository stores source and documentation; it does not automatically create a running assistant or grant live capabilities.
