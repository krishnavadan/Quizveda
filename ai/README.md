# QuizVeda AI Operations

This directory indexes the governed AI operating model. AI is optional and is not a runtime dependency for core gameplay.

- Agent architecture: ../docs/24-ai-agent-architecture.md
- Skill registry: ../docs/25-agent-skill-registry.md
- Memory graph and indexing: ../docs/26-memory-graph-and-indexing.md
- MCP tooling and permissions: ../docs/27-mcp-tooling-and-permission-model.md
- Token/context engineering: ../docs/28-token-efficiency-and-context-engineering.md
- Quality system: ../docs/29-quality-assurance-and-award-level-bar.md
- Age-aware UX: ../docs/30-age-aware-personalized-ux.md
- Evaluation/observability: ../docs/31-ai-evaluation-and-observability.md

Non-negotiables: deterministic gameplay; human approval before publication; evidence and provenance; least-privilege tools; no hidden reasoning traces in durable memory; no sensitive learner profiling or age inference; transparent user-controlled personalization.


## Hard boundary
**AI is for development only, not for the app.** This directory documents internal agent/skill/MCP workflows and offline content assistance. Do not package anything here into the production PWA, API, worker or learner-facing deployment. Do not connect agents to production learner data or secrets. Runtime product behavior—including question selection, hints, explanations, recommendations, scoring and progression—is deterministic. AI-assisted content is only a draft until human-reviewed, approved and published as an immutable content pack.
