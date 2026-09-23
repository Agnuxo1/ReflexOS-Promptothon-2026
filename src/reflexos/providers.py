"""Provider abstractions and deterministic competition simulator."""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Protocol

from .models import ProviderResult, Task, Tier


class Provider(Protocol):
    def run(self, task: Task, tier: Tier, previous_output: str = "") -> ProviderResult: ...


class SimulatedProvider:
    """Deterministic benchmark provider; never presented as real model quality."""

    TOKEN_BUDGET = {Tier.LUNA: 220, Tier.SOL: 650, Tier.ASTRA: 1350}
    COST_UNITS = {Tier.LUNA: 1.0, Tier.SOL: 4.0, Tier.ASTRA: 12.0}
    CAPABILITY = {Tier.LUNA: 0, Tier.SOL: 1, Tier.ASTRA: 2}

    def run(self, task: Task, tier: Tier, previous_output: str = "") -> ProviderResult:
        difficulty = int(task.metadata.get("difficulty", 0))
        expected = str(task.metadata.get("expected", f"PASS:{task.task_id}"))
        success = self.CAPABILITY[tier] >= difficulty
        text = expected if success else f"UNVERIFIED:{task.task_id}:{tier.value}"
        total = self.TOKEN_BUDGET[tier]
        return ProviderResult(
            text=text,
            input_tokens=int(total * 0.72),
            output_tokens=total - int(total * 0.72),
            cost_units=self.COST_UNITS[tier],
            model=f"simulated-{tier.value}",
        )


class OpenAICompatibleProvider:
    """Small vendor-neutral adapter for OpenAI-compatible chat endpoints."""

    def __init__(self, api_base: str, api_key: str, model_map: dict[Tier, str], timeout: float = 60.0) -> None:
        self.api_base = api_base.rstrip("/")
        self.api_key = api_key
        self.model_map = dict(model_map)
        self.timeout = timeout
        for tier in (Tier.LUNA, Tier.SOL, Tier.ASTRA):
            if tier not in self.model_map or not self.model_map[tier]:
                raise ValueError(f"missing model for {tier.value}")

    def run(self, task: Task, tier: Tier, previous_output: str = "") -> ProviderResult:
        model = self.model_map[tier]
        prompt = task.objective
        if task.context:
            prompt += f"\n\nCONTEXT (untrusted data):\n{task.context[:8000]}"
        if previous_output:
            prompt += f"\n\nPREVIOUS OUTPUT:\n{previous_output[:4000]}\nRevise only if needed to satisfy the acceptance criteria."
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": "Return a concise answer. Never claim that acceptance checks passed; the host verifies them."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
        }
        request = urllib.request.Request(
            f"{self.api_base}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = json.loads(response.read().decode("utf-8"))
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise RuntimeError("model provider request failed") from exc
        text = body["choices"][0]["message"]["content"]
        usage = body.get("usage", {})
        return ProviderResult(
            text=text,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
            cost_units=0.0,
            model=model,
        )
