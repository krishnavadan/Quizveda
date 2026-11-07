# API Errors, Events and Idempotency

## Error envelope
```json
{"error":{"code":"SESSION_QUESTION_EXPIRED","message":"This question is no longer active.","request_id":"req-id","details":[]}}
```
Do not return stack traces, SQL, answer keys, secrets or internal object URIs.

## HTTP status
400 malformed/domain configuration; 401 unauthenticated; 403 unauthorized; 404 absent/not visible; 409 state/idempotency conflict; 422 semantic validation; 429 rate limited (Retry-After); 500 unexpected; 503 dependency unavailable.

## Idempotency
Require keys for session creation and answer submission. Scope by principal and endpoint. Persist request fingerprint and original response. Same key+same request returns original result; same key+different request returns 409. One accepted answer per session question.

## Events
session.created.v1, session.started.v1, question.issued.v1, answer.accepted.v1, lifeline.used.v1, session.completed.v1, session.abandoned.v1, content.pack.validated.v1, content.pack.approved.v1, content.pack.published.v1, content.pack.rolled_back.v1.

## Delivery
Use transactional outbox: state change and outbox record commit together. Publisher retries transient failures. Consumers deduplicate by event_id and tolerate duplicate delivery/unknown optional fields. Never publish events only from in-memory post-commit callbacks.