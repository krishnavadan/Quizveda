# Engineering Workplan — QuizVeda

**Status:** Proposed implementation sequence  
**Baseline:** Product specification v0.1

## Delivery guardrails

- Build a modular monolith first; extract services only when scale, ownership or isolation requirements justify it.
- Keep the question bank independent from application releases.
- Pin every live game session to a published content-pack version.
- Never send correct answers to the client before the corresponding answer is accepted.
- Use deterministic scoring and selection rules for the MVP.
- Make AI-assisted content generation an editorial aid, not a runtime dependency.
- Every state-changing API must define authentication, authorization, validation, idempotency and audit expectations.

## Engineering batches

| Batch | Deliverable | Exit criteria |
|---|---|---|
| 01 | Domain model, database schema and ERD | Entities, keys, constraints, indexes and lifecycle rules reviewed |
| 02 | Question selection and perspective engine | Deterministic algorithm, explainable selection trace and test fixtures |
| 03 | Profile intelligence and personalization | Explicit preference precedence, consent and fallback rules |
| 04 | Content pack pipeline | Schema validation, linting, preview, publish, rollback and version pinning |
| 05 | Admin authoring and operations | Roles, review workflow, bulk import and audit trail |
| 06 | API and event contracts | OpenAPI-ready endpoints, payloads, error model and idempotency |
| 07 | Stories and test catalogue | User stories, acceptance criteria, negative tests and NFR tests |
| 08 | MVP implementation | End-to-end playable slice with observability and deployment runbook |

## MVP vertical slices

### Slice A — Browse and configure
- Browse subject, topic and difficulty taxonomy.
- Select a mode and question count.
- Continue as guest or sign in.
- Apply explicit preferences without requiring a profile.

### Slice B — Play a session
- Create a server-side session.
- Deliver one question at a time.
- Accept one answer per question.
- Calculate score and progression on the server.
- Recover safely from refresh, retry and network interruption.

### Slice C — Learn and review
- Show explanation and source/provenance after answer submission.
- Save session history for signed-in users.
- Show topic-level progress with clear sample-size caveats.

### Slice D — Operate content
- Upload a versioned JSON pack.
- Validate schema and semantic rules.
- Preview questions and metadata.
- Approve and publish atomically.
- Roll back to a prior published version.

## Definition of done

A feature is done only when:
- requirements and acceptance criteria are linked;
- authorization and privacy implications are reviewed;
- automated unit and integration tests pass;
- API and schema changes are documented;
- telemetry avoids answer leakage and unnecessary personal data;
- failure and retry behavior is tested;
- operational ownership and rollback are documented.