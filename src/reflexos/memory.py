"""Integrity-checked cache and factual run telemetry."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
import time
from pathlib import Path
from typing import Any


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=".reflexos-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(canonical(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Store:
    """Local state that stores only verified deterministic cache entries."""

    def __init__(self, root: str | Path = ".reflexos") -> None:
        self.root = Path(root)

    def get(self, key: str, ttl_seconds: float = 86_400.0) -> str | None:
        path = self.root / "cache" / f"{key}.json"
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            if record.get("key") != key or time.time() - float(record["created"]) > ttl_seconds:
                return None
            text = record["text"]
            if not isinstance(text, str) or fingerprint(text) != record.get("digest"):
                return None
            return text
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            return None

    def put_verified(self, key: str, text: str) -> None:
        _atomic_json(
            self.root / "cache" / f"{key}.json",
            {"key": key, "text": text, "digest": fingerprint(text), "created": time.time()},
        )

    def checkpoint(self, run_id: str, payload: dict[str, Any]) -> None:
        _atomic_json(self.root / "runs" / f"{run_id}.json", payload)
