"""Small command-line surface for reproducible ReflexOS demonstrations."""
from __future__ import annotations

import argparse
import json

from .benchmark import run_benchmark
from .engine import Engine
from .models import Task
from .providers import SimulatedProvider


def _simulate(difficulty: int) -> dict:
    task_id = f"demo-d{difficulty}"
    task = Task(
        task_id=task_id,
        objective=f"Produce the verified marker for difficulty {difficulty}",
        checks=({"kind": "contains", "value": f"PASS:{task_id}"},),
        metadata={"difficulty": difficulty, "expected": f"PASS:{task_id}"},
    )
    result = Engine(SimulatedProvider()).run(task)
    return {
        "status": result.status,
        "path": list(result.path),
        "checks": list(result.checks),
        "model_calls": result.model_calls,
        "observed_tokens": result.observed_tokens,
        "cost_units": result.cost_units,
        "events": list(result.events),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ReflexOS Promptothon demonstration CLI")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("benchmark", help="Run the credential-free routing benchmark")
    simulate = commands.add_parser("simulate", help="Show a Luna-first escalation path")
    simulate.add_argument("--difficulty", type=int, choices=(0, 1, 2), default=1)
    args = parser.parse_args(argv)
    payload = run_benchmark() if args.command == "benchmark" else _simulate(args.difficulty)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
