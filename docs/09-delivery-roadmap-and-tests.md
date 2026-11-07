# Delivery Roadmap and Test Strategy

## Delivery stages
1. Foundation: repo, CI, environment, database migrations, identity, taxonomy.
2. Playable slice: session state machine, question delivery, answer submission, scoring, results.
3. Learning: explanations, history, progress and optional profile signals.
4. Content operations: pack upload, validation, editorial workflow, publication and rollback.
5. Hardening: accessibility, localization, security, load testing, monitoring and backup restore.
6. Expansion: additional question types, educator features, multiplayer and AI-assisted authoring subject to separate approval.

## Test layers
Unit tests for selection/scoring/state machine; integration tests for DB and storage; contract tests for API/events; end-to-end journeys; security tests for IDOR/replay/answer leakage; load tests for catalog/session/answer flows; accessibility and localization checks.

## Release gates
Critical/high defects resolved or accepted with mitigation; migration plan reviewed; privacy/security checklist passed; smoke tests pass; performance thresholds measured; monitoring/alerts/backups/restore verified.

## Definition of done
Acceptance criteria linked; code reviewed; tests pass; API/schema docs updated; privacy/security reviewed; telemetry redacted; retry/failure behavior tested; runbook and rollback available.