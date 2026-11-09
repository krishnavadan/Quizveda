# Guest Gameplay API Contract — Initial Vertical Slice

## Base path
`/api/v1/gameplay`

## 1. Create a guest session
`POST /sessions`

Request:
```json
{
  "pack_key": "general-science",
  "version": "1.0.0",
  "locale": "en-IN",
  "mode": "play_to_learn",
  "question_count": 10,
  "difficulty": "beginner",
  "taxonomy_scope": ["science"]
}
```

The service requires an exact published pack version and selects only approved revisions in that version. Locale, explicit taxonomy and requested difficulty are hard filters. If the catalog cannot satisfy the requested count, return HTTP 422 with the available count; never broaden scope silently.

Response includes `session_id`, a one-time `guest_token`, mode, count and first question. Store the guest token securely on the client; only its SHA-256 hash is stored in the database. The response never contains answer keys.

## 2. Retrieve the current question
`GET /sessions/{session_id}/current`

Header: `Authorization: Bearer <guest_token>`

Returns the current session-question identifier, position, stem, options, time limit and server deadline. The server starts the timer when it first issues a question. A GET after expiry advances the session deterministically to the next question; completed sessions return score and question count.

## 3. Submit an answer
`POST /sessions/{session_id}/answers`

Headers:
- `Authorization: Bearer <guest_token>`
- `Idempotency-Key: <unique-request-key>`

Request:
```json
{
  "question_id": "session-question-uuid",
  "selected_option_key": "B"
}
```

The submitted question ID must match the current issued question. The server validates the option, enforces the deadline, evaluates against its private answer key, records the attempt, updates score and advances the session in one transaction. A repeated request with the same idempotency key and payload replays the original outcome. Reusing a key with a different payload returns HTTP 409.

## Domain invariants
- Only published pack versions and approved revisions are playable.
- The client never supplies score, correctness, next question or answer key.
- Session owns its immutable question sequence and selection-policy version.
- Question order and scoring are server-authoritative.
- Each session question accepts at most one answer.
- A stale question ID cannot be applied to the next question.
- Guest token hashes are compared in constant time.
- Timer and answer state are persisted; client clocks are informational only.
- All content and explanations are pre-authored/reviewed. No AI service is called at runtime.

## Current scope limits
The initial slice has guest-only access, fixed correct-answer score of 100, no lifelines, no user-account linking, no payment/prizes, no rate-limiting middleware and no admin CMS endpoints. These are separate implementation tasks, not implied capabilities.
