# First Vertical Slice — Acceptance and Test Plan

## Happy path

Given a published pack with at least five approved questions, a guest starts a session and receives a session ID and exactly one current question. The guest submits an option; the server evaluates it, persists the attempt and returns safe feedback. The next request returns the next question or a completed result.

## Required negative and resilience tests

1. Unknown session -> stable 404.
2. Session not owned by caller -> no data disclosure.
3. Completed session -> answer rejected without mutation.
4. Non-current question -> conflict response.
5. Invalid option ID -> validation error; no attempt persisted.
6. Same idempotency key and payload -> original response; one attempt only.
7. Same idempotency key with different payload -> conflict.
8. Concurrent submissions for one question -> at most one accepted transition.
9. Client timeout then retry -> no duplicate score.
10. Unpublished/unavailable pack -> session creation fails safely.
11. Pack published after session start -> session remains pinned to original version.
12. Timer expiry -> server policy decides outcome; client clock is informational.
13. Unsupported locale -> documented fallback or validation response.
14. Database transaction failure -> no partial attempt/session update.
15. Admin-only fields never appear in public DTOs.

## Security and privacy checks

- No answer key in catalog or current-question responses.
- No secrets in source control, logs or error responses.
- Rate limits on session creation and answer submission.
- Guest capability tokens are high entropy, scoped, expiring and stored safely.
- Profile fields are optional, explicit and editable/deletable.
- Analytics avoid answer payloads and unnecessary personal data.
- Admin actions are authorized and auditable.

## Release gate

Critical tests pass; migrations run from empty database; content validation passes; OpenAPI is generated and reviewed; accessibility smoke test passes; production HTTPS/CORS/cookie settings are secure; rollback is documented.
