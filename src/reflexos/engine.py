"""ReflexOS execution engine: deterministic first, Luna first, evidence-gated escalation."""
from __future__ import annotations

import time
import uuid
from typing import Any

from .checks import all_passed, verify
from .memory import Store, fingerprint
from .models import Limits, RunResult, SemanticDecision, Task, Tier
from .providers import Provider
from .reflex import ReflexFabric, ReflexSignal
from .router import LocalSemanticRouter, SemanticRouter
from .skills import execute, is_deterministic


class Engine:
    """Bounded cognitive orchestrator with explicit, inspectable control flow."""

    def __init__(
        self,
        provider: Provider,
        *,
        semantic_router: SemanticRouter | None = None,
        store: Store | None = None,
        limits: Limits | None = None,
    ) -> None:
        self.provider = provider
        self.router = semantic_router or LocalSemanticRouter()
        self.store = store or Store()
        self.limits = limits or Limits()
        self.reflex = ReflexFabric(self.limits)

    def run(self, task: Task) -> RunResult:
        started = time.monotonic()
        run_id = uuid.uuid4().hex
        events: list[dict[str, Any]] = [{"event": "task_validated", "task_id": task.task_id}]
        path: list[str] = []
        calls = 0
        tokens = 0
        cost_units = 0.0
        checkpoints = 0
        output = ""
        check_results: tuple[dict[str, Any], ...] = ()

        def elapsed() -> float:
            return time.monotonic() - started

        def finish(status: str, *, cache_hit: bool = False) -> RunResult:
            payload = {
                "run_id": run_id,
                "task_id": task.task_id,
                "status": status,
                "path": path,
                "model_calls": calls,
                "observed_tokens": tokens,
                "cost_units": round(cost_units, 4),
                "events": events,
            }
            self.store.checkpoint(run_id, payload)
            return RunResult(
                status=status,
                output=output,
                path=tuple(path),
                checks=check_results,
                model_calls=calls,
                observed_tokens=tokens,
                cost_units=round(cost_units, 4),
                elapsed_seconds=round(elapsed(), 6),
                events=tuple(events),
                cache_hit=cache_hit,
            )

        if is_deterministic(task.operation):
            cache_key = fingerprint({"operation": task.operation, "input": task.input_data, "checks": task.checks})
            cached = self.store.get(cache_key)
            if cached is not None:
                output = cached
                check_results = verify(output, task.checks)
                if all_passed(check_results):
                    path.append(Tier.DETERMINISTIC.value)
                    events.append({"event": "cache_revalidated"})
                    return finish("accepted", cache_hit=True)
            output = execute(task.operation, task.input_data)
            check_results = verify(output, task.checks)
            path.append(Tier.DETERMINISTIC.value)
            events.append({"event": "deterministic_skill_executed", "operation": task.operation})
            if all_passed(check_results):
                self.store.put_verified(cache_key, output)
                return finish("accepted")
            return finish("needs_review")

        initial_gate = self.reflex.decide(
            ReflexSignal(event="initial_route", risk=task.risk, tokens_used=tokens, checkpoints_used=checkpoints)
        )
        decision = SemanticDecision()
        if initial_gate.call_semantic_router:
            try:
                decision = self.router.decide(task, "initial_route")
                checkpoints += 1
                tokens += decision.usage_tokens
                events.append({
                    "event": "semantic_route",
                    "source": decision.source,
                    "collaboration": decision.collaboration,
                    "uncertainty": round(decision.uncertainty, 4),
                })
            except Exception:
                events.append({"event": "semantic_router_failed", "fallback": "local"})
                decision = LocalSemanticRouter().decide(task, "initial_route")

        if decision.needs_human_checkpoint and task.risk == "critical":
            events.append({"event": "human_checkpoint_required"})
            return finish("needs_human")

        tiers = (Tier.LUNA, Tier.SOL, Tier.ASTRA)
        previous = ""
        for index, tier in enumerate(tiers):
            if calls >= self.limits.max_model_calls or elapsed() >= self.limits.max_seconds:
                events.append({"event": "budget_exhausted"})
                return finish("budget_exhausted")
            if tokens >= self.limits.max_observed_tokens:
                events.append({"event": "token_budget_exhausted"})
                return finish("budget_exhausted")

            if index > 0:
                failed = tuple(item for item in check_results if not item.get("passed"))
                gate = self.reflex.decide(
                    ReflexSignal(
                        event="pre_escalation",
                        uncertainty=decision.uncertainty,
                        risk=task.risk,
                        failure_observed=True,
                        tokens_used=tokens,
                        checkpoints_used=checkpoints,
                    )
                )
                if not gate.allow_escalation:
                    events.append({"event": "escalation_denied", "reason": gate.reason})
                    return finish("needs_review")
                if gate.call_semantic_router and checkpoints < self.limits.max_checkpoints:
                    try:
                        decision = self.router.decide(task, "pre_escalation", failed)
                        checkpoints += 1
                        tokens += decision.usage_tokens
                        events.append({"event": "pre_escalation_checkpoint", "source": decision.source})
                    except Exception:
                        events.append({"event": "pre_escalation_router_failed"})

            result = self.provider.run(task, tier, previous)
            calls += 1
            path.append(tier.value)
            if result.input_tokens is not None and result.output_tokens is not None:
                tokens += result.input_tokens + result.output_tokens
            cost_units += float(result.cost_units)
            output = result.text
            check_results = verify(output, task.checks)
            events.append(
                {
                    "event": "model_attempt",
                    "tier": tier.value,
                    "model": result.model,
                    "accepted": all_passed(check_results),
                }
            )
            if all_passed(check_results):
                return finish("accepted")
            previous = output

        return finish("needs_review")
