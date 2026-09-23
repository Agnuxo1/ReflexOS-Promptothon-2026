"""Gradio demo for Promptothon 2026."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import gradio as gr

from reflexos.benchmark import run_benchmark
from reflexos.models import Task
from reflexos.router import JEVSubprocessRouter, LocalSemanticRouter, SemanticRouter


def build_router() -> SemanticRouter:
    """Use an explicitly configured JEV connector, otherwise stay credential-free."""

    raw = os.environ.get("REFLEXOS_JEV_CONNECTOR_JSON", "").strip()
    if not raw:
        return LocalSemanticRouter()
    try:
        connector = json.loads(raw)
        if not isinstance(connector, list) or not all(isinstance(item, str) and item for item in connector):
            raise ValueError
        return JEVSubprocessRouter(connector, cwd=os.environ.get("REFLEXOS_JEV_CWD") or None)
    except (ValueError, TypeError, json.JSONDecodeError):
        return LocalSemanticRouter()


router = build_router()


def inspect_route(prompt: str, risk: str) -> tuple[str, str, str]:
    prompt = (prompt or "").strip()
    if not prompt:
        return "No prompt supplied.", "-", "-"
    task = Task(objective=prompt, checks=({"kind": "nonempty"},), risk=risk)
    try:
        decision = router.decide(task, "initial_route")
    except Exception:
        decision = LocalSemanticRouter().decide(task, "initial_route")
    policy = ["deterministic tools first", "Luna first for generative work"]
    if decision.collaboration != "single":
        policy.append(f"recommended review: {decision.collaboration}")
    policy.append("Sol/Astra only after failed acceptance gates")
    return " -> ".join(policy), f"{decision.uncertainty:.2f}", decision.source


def benchmark_markdown() -> str:
    data = run_benchmark()
    baseline = data["baseline_always_astra"]
    reflex = data["reflexos"]
    savings = data["savings"]
    return f"""
### Credential-free routing benchmark

| Metric | Always-Astra baseline | ReflexOS |
|---|---:|---:|
| Accepted tasks | {baseline['accepted']} | {reflex['accepted']} |
| Model calls | {baseline['model_calls']} | {reflex['model_calls']} |
| Observed tokens | {baseline['observed_tokens']} | {reflex['observed_tokens']} |
| Abstract cost units | {baseline['cost_units']:.0f} | {reflex['cost_units']:.0f} |

**Savings:** {savings['observed_tokens_pct']}% simulated tokens · {savings['cost_units_pct']}% abstract cost units.

> Transparent synthetic policy benchmark. It validates orchestration behavior, not frontier-model quality or real monetary cost.
"""


with gr.Blocks(title="ReflexOS — Promptothon 2026") as demo:
    gr.Markdown("# ReflexOS\n### Use the smallest intelligence necessary — and prove when escalation is justified.")
    with gr.Tab("Route Inspector"):
        prompt = gr.Textbox(label="Task", lines=5, placeholder="Describe a task for an AI agent...")
        risk = gr.Dropdown(["low", "moderate", "high", "critical"], value="moderate", label="Risk")
        run = gr.Button("Inspect policy", variant="primary")
        route = gr.Textbox(label="Policy plan")
        uncertainty = gr.Textbox(label="Semantic uncertainty")
        source = gr.Textbox(label="Routing source")
        run.click(inspect_route, [prompt, risk], [route, uncertainty, source])
    with gr.Tab("Benchmark"):
        bench = gr.Markdown()
        button = gr.Button("Run reproducible benchmark", variant="primary")
        button.click(benchmark_markdown, outputs=bench)
        demo.load(benchmark_markdown, outputs=bench)
    with gr.Tab("Architecture"):
        gr.Markdown(
            """
1. **Deterministic fast path** handles exact work without an LLM.  
2. **Reflex Fabric** decides whether a semantic checkpoint is worth paying for.  
3. **JEV** can recommend uncertainty and review shape when explicitly configured; a local fallback keeps the demo reproducible.  
4. **Luna-first** is an invariant for every generative task.  
5. **Acceptance gates** determine whether escalation to Sol or Astra is justified.  
6. **Integrity-checked cache and factual telemetry** make runs inspectable.
"""
        )


if __name__ == "__main__":
    demo.launch()
