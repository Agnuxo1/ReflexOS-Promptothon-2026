"""Deterministic acceptance gates."""
from __future__ import annotations

import json
from typing import Any, Iterable


def _canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def verify(text: str, checks: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Evaluate explicit checks without delegating correctness to a model."""

    results: list[dict[str, Any]] = []
    for index, check in enumerate(checks):
        kind = check.get("kind")
        passed = False
        try:
            if kind == "nonempty":
                passed = bool(text.strip())
            elif kind == "contains":
                value = check.get("value")
                passed = isinstance(value, str) and bool(value) and value in text
            elif kind == "excludes":
                value = check.get("value")
                passed = isinstance(value, str) and bool(value) and value not in text
            elif kind == "json_equals":
                value: Any = json.loads(text)
                path = check.get("path", [])
                if not isinstance(path, list):
                    raise TypeError("path must be a list")
                for key in path:
                    if isinstance(key, bool) or not isinstance(key, (str, int)):
                        raise TypeError("unsafe path component")
                    value = value[key]
                passed = _canonical(value) == _canonical(check.get("value"))
            elif kind == "numeric_range":
                value = float(text.strip())
                lower = float(check.get("min", "-inf"))
                upper = float(check.get("max", "inf"))
                passed = lower <= value <= upper
            else:
                raise ValueError("unknown check")
        except (ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError):
            passed = False
        results.append({"index": index, "kind": kind, "passed": passed})
    return tuple(results)


def all_passed(results: Iterable[dict[str, Any]]) -> bool:
    """Return True only when every acceptance check passed."""

    results = tuple(results)
    return bool(results) and all(bool(item.get("passed")) for item in results)
