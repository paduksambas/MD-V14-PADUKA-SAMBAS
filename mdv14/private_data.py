"""Private local data helpers for MD V14.

These helpers deliberately keep sensitive outputs on the operator's local machine.
They do not upload, publish, or sync data to GitHub.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .storage import save_json_atomic


DEFAULT_PRIVATE_DIR = Path("data/private")


def ensure_private_dir(path: str | Path = DEFAULT_PRIVATE_DIR) -> Path:
    """Create a local private directory and apply owner-only permissions where supported."""
    directory = Path(path).expanduser()
    directory.mkdir(parents=True, exist_ok=True)
    if directory.is_symlink():
        raise ValueError("private data directory must not be a symlink")
    try:
        directory.chmod(0o700)
    except OSError:
        # Permission modes may not be supported on every platform.
        pass
    return directory


def save_private_json(filename: str, payload: Any, directory: str | Path = DEFAULT_PRIVATE_DIR) -> Path:
    """Save JSON into the private directory; accept only a simple filename."""
    if not filename or filename in {".", ".."} or Path(filename).name != filename:
        raise ValueError("filename must be a simple name without path components")
    private_dir = ensure_private_dir(directory)
    destination = private_dir / filename
    save_json_atomic(destination, payload)
    try:
        destination.chmod(0o600)
    except OSError:
        pass
    return destination
