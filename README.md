# QuizVeda

A personalized, profile-driven quiz and knowledge platform. It combines progressive quiz excitement with multi-perspective learning under an original product identity.

> **Project status:** Product specifications and initial implementation slices are maintained in sequential draft pull requests. This repository is not yet a production deployment.

## Product experiences
- **Play to Win:** progressive rounds, timer, lifelines, score and session result.
- **Play to Learn:** practice, explanations, topic progress and optional adaptation.

## Core principles
1. Profile-aware, never profile-restricted; explicit choices always win.
2. Multi-perspective question design across cognitive objectives.
3. Immutable, independently versioned JSON content packs.
4. AI is development-only; the learner application has no AI runtime dependency.
5. Server-authoritative answers, timers, scoring and progression.
6. Original brand, content and UX; do not copy KBC/Kaun Banega Crorepati branding, logo, music, host likeness, scripts, question bank or distinctive trade dress.

## Proposed stack
React/Next.js PWA · FastAPI modular monolith · PostgreSQL · Redis only when justified · object storage/CDN · background worker.

## Repository map
- `docs/01–09`: PRD, functional requirements, personas, UX, content operations, architecture, security, API and delivery.
- `docs/10`: engineering workplan.
- `docs/11–15`: domain/database, selection engine, personalization, content pipeline and Admin CMS.
- `docs/16–17`: OpenAPI contract, errors, events and idempotency.
- `docs/18–23`: threat model/privacy, SLOs, test strategy, DevOps, analytics and decision register.
- `docs/24–31`: internal AI development/content operations, quality, age-aware UX and evaluation.
- `docs/32–33`: Admin CMS/RBAC and deterministic editorial quality assurance.
- `docs/34–35`: immutable question authoring, revision governance, authoring API and data model.
- `architecture/`: architecture decision records.
- `content/`: authoring checklist, JSON examples and schemas.
- `engineering/sql/`: PostgreSQL starter schema.
- `engineering/`: implementation blueprint, backend/frontend module maps, migration plan, acceptance tests, workplan, AI-assisted development workflow and gameplay API contract.
- `backend/`: FastAPI scaffold, migrations, gameplay/admin APIs and tests.
- `ai/`: internal-only agent, memory and MCP governance artefacts.

## Recommended implementation sequence
1. Resolve open decisions in `docs/23-glossary-and-product-decisions.md`.
2. Review and merge the foundational backend and admin PRs in dependency order.
3. Complete governed authoring workspaces, immutable revisions, validation and review.
4. Materialize immutable releases and verify storage/database reconciliation.
5. Complete learner PWA, gameplay flows, lifelines and progress.
6. Complete security, accessibility, performance and release gates before public launch.

## AI architecture boundary
**AI is development-only.** It supports internal requirements analysis, architecture, code assistance, test generation, security review and offline content-authoring. The deployed learner application has no LLM calls, agent runtime, MCP server, vector database or AI-token dependency. Published questions and explanations are human-approved immutable content; learner personalization is deterministic and profile/session-rule based. See `architecture/ADR-006-ai-development-only.md` and `engineering/ai-assisted-development-workflow.md`.

## Naming and licensing
**QuizVeda** is a working product name; complete trademark, company-name and domain clearance before commercial use. Third-party content rights are not implied. Every pack must record provenance and usage rights.

## Specification maturity
These files are an implementation baseline, not a deployed application or a legal/security certification. Review open decisions, hosting assumptions, scoring policy and data retention before production.
