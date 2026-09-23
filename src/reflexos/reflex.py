"""Deterministic reflex fabric controlling expensive semantic checkpoints."""
from __future__ import annotations

from dataclasses import dataclass

from .models import Limits


@dataclass(frozen=True)
class ReflexSignal:
    event: str
    uncertainty: float = 0.0
    risk: str = "moderate"
    semantic_ambiguity: bool = False
    failure_observed: bool = False
    conflicting_evidence: bool = False
    irreversible: bool = False
    tokens_used: int = 0
    checkpoints_used: int = 0


@dataclass(frozen=True)
class ReflexDecision:
    call_semantic_router: bool
    allow_parallel_review: bool
    allow_escalation: bool
    reason: str


class ReflexFabric:
    """Cheap local gate around expensive semantic routing and review."""

    ALWAYS_CHECK = frozenset({"initial_route", "pre_escalation", "pre_finish"})
    EVENT_CHECK = frozenset({"tool_failure", "agent_failure", "conflicting_evidence", "acceptance_uncertain"})

    def __init__(self, limits: Limits) -> None:
        self.limits = limits

    def decide(self, signal: ReflexSignal) -> ReflexDecision:
        if signal.checkpoints_used >= self.limits.max_checkpoints:
            return ReflexDecision(False, False, False, "checkpoint_budget_exhausted")
        if signal.tokens_used >= self.limits.max_observed_tokens:
            return ReflexDecision(False, False, False, "token_budget_exhausted")

        high_risk = signal.risk in {"high", "critical"}
        trigger = (
            signal.event in self.ALWAYS_CHECK
            or signal.event in self.EVENT_CHECK
            or signal.semantic_ambiguity
            or signal.failure_observed
            or signal.conflicting_evidence
            or signal.irreversible
            or signal.uncertainty >= self.limits.thinktank_threshold
            or high_risk
        )
        if not trigger:
            return ReflexDecision(False, False, False, "deterministic_fast_path")

        parallel = signal.conflicting_evidence or signal.uncertainty >= self.limits.thinktank_threshold
        escalation = signal.failure_observed or signal.uncertainty >= self.limits.escalation_threshold
        return ReflexDecision(True, parallel, escalation, "semantic_checkpoint_justified")
