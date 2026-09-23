from pathlib import Path

import pytest

from reflexos.engine import Engine
from reflexos.memory import Store
from reflexos.models import Limits, ProviderResult, SemanticDecision, Task, Tier
from reflexos.providers import SimulatedProvider


class BrokenRouter:
    def decide(self, task, event, failed_checks=()):
        raise RuntimeError("router unavailable")


class CriticalRouter:
    def decide(self, task, event, failed_checks=()):
        return SemanticDecision(uncertainty=0.9, needs_human_checkpoint=True, source="test")


class RecordingProvider:
    def __init__(self, outputs):
        self.outputs = iter(outputs)
        self.tiers = []

    def run(self, task, tier, previous_output=""):
        self.tiers.append(tier)
        return ProviderResult(next(self.outputs), 10, 5, 1.0, f"test-{tier.value}")


def test_deterministic_cache_revalidates(tmp_path: Path):
    task = Task(
        task_id="stats",
        objective="Count words",
        operation="text_stats",
        input_data="one two three",
        checks=({"kind": "json_equals", "path": ["words"], "value": 3},),
    )
    engine = Engine(SimulatedProvider(), store=Store(tmp_path))
    first = engine.run(task)
    second = engine.run(task)
    assert first.status == second.status == "accepted"
    assert first.model_calls == second.model_calls == 0
    assert not first.cache_hit
    assert second.cache_hit


def test_luna_is_always_first_and_escalation_requires_failed_gate(tmp_path: Path):
    provider = RecordingProvider(["wrong", "PASS", "unused"])
    task = Task(objective="Return PASS", checks=({"kind": "contains", "value": "PASS"},))
    result = Engine(provider, store=Store(tmp_path)).run(task)
    assert result.status == "accepted"
    assert provider.tiers == [Tier.LUNA, Tier.SOL]
    assert result.path == ("luna", "sol")
    assert any(event["event"] == "pre_escalation_checkpoint" for event in result.events)


def test_astra_is_only_reached_after_luna_and_sol_fail(tmp_path: Path):
    provider = RecordingProvider(["wrong-luna", "wrong-sol", "PASS"])
    task = Task(objective="Return PASS", checks=({"kind": "contains", "value": "PASS"},))
    result = Engine(provider, store=Store(tmp_path)).run(task)
    assert result.status == "accepted"
    assert provider.tiers == [Tier.LUNA, Tier.SOL, Tier.ASTRA]


def test_semantic_router_failure_uses_safe_local_fallback(tmp_path: Path):
    provider = RecordingProvider(["PASS"])
    task = Task(objective="Return PASS", checks=({"kind": "contains", "value": "PASS"},))
    result = Engine(provider, semantic_router=BrokenRouter(), store=Store(tmp_path)).run(task)
    assert result.status == "accepted"
    assert result.path == ("luna",)
    assert any(event["event"] == "semantic_router_failed" for event in result.events)


def test_critical_human_checkpoint_fails_closed_before_model_call(tmp_path: Path):
    provider = RecordingProvider(["PASS"])
    task = Task(objective="Irreversible operation", checks=({"kind": "nonempty"},), risk="critical")
    result = Engine(provider, semantic_router=CriticalRouter(), store=Store(tmp_path)).run(task)
    assert result.status == "needs_human"
    assert provider.tiers == []


def test_model_call_budget_is_hard_limit(tmp_path: Path):
    provider = RecordingProvider(["wrong"])
    task = Task(objective="Return PASS", checks=({"kind": "contains", "value": "PASS"},))
    result = Engine(provider, store=Store(tmp_path), limits=Limits(max_model_calls=1)).run(task)
    assert result.status == "budget_exhausted"
    assert provider.tiers == [Tier.LUNA]
