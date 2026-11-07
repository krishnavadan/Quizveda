# Test Strategy and Acceptance Catalogue

## Pyramid
Unit tests: scoring, state transitions, eligibility, difficulty, personalization precedence and validators. Integration: PostgreSQL constraints, transaction semantics, storage, cache and outbox. Contract: OpenAPI/events. E2E: browse→configure→play→answer→result→progress. Security: authorization, replay, IDOR, answer leakage and uploads. Performance: catalog, session, concurrent answers and publishing. Accessibility/localization checks.

## Critical acceptance scenarios
- Guest completes game without registration or profile.
- Explicit topic/difficulty is honored; personalization off ignores behavioral signals.
- Only approved/published revisions selected; existing session remains pinned after rollback.
- Session create and answer submission are idempotent.
- One accepted answer maximum per question; concurrent submissions produce one score outcome.
- Client cannot set correctness, score, time remaining or next question.
- Correct answer/explanation revealed only after accepted submission.
- Expired question token/deadline cannot score.
- User A cannot read/mutate User B session.
- Invalid pack produces actionable record-level errors.

## Property tests
Score non-negative and bounded; position monotonic; one attempt per question; no duplicate revision; selected references resolve to approved immutable revisions; all protected resources enforce ownership.

## Release gates
Critical/high defects resolved or mitigated; migration and rollback reviewed; privacy/security checks passed; accessibility smoke test passes; performance thresholds measured; monitoring, alerts, backup and restore verified.