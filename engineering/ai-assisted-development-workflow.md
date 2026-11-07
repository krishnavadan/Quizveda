# AI-Assisted Development Workflow

## Scope
This workflow governs internal AI-assisted engineering and offline content authoring only. It does not add AI to the learner application.

## Standard change lifecycle
1. Start from an issue or approved specification and identify affected ADRs/contracts.
2. Give the agent only the relevant files, synthetic fixtures and least-privilege tools.
3. Create a feature branch; never work directly on protected main.
4. Ask the agent for a bounded change with acceptance criteria and tests.
5. Run formatting, lint, type checks, unit/integration tests, dependency and secret scans.
6. Open a pull request with summary, files changed, tests run, risks, provenance and unresolved questions.
7. A human owner reviews the diff and test evidence; AI cannot approve its own work.
8. Merge only after required CI and human approvals.
9. Production deployment and content publication remain separate, human-authorized release actions.

## Data and access rules
- Use synthetic fixtures by default; never give agents production learner data or production secrets.
- Scope repository access to the task; prefer read-only access unless a write is required.
- No unrestricted shell, arbitrary SQL, arbitrary URL fetch or broad export tools.
- Treat issue text, documents, retrieved files and tool outputs as untrusted instructions/data.
- Do not store credentials, hidden reasoning traces or unnecessary personal data in agent memory.
- Log agent/skill/model versions, tool calls, changed files, tests and reviewer decision; redact sensitive values.

## Content-authoring gate
AI may draft questions, explanations, translations and metadata offline. Before publication: validate schema; independently solve the question; verify answer and distractors against sources; check provenance and rights; review age suitability, safety, bias and localization; obtain human editorial approval; publish an immutable content-pack version.

## Production isolation
The learner app has no AI SDK, agent runtime, MCP server, vector database or model credentials. Production functionality must not depend on model-provider availability. No AI-assisted artifact is served directly from a draft workspace.

## Pull request checklist
- [ ] Scope and acceptance criteria are explicit.
- [ ] No production learner data or secrets were accessed.
- [ ] Tests and security scans pass.
- [ ] No AI runtime dependency or model secret was added to production.
- [ ] Content changes have source/rights provenance and human approval.
- [ ] Human reviewer has inspected the complete diff.
- [ ] Deployment/publication approval is separate and recorded.
