# QuizVeda

A personalized, profile-driven quiz and knowledge platform. QuizVeda uses the excitement of progressive quiz gameplay while maintaining its own identity, content, interaction design, and brand.

> **Project status:** Product discovery and specification baseline. This repository does not yet contain a running application.

## Product experiences

- **Play to Win:** progressive rounds, timed questions, lifelines, score and session summary.
- **Play to Learn:** practice, explanations, topic mastery and skill development.

Both experiences use the same governed question bank and taxonomy.

## Product principles

1. Profile-aware, never profile-restricted: explicit user choices always take priority.
2. Multi-perspective learning: questions can test recall, understanding, application, analysis, evaluation and creation.
3. Content is data: independently versioned JSON packs can be validated, published, rolled back and served through a CDN.
4. AI is optional: normal gameplay and scoring must not require a live model call.
5. Server-authoritative gameplay: answers, scoring, timers and session transitions are validated on the server.
6. Original identity: do not copy KBC/Kaun Banega Crorepati branding, logo, music, host likeness, scripts, question bank or distinctive trade dress.

## Proposed technology

- Frontend: React / Next.js, responsive PWA
- Backend: Python FastAPI modular monolith
- Primary data: PostgreSQL
- Cache / ephemeral coordination: Redis when justified by measured need
- Content delivery: object storage + CDN, immutable versioned JSON
- Background work: worker queue for imports, reports and optional AI-assisted authoring

## Repository map

- `docs/` — product, functional, UX, architecture, security, API and delivery specifications
- `architecture/` — architecture decision records
- `content/` — content pack guidance, JSON examples and schemas
- `engineering/` — implementation-level engineering specifications (to be added in subsequent batches)

## Initial delivery sequence

1. Confirm product decisions and scope.
2. Finalize domain model, database schema and ERD.
3. Specify question selection, perspective coverage and personalization.
4. Specify content pack ingestion, validation, publication and rollback.
5. Specify APIs, events, admin workflows and acceptance tests.
6. Build vertical MVP slices; test each slice before expanding.

## Naming

**QuizVeda** is a working product name only. Complete trademark, company-name and domain clearance before public commercial use.

## License and content

No license for third-party question content is implied. All question packs must have documented provenance and usage rights.