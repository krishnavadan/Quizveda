# 24. AI Agent Architecture and Operating Model

## Objective and execution planes
Use bounded agents to improve research, question drafting, verification, localisation, UX and engineering. Agents are collaborators, not authorities.

**Content/build plane:** authorised staff workflows may use LLMs and MCP tools.  
**Learner plane:** gameplay, scoring, answer evaluation, timers and progression remain deterministic. Learner-facing AI may explain approved content or recommend approved topics; it cannot invent live questions or alter scores.

## Agent catalogue
| ID | Agent | Responsibility | Authority |
|---|---|---|---|
| A01 | Product Orchestrator | classify tasks and route workflows | route only |
| A02 | Knowledge Researcher | retrieve approved sources and citations | no publish |
| A03 | Taxonomy Curator | map topics, objectives and perspectives | propose |
| A04 | Question Architect | draft age-appropriate MCQs | draft only |
| A05 | Answer Verifier | independently solve and verify key/distractors | block on failure |
| A06 | Pedagogy Reviewer | assess objective, explanation and cognitive level | block critical issues |
| A07 | Age & Safety Reviewer | assess suitability, safety and stereotypes | block critical issues |
| A08 | Bias & Inclusion Reviewer | cultural assumptions, representation and accessibility | block critical issues |
| A09 | Localization Agent | translate and adapt by locale | draft only |
| A10 | Content Quality Editor | clarity, grammar, reading level and duplication | edit draft |
| A11 | UX Research Synthesizer | analyse consented usability evidence | insight only |
| A12 | Personalization Planner | propose transparent topic/difficulty choices | user choice wins |
| A13 | Assessment Analyst | aggregate item and cohort analysis | no high-stakes decisions |
| A14 | Test Engineer | generate tests and regression candidates | CI decides |
| A15 | Security & Privacy Reviewer | threat, data-flow and permission review | block critical risk |
| A16 | Release Auditor | verify approvals, gates and rollback | no unilateral release |

## Standard content workflow
Task intake -> policy classification -> evidence retrieval -> draft -> independent verification -> age/safety/bias review -> editorial review -> schema validation -> human approval -> immutable publication -> monitoring.

The drafting agent cannot be the sole verifier. High-risk or disputed material requires independent human review.

## Agent contract
Every run declares agent/version, task, permitted sources, output schema, tool allowlist, data classification, token budget, timeout, retry policy, evidence requirements, human-approval requirement and correlation ID.

Structured output includes status, artifact, evidence references, issues, confidence, model ID, prompt version, skill versions and usage. Confidence is advisory, never a substitute for evidence.

## Failure handling
Fail closed for answer-key uncertainty, child safety, privacy, rights and publication. Retry transient failures with bounded attempts. Escalate low-confidence or conflicting evidence. Preserve drafts and review history. Agents cannot grant permissions or call unlisted tools.
