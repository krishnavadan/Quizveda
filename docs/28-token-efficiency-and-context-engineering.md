# 28. Token Efficiency, Context Engineering and Model Routing

## Principles
Optimise useful, correct work per token—not minimum tokens at any cost. Never compress away evidence, safety constraints, uncertainty or acceptance criteria.

## Task-specific context
Assemble policy + agent contract + relevant ADR/decision IDs + compact skill instructions + retrieved evidence cards + input artifact + output schema + concise acceptance checklist. Do not send the whole repository or full conversation by default.

## Model routing
- Deterministic code: scoring, state transitions, calculations, schema checks and deduplication.
- Small model: classification, routing, extraction and tagging.
- Mid-tier model: drafts, explanations, summaries and localization drafts.
- Strong reasoning model: source conflicts, complex verification and architecture/security review.
- Human reviewer: safety, rights, disputed facts, low confidence and publication.

Keep model routing configurable and vendor-neutral.

## Budget controls and efficiency
Declare input/output/total token ceilings per task. Start compact; allow bounded evidence expansion only when needed. Set output caps by artifact type. Limit delegation depth and parallel fan-out. Require reason for expensive model escalation. Cache stable prefixes and immutable retrieval results. Use deterministic prefilters, structured outputs, evidence IDs, batch independent checks and versioned summaries linked to originals. Stop no-progress loops.

## Quality safeguards
Compression preserves references, uncertainty, exclusions and constraints. Contradictory evidence must remain visible. Validate structured output. If budget exhaustion prevents verification, return needs_review, never approved.

## Metrics
Cost per accepted question/pack, tokens per successful task, first-pass acceptance, retry rate, escalation rate, retrieval hit rate, factual error rate and reviewer correction rate. Optimise quality-adjusted cost.
