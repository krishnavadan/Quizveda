# QuizVeda — Implementation Blueprint

**Status:** Engineering baseline for MVP.  
**Source of truth:** docs 01–23 and architecture ADRs.  
**Scope:** First production-shaped increment; this does not mean the application is deployed.

## 1. MVP delivery objective

Deliver one complete, server-authoritative single-player journey:
1. Open the PWA and browse topics.
2. Start Play to Learn or Play to Win.
3. Receive one question at a time from the server.
4. Submit an answer with an idempotency key.
5. Receive correctness, score update and explanation.
6. Complete or abandon the session.
7. View a result summary and session history.

Use a reviewed, versioned content pack. No runtime LLM dependency.

## 2. Architecture baseline

- Web: Next.js + TypeScript responsive PWA.
- API: FastAPI, Python modular monolith.
- Persistence: PostgreSQL, SQLAlchemy 2.x async, Alembic.
- Redis: only for measured needs; PostgreSQL remains authoritative.
- Content: versioned JSON packs validated before publication; immutable published versions.
- Operations: Docker Compose locally; CI runs lint, type checks, unit, integration and contract tests.

## 3. Backend module boundaries

| Module | Owns |
|---|---|
| identity | guest/user identity and authentication boundary |
| profile | explicit preferences and consent |
| catalog | topics, modes and public content metadata |
| content | pack import, validation, publication and version pinning |
| gameplay | session state machine, question delivery, answer submission and lifelines |
| progress | completed sessions and aggregates |
| admin | editorial workflows, review and publish controls |
| platform | configuration, database, telemetry and common errors |

## 4. First vertical slice API

- GET /api/v1/catalog
- POST /api/v1/sessions
- GET /api/v1/sessions/{session_id}/current-question
- POST /api/v1/sessions/{session_id}/answers
- POST /api/v1/sessions/{session_id}/abandon
- GET /api/v1/sessions/{session_id}/result

Current-question responses must never contain correct option IDs, answer-key metadata, future questions or internal selection seeds.

## 5. Gameplay invariants

- Server owns session state, question order, timer policy, scoring, lifeline availability and answer evaluation.
- A session pins a published content-pack version and selection-policy version at creation.
- Each answer request includes an idempotency key. Replays return the original outcome and do not increment score twice.
- A question can be answered only while its session is active and the question is current.
- Client timeout is not proof the server rejected a request; retry with the same idempotency key.
- Published versions are immutable. Corrections create a new version; active sessions retain their pinned version.
- Never send future questions to the browser.

## 6. Frontend route map

- / — landing and mode entry
- /play — mode and topic selection
- /session/[sessionId] — active quiz
- /session/[sessionId]/result — result and explanations
- /profile — optional profile and personalization controls
- /history — session history
- /admin — protected editorial console

## 7. Delivery sequence

1. Repository hygiene, environment configuration and CI.
2. Database schema and Alembic migration baseline.
3. Content-pack validation and deterministic import.
4. Catalog and session creation endpoints.
5. Question delivery, answer evaluation and idempotency.
6. Result, history and progress.
7. Responsive frontend vertical slice.
8. Admin authoring and publication workflow.
9. Security, accessibility, performance and release hardening.

## 8. Definition of done

- A fresh database migrates from zero.
- A known test pack imports and publishes through a controlled command.
- A guest completes a session without registration.
- Replaying an answer cannot change score or create another attempt.
- Wrong/stale question IDs are rejected with stable error codes.
- Answer keys and future questions are absent from public payloads.
- Integration tests cover state transitions and concurrent/replayed submissions.
- UI has loading, empty, error, retry and completed states.
- Secrets are injected at runtime and excluded from Git.
