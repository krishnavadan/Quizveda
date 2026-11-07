# QuizVeda

A personalized, profile-driven quiz and knowledge platform. It combines progressive quiz excitement with multi-perspective learning under an original product identity.

> **Project status:** Product and implementation specification baseline is committed. No running application is included yet.

## Product experiences
- **Play to Win:** progressive rounds, timer, lifelines, score and session result.
- **Play to Learn:** practice, explanations, topic progress and optional adaptation.

## Core principles
1. Profile-aware, never profile-restricted; explicit choices always win.
2. Multi-perspective question design across cognitive objectives.
3. Immutable, independently versioned JSON content packs.
4. AI is optional and never required for normal gameplay.
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
- `architecture/`: architecture decision records ADR-001 through ADR-005.
- `content/`: authoring checklist, JSON examples and schemas.
- `engineering/sql/`: PostgreSQL starter schema.
- `engineering/`: engineering implementation index.

## Recommended implementation sequence
1. Resolve open decisions in `docs/23-glossary-and-product-decisions.md`.
2. Convert starter SQL into reviewed Alembic migrations.
3. Implement domain services and deterministic selection.
4. Implement content import, validation, review and publication.
5. Implement server-authoritative gameplay and API contracts.
6. Complete security, accessibility, performance and release gates before public launch.

## Naming and licensing
**QuizVeda** is a working product name; complete trademark, company-name and domain clearance before commercial use. Third-party content rights are not implied. Every pack must record provenance and usage rights.

## Specification maturity
These files are a detailed implementation baseline, not a deployed application or a legal/security certification. Review open decisions, hosting assumptions, scoring policy and data retention before production.
