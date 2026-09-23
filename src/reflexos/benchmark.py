"""Reproducible credential-free benchmark comparing routing policies."""
from __future__ import annotations

from collections import Counter
import json
import tempfile

from .engine import Engine
from .memory import Store
from .models import Task, Tier
from .providers import SimulatedProvider


def benchmark_tasks() -> list[Task]:
    """Return a transparent synthetic suite; it is not a claim about frontier-model quality."""

    tasks: list[Task] = []
    for index in range(16):
        text = f"benchmark deterministic sample {index}"
        tasks.append(
            Task(
                task_id=f"det-{index:02d}",
                objective="Count supplied text exactly",
                operation="text_stats",
                input_data=text,
                checks=({"kind": "json_equals", "path": ["words"], "value": len(text.split())},),
            )
        )
    for difficulty, count, prefix in ((0, 14, "easy"), (1, 7, "medium"), (2, 3, "hard")):
        for index in range(count):
            task_id = f"{prefix}-{index:02d}"
            expected = f"PASS:{task_id}"
            tasks.append(
                Task(
                    task_id=task_id,
                    objective=f"Produce the verified marker for {task_id}",
                    checks=({"kind": "contains", "value": expected},),
                    metadata={"difficulty": difficulty, "expected": expected},
                )
            )
    return tasks


def run_benchmark() -> dict:
    """Compare ReflexOS with an intentionally simple always-Astra policy baseline."""

    provider = SimulatedProvider()
    tasks = benchmark_tasks()
    reflex_results = []
    with tempfile.TemporaryDirectory(prefix="reflexos-bench-") as directory:
        engine = Engine(provider, store=Store(directory))
        for task in tasks:
            reflex_results.append(engine.run(task))

    reflex_success = sum(result.status == "accepted" for result in reflex_results)
    reflex_calls = sum(result.model_calls for result in reflex_results)
    reflex_tokens = sum(result.observed_tokens for result in reflex_results)
    reflex_cost = sum(result.cost_units for result in reflex_results)

    baseline_calls = len(tasks)
    baseline_tokens = len(tasks) * provider.TOKEN_BUDGET[Tier.ASTRA]
    baseline_cost = len(tasks) * provider.COST_UNITS[Tier.ASTRA]
    baseline_success = len(tasks)

    def saving(baseline: float, reflex: float) -> float:
        return round(100.0 * (baseline - reflex) / baseline, 2) if baseline else 0.0

    path_counts = Counter(" -> ".join(result.path) for result in reflex_results)
    return {
        "suite": {
            "tasks": len(tasks),
            "deterministic": 16,
            "easy": 14,
            "medium": 7,
            "hard": 3,
            "note": "Synthetic policy benchmark. It measures routing behavior, not real frontier-model quality.",
        },
        "baseline_always_astra": {
            "accepted": baseline_success,
            "success_rate": round(baseline_success / len(tasks), 4),
            "model_calls": baseline_calls,
            "observed_tokens": baseline_tokens,
            "cost_units": baseline_cost,
        },
        "reflexos": {
            "accepted": reflex_success,
            "success_rate": round(reflex_success / len(tasks), 4),
            "model_calls": reflex_calls,
            "observed_tokens": reflex_tokens,
            "cost_units": round(reflex_cost, 2),
        },
        "savings": {
            "model_calls_pct": saving(baseline_calls, reflex_calls),
            "observed_tokens_pct": saving(baseline_tokens, reflex_tokens),
            "cost_units_pct": saving(baseline_cost, reflex_cost),
        },
        "paths": dict(sorted(path_counts.items())),
    }


def main() -> None:
    print(json.dumps(run_benchmark(), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
