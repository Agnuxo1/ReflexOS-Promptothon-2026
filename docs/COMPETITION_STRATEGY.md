# Promptothon 2026 Competition Strategy

## Verified competition state — 23 September 2026

The official Kaggle page reports a 100-point judge rubric: Technical Implementation 25, Innovation & Originality 20, Effective Use of AI 20, Problem Relevance & Impact 15, User Experience & Usability 10, and Scalability & Feasibility 10.

At the time of analysis, Kaggle publicly reports 2 teams and 2 submissions, but the public Writeups page exposes no competitor writeups and the Code page exposes no notebooks. Therefore, the strategies of the currently listed first and second submissions cannot be responsibly reconstructed from public evidence. Any claim about their architecture would be speculation.

### Monitoring rule

If competitor writeups or notebooks become public before final submission, compare them on documented architecture, demo clarity, reproducibility, measured evidence, and rubric coverage. Do not copy undisclosed or private work; use only public evidence.

## Chosen track

**LLMs & Automation.**

A live TypeSafe JEV consultation selected this track with probability 1.00 for the proposed hybrid. The same consultation selected the `adaptive_cognitive_os` bundle with probability 1.00 and chose Universal Cognitive Architecture JEV v2 as the strongest primary base among the supplied candidates (0.67 versus 0.21 JEV v3 and 0.11 King-Skill). These values are routing advice, not guarantees of judge scoring.

## Product thesis

Most agent systems optimize answer capability but do not make the *decision to spend intelligence* explicit and testable. ReflexOS turns that decision into code.

The judge-visible story is simple:

1. Give ReflexOS an exact task: it uses no LLM.
2. Give it an easy generative task: Luna succeeds and it stops.
3. Give it a harder task: the Luna output fails an explicit gate, which becomes the evidence that unlocks Sol.
4. Give it a hard task: the same proof chain reaches Astra only after Luna and Sol fail.
5. Run the 40-task benchmark to show that the policy preserves acceptance on the simulator while reducing simulated tokens and abstract cost.

## Hybridization decisions

### Keep from Universal Cognitive Architecture JEV v2

- explicit acceptance gates
- integrity-checked deterministic cache
- bounded model calls and token budgets
- factual checkpoints
- provider separation

### Keep from JEV Orchestrator v3

- Reflex Fabric
- event-driven semantic checkpoints
- LUNA-FIRST invariant
- evidence-gated escalation
- semantic-router failure fallback

### Keep from King-Skill v4

- deterministic tool-first philosophy
- strict separation between exact computation and generative work
- empirical-claim discipline

### Do not use as the primary path

- GPU-heavy CHIMERA/NEBULA training: impressive research, but it consumes scarce compute without directly improving this judging rubric.
- The Living Agent as the core: persistent autonomous memory is interesting, but it makes a three-minute demo harder to explain and reproduce.
- P2PCLAW as the core: strong network/visualization layer, but less direct than the adaptive routing problem for the LLMs & Automation track.

## Rubric attack plan

### Technical Implementation — 25 points available

Evidence: 20 automated tests, typed dataclasses/protocols, safe AST math executor, hard budgets, cache integrity validation, JEV subprocess boundary, failure fallback, CI on Python 3.11/3.12.

### Innovation & Originality — 20 points available

Lead with **proof-carrying escalation**: every transition to a stronger model has a machine-observable reason. JEV does not simply choose a model; a deterministic Reflex Fabric decides whether a semantic checkpoint is worth paying for, and local acceptance failure is what unlocks escalation.

### Effective Use of AI — 20 points available

Use JEV for bounded probabilistic semantic decisions and LLM tiers for genuinely generative work. Avoid using an LLM for hashing, counting or arithmetic simply to claim more AI.

### Problem Relevance & Impact — 15 points available

Frame the problem as the operational inefficiency of "largest model for everything" agent stacks: unnecessary inference cost, latency and energy, plus opaque escalation. ReflexOS makes the trade-off inspectable.

### UX & Usability — 10 points available

The Gradio demo must tell the story in under 30 seconds per interaction. Judges should not need credentials for the benchmark or policy simulator.

### Scalability & Feasibility — 10 points available

Core runtime is dependency-free; provider and semantic-router integrations are adapters; credentials remain external; no GPU or TPU is required for the orchestration layer.

## Accelerator decision

Do **not** use Kaggle TPU merely because GPU quota is exhausted. A JEV consultation gave `needs_accelerator = 0.23`, and the architecture itself is CPU/API bound. TPU would add setup risk without improving the judge-visible value proposition. Colab or the local RTX 3090 should only be used if a later real-provider evaluation introduces a genuine accelerator workload.

## Known eligibility/logistics risk

The official Kaggle description states a 3–4 member team, dates 26–27 September 2026, venue AVN Institute of Engineering & Technology in Hyderabad, and ₹499 registration per participant. Project engineering can be completed remotely, but final eligibility/presentation requirements must be satisfied by the registered team. The repository does not invent teammates or claim physical attendance.
