# Functional Specification

## User capabilities
- Browse subject → domain → topic → subtopic.
- Choose game mode, language, question count, topic scope and difficulty.
- Play as guest or signed-in user.
- Optionally complete and edit a profile; turn personalization off.
- Receive one question at a time; select one option; see accepted outcome and explanation.
- Use an available lifeline; pause/resume where mode permits; abandon or complete a session.
- Review score, answers, explanations and topic progress.
- Export account data and request deletion.

## Session state machine
`created → in_progress → completed`; alternate terminal states: `abandoned`, `expired`. Server validates every transition. Session pins content-pack version and selection-policy version. Question positions are monotonic. Only the active question can be answered.

## Question delivery
Client receives question token, stem, options, position and deadline. It must not receive answer key, scoring rule internals or future questions. Submission includes question token, option key, response time and idempotency key. Server validates ownership, active position, deadline and token; persists outcome once; then reveals correctness and explanation.

## Modes
- Classic Ladder: progressively harder questions.
- Practice: fixed difficulty, explanation-first learning emphasis.
- Quick Quiz: short 5/10-question session.
- Topic Challenge: user-selected taxonomy scope.

## Lifelines
MVP candidates: 50:50, Hint, Skip. Availability, use limits and exact effects are configuration-driven. Lifeline results are generated server-side and audited.

## Profile/personalization
Optional and editable. Current session choices override explicit profile preferences; profile preferences override soft observed signals. Personalization off means no behavioral signal is applied.

## Content operations
Draft → upload → validate → editorial review → approve → publish. Published versions immutable. Rollback changes active pointer for new sessions only; active sessions retain pinned versions.

## Admin
Question editor, taxonomy manager, bulk import, validation report, review queue, pack/version manager, staging preview, production publication, rollback, user support with audited access, RBAC and audit log.

## Business rules
One accepted attempt per question; no duplicate question revision in a session; answer keys never appear in public assets; content must be approved and published; question source/provenance and usage rights required.