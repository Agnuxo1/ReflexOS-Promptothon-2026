"""Semantic routing adapters. Luna-first remains an engine invariant."""
from __future__ import annotations

import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Protocol

from .models import SemanticDecision, Task


class SemanticRouter(Protocol):
    def decide(self, task: Task, event: str, failed_checks: tuple[dict, ...] = ()) -> SemanticDecision: ...


class LocalSemanticRouter:
    """Credential-free conservative fallback for reproducible demos."""

    def decide(self, task: Task, event: str, failed_checks: tuple[dict, ...] = ()) -> SemanticDecision:
        text = f"{task.objective} {task.context}".lower()
        conflict = any(token in text for token in ("conflict", "contradiction", "disagree", "uncertain"))
        complex_terms = sum(token in text for token in ("architecture", "research", "scientific", "security", "legal", "optimize"))
        uncertainty = min(1.0, 0.18 + 0.17 * complex_terms + (0.25 if conflict else 0.0) + (0.20 if failed_checks else 0.0))
        collaboration = "second_opinion" if conflict or uncertainty >= 0.70 else "single"
        if task.risk in {"high", "critical"} and uncertainty >= 0.70:
            collaboration = "thinktank"
        return SemanticDecision(
            collaboration=collaboration,
            uncertainty=uncertainty,
            needs_human_checkpoint=task.risk == "critical",
            source="local_fallback",
            usage_tokens=0,
        )


class JEVSubprocessRouter:
    """Portable adapter to an existing JEV installation without embedding secrets."""

    def __init__(self, connector: list[str], cwd: str | None = None, timeout: float = 45.0) -> None:
        if not connector or not all(isinstance(value, str) and value for value in connector):
            raise ValueError("connector must be a non-empty argument list")
        if timeout <= 0 or not math.isfinite(timeout):
            raise ValueError("timeout must be positive and finite")
        self.connector = list(connector)
        self.cwd = str(Path(cwd).resolve()) if cwd else None
        self.timeout = timeout

    def decide(self, task: Task, event: str, failed_checks: tuple[dict, ...] = ()) -> SemanticDecision:
        state = {
            "objective": task.objective,
            "context": task.context[:5000],
            "risk": task.risk,
            "event": event,
            "failed_checks": list(failed_checks),
            "policy": "Luna is always the first generative tier. JEV can advise collaboration and uncertainty only.",
        }
        questions = {
            "collaboration": {
                "type": "choice",
                "instructions": "Choose the smallest useful review shape. Do not choose a model tier.",
                "criteria": {
                    "single": "One worker is enough",
                    "second_opinion": "One independent review is justified",
                    "thinktank": "Two independent views plus critic are justified",
                },
            },
            "uncertainty": {"type": "noul", "instructions": "How uncertain or semantically ambiguous is this decision?"},
            "human_checkpoint": {"type": "noul", "instructions": "Should a human checkpoint be required before an irreversible action?"},
        }
        with tempfile.TemporaryDirectory(prefix="reflexos-jev-") as directory:
            state_path = Path(directory) / "state.json"
            questions_path = Path(directory) / "questions.json"
            state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
            questions_path.write_text(json.dumps(questions, ensure_ascii=False), encoding="utf-8")
            command = [*self.connector, "query", "--state-file", str(state_path), "--questions-file", str(questions_path)]
            completed = subprocess.run(
                command,
                cwd=self.cwd or directory,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="strict",
                timeout=self.timeout,
                check=False,
            )
        if completed.returncode != 0:
            raise RuntimeError("JEV routing failed")
        payload = json.loads(completed.stdout)
        if payload.get("status") != "connected":
            raise RuntimeError("JEV routing was not connected")
        answers = payload["answers"]
        collaboration = answers["collaboration"]["value"]
        if collaboration not in {"single", "second_opinion", "thinktank"}:
            raise RuntimeError("JEV returned an invalid collaboration mode")
        uncertainty = float(answers["uncertainty"]["value"])
        human = float(answers["human_checkpoint"]["value"]) >= 0.5
        usage = payload.get("usage", {})
        usage_tokens = int(usage.get("input_tokens", 0) or 0) + int(usage.get("output_tokens", 0) or 0)
        return SemanticDecision(collaboration, uncertainty, human, "typesafe_jev", usage_tokens)
