# ADR-006: AI Is Development-Only

**Status:** Accepted
**Date:** 2026-11-08

## Context
QuizVeda needs AI-assisted engineering and may use AI during offline content production. The learner product must remain predictable, affordable, auditable and operational without external model providers.

## Decision
AI is used exclusively in internal development and content-authoring workflows. It is not a feature or runtime dependency of the learner-facing application.

### Permitted internal uses
- Requirements analysis, architecture and documentation assistance.
- Code drafting, refactoring suggestions, test generation and code review.
- Security, accessibility and UX review assistance.
- Offline question/content drafting, translation drafts, metadata suggestions and verification support.
- Internal retrieval over approved product specifications, ADRs, code, schemas, test artefacts and content provenance.

### Prohibited production uses
- No learner-facing chatbot, tutor or AI assistant.
- No live AI-generated questions, hints, explanations or lifeline outcomes.
- No LLM-based question selection, scoring, timer, progression or recommendations.
- No agent, skill runtime, MCP server, vector database or AI memory graph in the production learner deployment.
- No model API keys, AI SDK/runtime dependencies or model-provider network requirement in production.

### Learner application behavior
The PWA and API use deterministic application logic, explicit profile/session choices and approved immutable content packs. Questions, hints and explanations are authored and reviewed before publication. Recommendations and difficulty adaptation use transparent deterministic rules. Gameplay must work when all model-provider services are unavailable and credentials are absent.

### Content publication controls
AI-generated material is a draft, never a trusted source. It must pass schema validation, independent answer verification, source/rights checks, age/safety/bias review and human editorial approval. Only approved, versioned content may be published.

### Development environment controls
Agents operate in isolated workspaces and scoped branches. They open pull requests; CI and human reviewers determine acceptance. Agents cannot push directly to protected main, self-approve, access production learner data or secrets, alter permissions, or deploy/publish without explicit human authorization. Use synthetic or sanitized test data.

## Consequences
- No runtime AI cost, latency or model-provider outage risk for learners.
- Deterministic behavior is easier to test and audit.
- Internal AI workflows still require prompt-injection defenses, least privilege, audit and human review.
- Future introduction of learner-facing AI requires a new ADR, explicit product approval, privacy/safety review and revised threat model; it is not implied by this decision.

## Verification
Release tests confirm learner journeys work without model credentials or provider egress. Production manifests contain no AI/agent/MCP runtime packages or model secrets. Content provenance and human approval are required for every published pack.
