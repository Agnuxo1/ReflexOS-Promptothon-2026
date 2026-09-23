from reflexos.models import Limits
from reflexos.reflex import ReflexFabric, ReflexSignal


def test_reflex_fast_path_avoids_unneeded_semantic_call():
    fabric = ReflexFabric(Limits())
    decision = fabric.decide(ReflexSignal(event="routine_step", risk="low"))
    assert not decision.call_semantic_router
    assert decision.reason == "deterministic_fast_path"


def test_failure_allows_evidence_gated_escalation():
    fabric = ReflexFabric(Limits())
    decision = fabric.decide(ReflexSignal(event="pre_escalation", failure_observed=True))
    assert decision.call_semantic_router
    assert decision.allow_escalation


def test_budgets_fail_closed():
    limits = Limits(max_checkpoints=1, max_observed_tokens=100)
    fabric = ReflexFabric(limits)
    assert not fabric.decide(ReflexSignal(event="pre_escalation", checkpoints_used=1)).allow_escalation
    assert not fabric.decide(ReflexSignal(event="pre_escalation", tokens_used=100)).allow_escalation
