# Build 4.4 — Private Local Storage Foundation

## Purpose
Separate local/private intelligence outputs from the public source repository. This is a local storage foundation, not private cloud hosting or an authenticated remote dashboard deployment.

## Added
- `mdv14/private_data.py`: `ensure_private_dir()` creates a local private folder and attempts owner-only permissions (0700).
- `save_private_json()` saves JSON atomically through the existing storage helper, restricts filenames to simple names, and attempts owner-only file permissions (0600).
- `.gitignore` ignores local private folders, SQLite history files, and environment files.
- Unit tests cover writing, filename traversal rejection, and symlink directory rejection.

## Usage
```python
from mdv14.private_data import save_private_json
save_private_json("snapshot.json", report, directory="data/private")
```
Or use the CLI's existing `--output` and `--database` paths with local paths under `data/private/` (ensure the private directory exists and is not synced/shared). Keep generated reports, SQLite history, API keys, and credentials off the public repo.

## Limits / next steps
- The dashboard remains a local HTML file; no remote login or private hosting is configured in this build.
- Git ignore is a safety guard, not encryption or a guarantee against accidental commits. Verify `git status` before publishing.
- GitHub Actions runs are ephemeral and should not be used as private durable storage.
