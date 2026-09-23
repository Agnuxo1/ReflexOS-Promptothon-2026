# ReflexOS — Proof-Carrying Adaptive Cognitive Routing

## Track

LLMs & Automation

## Problem Statement

AI agents increasingly default to the most capable available language model even when a task is exact, routine, or already verifiable by code. That creates unnecessary latency and inference cost, while making it difficult to explain why an expensive model was selected. Cheap-model-only pipelines have the opposite failure mode: they can save cost but silently lose quality on harder tasks.

ReflexOS addresses the decision between those extremes. It treats model capability as a budgeted resource and requires observable evidence before a stronger tier is used.

## Solution Overview

ReflexOS is an adaptive cognitive orchestration layer with four stages:

1. **Deterministic fast path.** Exact operations such as hashing, text statistics, JSON fingerprinting and safe arithmetic are executed by verified tools without an LLM.
2. **Reflex Fabric.** A deterministic local gate decides whether semantic routing is worth another call.
3. **JEV semantic routing.** When configured, TypeSafe JEV supplies bounded probabilistic advice about uncertainty, collaboration and human checkpoints. A credential-free local fallback keeps the workflow reproducible.
4. **LUNA-FIRST execution with proof-carrying escalation.** Every generative task starts on Luna. Sol or Astra can only be reached after explicit acceptance checks fail and the local escalation gate permits it.

The result is an inspectable path such as `deterministic`, `luna`, `luna -> sol`, or `luna -> sol -> astra`, together with factual telemetry explaining the transition events.

## Innovation & Uniqueness

The core innovation is **proof-carrying escalation**. Model routing is not merely a classifier that predicts which model might be best. ReflexOS requires a concrete runtime reason to spend more intelligence: failed acceptance criteria, uncertainty, conflicting evidence, risk, or a bounded semantic checkpoint.

A second innovation is the separation between two different decisions that are often conflated:

- **Should we ask a semantic router?** — decided by the deterministic Reflex Fabric.
- **Should we unlock a stronger generative tier?** — decided only after observable gate failure and budget checks.

JEV remains advisory. It cannot bypass hard local budgets, acceptance criteria or human checkpoints.

## How AI Is Used

TypeSafe JEV is used for compact semantic System-One decisions when configured. It estimates uncertainty and the useful review shape without owning execution safety. Generative tasks are then handled through a tiered model abstraction: Luna first, Sol second, Astra last.

AI is deliberately *not* used for operations that deterministic code can solve exactly. This is a design choice: effective AI use means applying AI where semantic generation is valuable rather than maximizing the number of model calls.

## Technology Stack

- Python 3.11+
- TypeSafe JEV integration through a JSON subprocess adapter
- Provider-neutral model adapter for OpenAI-compatible chat endpoints
- Gradio demonstration UI
- Pytest regression suite
- GitHub Actions CI
- Standard-library-only core runtime

## System Architecture / Workflow

`Task + checks -> deterministic skill? -> Reflex Fabric -> optional JEV -> Luna -> acceptance gate -> optional JEV checkpoint -> Sol -> gate -> Astra -> final gate -> factual checkpoint`

Only verified deterministic results are cached. Model outputs are never assumed correct because of model identity or agreement.

## Implementation Details

The project uses typed public contracts for tasks, limits, semantic decisions, model responses and run results. The execution engine enforces local call/token/time/checkpoint budgets. Acceptance checks support non-empty output, required/excluded text, strict JSON equality and numeric ranges.

A safe arithmetic tool parses a Python expression into an AST and evaluates only an explicit allowlist of numeric constants, operators and functions. It never calls `eval` or `exec`.

The JEV adapter writes compact UTF-8 JSON files into a temporary directory, invokes an existing authenticated JEV connector, validates the returned schema, and converts it to a small `SemanticDecision`. Credentials never belong in the competition repository.

## Reproducible Evaluation

The repository includes a credential-free 40-task synthetic routing-policy benchmark:

- 16 deterministic tasks
- 14 easy generative tasks
- 7 medium generative tasks
- 3 hard generative tasks

The simulated provider transparently assigns capability, token and abstract-cost budgets to the three tiers. Against an intentionally simple always-Astra policy, both policies accept 40/40 tasks in the simulator, while ReflexOS produces:

- 15,830 vs 54,000 observed simulated tokens — **70.69% reduction**
- 100 vs 480 abstract cost units — **79.17% reduction**
- routes exactly matching task difficulty: deterministic / Luna / Luna->Sol / Luna->Sol->Astra

These numbers measure routing-policy behavior only. They are not presented as real-model accuracy, energy consumption, price, or frontier-model superiority.

## Testing

The current release passes 20/20 automated tests. Coverage includes deterministic execution, code-injection rejection, strict checks, cache integrity, mandatory Luna-first ordering, evidence-gated escalation, router-failure fallback, critical-risk human checkpoints, hard budgets and benchmark invariants.

## Challenges & Solutions

**Challenge: semantic routers can fail or be unavailable.**  
Solution: record the failure and use a conservative local router; never silently bypass verification.

**Challenge: a routing benchmark can be mistaken for a model benchmark.**  
Solution: use a fully transparent deterministic simulator, label every number as synthetic policy evidence, and keep real-provider evaluation separate.

**Challenge: powerful models can become an unconditional shortcut.**  
Solution: encode Luna-first and evidence-gated escalation as engine invariants rather than prompt instructions.

**Challenge: exact tools can create a code-execution surface.**  
Solution: strict operation allowlists and AST-based arithmetic with no arbitrary execution.

## User Experience

The Gradio interface exposes a Route Inspector and a one-click benchmark. A judge can understand the main idea without an API key: exact work stays deterministic, generative work begins on Luna, and stronger tiers appear only when the policy has evidence to justify them.

## Scalability & Feasibility

ReflexOS is intentionally small and provider-neutral. New model backends, semantic routers and deterministic skills can be added behind typed interfaces. Core orchestration does not require a GPU or TPU. This makes deployment feasible from a laptop to a cloud agent service while preserving the same control-flow evidence.

## Future Scope

- Real multi-provider A/B evaluation with recorded latency/token/cost evidence
- richer domain-specific acceptance evaluators
- independent semantic critics for high-risk tasks
- OpenTelemetry-compatible run traces
- policy learning from historical accepted/rejected routes without weakening hard safety gates
- distributed execution through the P2PCLAW ecosystem

## Team

**Francisco Angulo de Lafuente** — architecture, implementation, evaluation and documentation.

The official competition requires the final registered Kaggle team to satisfy its team-size rules. This writeup intentionally lists only confirmed identities; it does not invent additional team members.
