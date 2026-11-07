# 31. AI Evaluation, Observability and Governance

## Traceability
Record task ID, agent/skill versions, model, prompt version, retrieval index version, source IDs, tool calls, token usage, latency, validation, reviewer outcome and artifact hash. Redact sensitive data and apply retention limits.

## Evaluation datasets
Maintain versioned gold sets for correctness, ambiguity, answer verification, distractors, explanations, age suitability, safety, bias, localization, retrieval grounding, citations, prompt injection, tool security and cost efficiency. Keep held-out evaluation data separate from examples.

## Release criteria
Model, prompt or skill updates pass regression and adversarial thresholds against the previous approved baseline. Roll out behind feature flags, monitor reviewer correction rate and retain rollback.

## Human oversight
Humans approve new content and policy changes. Agents cannot approve their own work, change policy, publish, delete learner data or grant access. High-risk output requires an accountable reviewer.

## Dashboards
Track content approval/rejection and provenance; agent first-pass acceptance and corrections; retrieval precision and stale index; cost per approved artifact; product completion, learning and trust; platform latency, errors and recovery.

## Incident process
Disable affected agent/tool or content pack, preserve audit evidence, assess impact, correct/rollback, perform root-cause analysis, add regression tests and communicate under approved policy. Agents cannot suppress or rewrite audit records.
