"""Typed public contracts for ReflexOS."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Tier(str, Enum):
    """Execution tiers enforced by the Luna-first policy."""

    DETERMINISTIC = "deterministic"
    LUNA = "luna"
    SOL = "sol"
    ASTRA = "astra"


@dataclass(frozen=True)
class Limits:
    """Hard local budgets. Provider advice cannot override these limits."""

    max_model_calls: int = 4
    max_seconds: float = 120.0
    max_observed_tokens: int = 30_000
    max_checkpoints: int = 4
    escalation_threshold: float = 0.55
    thinktank_threshold: float = 0.70

    def __post_init__(self) -> None:
        if self.max_model_calls < 1:
            raise ValueError("max_model_calls must be positive")
        if self.max_seconds <= 0:
            raise ValueError("max_seconds must be positive")
        if self.max_observed_tokens < 1:
            raise ValueError("max_observed_tokens must be positive")
        if self.max_checkpoints < 0:
            raise ValueError("max_checkpoints cannot be negative")
        for value in (self.escalation_threshold, self.thinktank_threshold):
            if not 0.0 <= value <= 1.0:
                raise ValueError("thresholds must be between 0 and 1")


@dataclass(frozen=True)
class Task:
    """A bounded task with explicit acceptance criteria."""

    objective: str
    checks: tuple[dict[str, Any], ...]
    context: str = ""
    operation: str = "model"
    input_data: Any = None
    risk: str = "moderate"
    task_id: str = "task"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not isinstance(self.objective, str) or not self.objective.strip():
            raise ValueError("objective must be non-empty text")
        if not self.checks:
            raise ValueError("at least one acceptance check is required")
        if self.risk not in {"low", "moderate", "high", "critical"}:
            raise ValueError("risk must be low, moderate, high, or critical")


@dataclass(frozen=True)
class ProviderResult:
    """Normalized model response and observable usage."""

    text: str
    input_tokens: int | None = None
    output_tokens: int | None = None
    cost_units: float = 0.0
    model: str = ""


@dataclass(frozen=True)
class SemanticDecision:
    """Optional semantic-routing advice. It never changes the first model tier."""

    collaboration: str = "single"
    uncertainty: float = 0.0
    needs_human_checkpoint: bool = False
    source: str = "local"
    usage_tokens: int = 0


@dataclass(frozen=True)
class RunResult:
    """Stable result returned by the engine."""

    status: str
    output: str
    path: tuple[str, ...]
    checks: tuple[dict[str, Any], ...]
    model_calls: int
    observed_tokens: int
    cost_units: float
    elapsed_seconds: float
    events: tuple[dict[str, Any], ...]
    cache_hit: bool = False
