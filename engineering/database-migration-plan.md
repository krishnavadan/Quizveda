# Database Migration Plan

## Policy

The SQL in engineering/sql/001_initial_schema.sql is a conceptual starter schema, not a production migration. Convert the approved model into Alembic revisions after reviewing constraints, indexes, deletion policy and ownership boundaries.

## Migration sequence

1. Foundation: users/guest principals, profiles, taxonomy and locale references.
2. Content: content packs, immutable pack versions, question revisions, options, perspectives and objectives.
3. Gameplay: sessions, session-question snapshots, attempts, lifeline usage and state version.
4. Progress: aggregate progress and history projections.
5. Operations: publication records, audit log and transactional outbox.

## Required safeguards

- UUID primary keys for externally addressable entities.
- UTC timestamps using timezone-aware types.
- Foreign keys and explicit ON DELETE policy.
- Unique (session_id, idempotency_key) constraint.
- Unique attempt constraint preventing duplicate accepted answers for a session question.
- Indexes for session owner/status, session-question ordering, pack publication state and user history.
- Check constraints for enumerated states and non-negative scores/sequence numbers.
- Store content pack version and selection-policy version on each session.
- Never hard-delete published revisions referenced by sessions.

## Rollout

- Generate revision from reviewed SQLAlchemy metadata.
- Inspect generated migration manually; do not blindly trust autogeneration.
- Test upgrade from empty database and from previous release schema.
- Test downgrade only where safe; destructive downgrades need an explicit operational procedure.
- Back up before production migration and verify restore procedure.
