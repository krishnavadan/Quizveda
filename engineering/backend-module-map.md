# Backend Module Map

## Proposed package layout

backend/
  pyproject.toml
  alembic.ini
  alembic/
    env.py
    versions/
  app/
    main.py
    core/ (config, errors, logging, security)
    db/ (base, session)
    modules/
      identity/
      profile/
      catalog/
      content/
      gameplay/ (domain, schemas, service, repository, router)
      progress/
      admin/
    tests/ (unit, integration)

## Dependency direction

Routers -> application services -> domain rules and repositories -> persistence adapters.

- Domain logic must not import FastAPI request objects.
- Repositories must not decide gameplay policy.
- API schemas are not ORM models.
- Admin routes require explicit admin authorization; hiding a route in the UI is not authorization.
- External services are adapters and must be replaceable.

## Gameplay service responsibilities

1. Validate session ownership or guest-session capability.
2. Load active session under transaction/locking policy.
3. Verify the submitted question is current and unanswered.
4. Resolve idempotency key before applying a new transition.
5. Evaluate against the server-side answer key.
6. Persist attempt and state transition atomically.
7. Return a safe DTO with correctness, score delta and explanation.
8. Emit an event through an outbox or reliable post-commit mechanism.

## Persistence and concurrency

Use PostgreSQL transactions. Enforce uniqueness for (session_id, idempotency_key) and prevent duplicate accepted attempts for one session question. Lock the session row or use an optimistic version column to serialize transitions. A transaction must persist the attempt and session update together or persist neither.

## API response safety

Public question DTO: question ID, prompt, ordered options, locale, optional media reference, remaining time and safe display metadata.

Never expose correct option ID, answer rationale before submission, internal selection seed, unpublished content, future questions, moderation notes or admin-only provenance fields.
