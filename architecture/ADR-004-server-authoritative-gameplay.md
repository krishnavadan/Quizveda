# ADR-004: Server-authoritative gameplay

- **Status:** Accepted for MVP
- **Date:** 2026-11-08

## Context

Quiz sessions contain answer keys, timers, scoring, lifeline state and progression. If the browser is authoritative, a user can inspect or alter client state, replay submissions, manipulate timers or skip progression.

## Decision

The backend owns the canonical session state machine. The client receives only the active question payload and presentation-safe metadata. Correct answers, scoring rules and future questions remain server-side until the answer submission has been accepted.

## Required behavior

1. Session creation pins a published content-pack version and selection-policy version.
2. A question is delivered with a session-scoped question token and deadline metadata.
3. Answer submission includes a unique idempotency key.
4. The server validates session ownership, active question, token, deadline and answer format.
5. The server records the attempt exactly once and calculates correctness and score.
6. The response reveals the explanation and correctness only after acceptance.
7. Repeated submissions return the original outcome; they do not score twice.
8. Session transitions are transactional and auditable.

## Consequences

- Slightly more backend work and state management.
- Better protection against casual tampering and answer leakage.
- Consistent results across browser, PWA and future native clients.
- Offline play is limited in the MVP; a later offline mode would require a separate threat model and reconciliation design.