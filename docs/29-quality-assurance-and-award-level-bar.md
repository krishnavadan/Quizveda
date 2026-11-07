# 29. Product Quality System and Excellence Bar

## Quality promise
Award-calibre quality is an aspiration measured through product craft and evidence, not a guarantee of awards.

## Quality dimensions
| Dimension | Weight | Minimum |
|---|---:|---:|
| Factual correctness and answer integrity | 25% | 95/100 |
| Learning value and explanations | 15% | 90/100 |
| UX clarity and task completion | 15% | 90/100 |
| Accessibility and inclusion | 15% | 95/100 |
| Reliability and performance | 10% | 95/100 |
| Security and privacy | 10% | 100% critical controls |
| Provenance and rights | 5% | all required records |
| Visual consistency and polish | 5% | 90/100 |

Any critical safety, privacy, answer-key, rights or security defect blocks release regardless of score.

## Content rubric
Check one defensible correct answer, no ambiguity, evidence, currentness, plausible distractors, age suitability, language clarity, cognitive objective, useful explanation, cultural neutrality, duplicate similarity, rights and locale correctness. For disputed or rapidly changing facts, record an as-of date and review expiry. High-impact facts require independent verification.

## Evaluation layers
Unit, contract, integration, end-to-end, adversarial, human and production monitoring. Include prompt injection, malicious content, data leakage and tool misuse tests.

## Release gates
No open critical/high defect; independently verified answer keys; provenance/rights complete; manual keyboard and screen-reader review; security/privacy signoff; low-end mobile performance budgets; restore/rollback verified; privacy-safe analytics; human approval and immutable release artifact hash.

Measure task completion, time-to-first-question, quiz completion, explanation engagement, return learning, clarity, accessibility defects, crash-free sessions and trust. Do not optimise only session duration, streak pressure or compulsive return.


## AI boundary quality gate
Test that learner journeys work with all model-provider credentials absent and model-provider network egress unavailable. Verify that production dependency manifests contain no AI/agent/MCP runtime packages, no model secrets are provisioned, and all explanations/hints/questions originate from approved versioned content. Any accidental runtime model call is a release-blocking defect.
