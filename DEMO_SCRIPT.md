# ReflexOS — 3-Minute Demo Script

## 0:00–0:20 — Problem

"Most AI-agent stacks make one of two mistakes: they send everything to the largest model, wasting cost and latency, or they force everything through a cheap model and lose quality. ReflexOS makes model escalation explicit, testable and evidence-driven."

Show the title: **Use the smallest intelligence necessary — and prove when escalation is justified.**

## 0:20–0:45 — Architecture

Show the Architecture tab.

"Exact work goes to deterministic tools. For generative work, a Reflex Fabric decides whether a semantic checkpoint is useful. JEV can advise uncertainty and collaboration, but local code owns budgets and safety. Luna is always first. Sol or Astra are unlocked only after an acceptance gate actually fails."

## 0:45–1:20 — Route Inspector

Enter an ordinary task with moderate risk.

"This stays on a single-worker recommendation. Now I add conflicting evidence and high risk. The semantic advisor raises uncertainty and recommends independent review. The important point is that this advice still cannot skip Luna or bypass hard checks."

## 1:20–2:05 — Executable escalation proof

Run in a terminal or notebook:

```bash
reflexos simulate --difficulty 0
reflexos simulate --difficulty 1
reflexos simulate --difficulty 2
```

Narrate the paths:

- difficulty 0 -> `luna`
- difficulty 1 -> `luna -> sol`
- difficulty 2 -> `luna -> sol -> astra`

"The stronger tier is not selected because a prompt said so. It is reached because the previous tier produced an output that failed the host acceptance gate."

## 2:05–2:35 — Benchmark

Click **Run reproducible benchmark**.

"This is a transparent synthetic routing benchmark, not a frontier-model benchmark. Both policies accept all 40 simulator tasks. The always-Astra baseline consumes 54,000 simulated tokens and 480 abstract cost units. ReflexOS consumes 15,830 tokens and 100 units: 70.69% fewer simulated tokens and 79.17% fewer cost units."

Keep the disclaimer visible.

## 2:35–2:55 — Reliability

Show tests/CI.

"The prototype passes 20 automated tests: safe tools, cache integrity, Luna-first ordering, escalation gates, router-outage fallback, critical-risk human checkpoints and benchmark invariants. Core routing needs no GPU or TPU."

## 2:55–3:00 — Close

"ReflexOS does not ask which model is smartest. It asks: what is the smallest amount of intelligence we can justify for this task — and what evidence proves that we need more?"
