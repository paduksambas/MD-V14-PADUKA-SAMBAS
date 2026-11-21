"""JSON persistence helpers for trend signals and generated reports."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable


def load_signals(path: str | Path) -> list[dict[str, Any]]:
    """Load a JSON array of signals; reject malformed or unexpected structures."""
    source = Path(path)
    with source.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("signal file must contain a JSON array")
    if any(not isinstance(item, dict) for item in payload):
        raise ValueError("each signal must be a JSON object")
    return payload


def save_json_atomic(path: str | Path, payload: Any) -> None:
    """Write JSON atomically to avoid leaving a partially-written report."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_name = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", dir=destination.parent,
            delete=False, prefix=f".{destination.name}.",
        ) as handle:
            temp_name = handle.name
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, destination)
    finally:
        if temp_name and os.path.exists(temp_name):
            os.unlink(temp_name)


def save_signals(path: str | Path, signals: Iterable[dict[str, Any]]) -> None:
    save_json_atomic(path, list(signals))
