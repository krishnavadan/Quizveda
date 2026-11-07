# Frontend Screen and Component Map

## Route-to-screen mapping

| Route | Screen | Primary states |
|---|---|---|
| / | Welcome | initial, loading catalog, unavailable |
| /play | Mode and topic selection | default, selected, no content, validation |
| /session/[sessionId] | Quiz play | loading, question, submitting, feedback, timeout, retry, completed |
| /session/[sessionId]/result | Result | loading, result, expired |
| /profile | Profile preferences | anonymous, saved, validation, personalization off |
| /history | Session history | loading, populated, empty, error |
| /admin | Admin console | unauthorized, draft, review, publish, rollback |

## Component boundaries

- AppShell: navigation, responsive layout and global feedback.
- ModeSelector: Play to Win / Play to Learn.
- TopicSelector: taxonomy-backed selection.
- SessionHeader: progress, timer and safe session metadata.
- QuestionPanel: prompt and options.
- AnswerOption: keyboard-operable selectable option.
- LifelineControls: available lifelines and confirmation.
- AnswerFeedback: correctness and explanation after server response.
- ResultSummary: score, completed rounds and next action.
- ProfilePreferences: explicit settings and personalization controls.

## Interaction requirements

- Keyboard navigation and visible focus states for all quiz controls.
- Do not use color as the sole indicator of correctness.
- Announce timer warnings and answer feedback accessibly.
- Disable duplicate submit visually, but rely on server idempotency.
- Preserve the idempotency key across retries of one answer.
- Do not optimistically reveal correctness or update authoritative score.
- On refresh/reconnect, fetch session state from the server.
- Respect reduced-motion preferences.

## Responsive behavior

Use a mobile-first single-column play surface. Tablet and desktop may add supporting context but must not expose future questions. Support narrow widths and browser zoom; meet WCAG 2.2 AA accessibility requirements.
