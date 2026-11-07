# API and Event Contracts

## API conventions
REST under /v1; JSON; UTC ISO-8601 timestamps; UUID resource IDs; bearer authentication for account routes; explicit admin scopes. Use request IDs and consistent error envelopes.

## Main endpoints
GET /catalog; GET/PATCH /me; POST /sessions; GET /sessions/{id}; POST /sessions/{id}/answers; POST /sessions/{id}/lifelines; POST /sessions/{id}/abandon; GET /me/progress; GET /sessions; admin content pack and publication endpoints.

## Session create
Requires mode, locale, question count and optional taxonomy IDs/difficulty policy/personalization flag. Require Idempotency-Key. Return session ID and first question without answer key.

## Answer submit
Requires question token, option key, response time and Idempotency-Key. Server validates owner, active question, token and deadline. Return accepted result, correctness, awarded score, explanation and next question/session completion.

## Events
session.created, session.started, question.issued, answer.accepted, lifeline.used, session.completed, session.abandoned, content.pack.validated, content.pack.approved, content.pack.published, content.pack.rolled_back.

## Reliability
Use transactional outbox. Consumers deduplicate by event ID. Same idempotency key and same request returns original result; same key with different request returns conflict. Retry transient failures only.