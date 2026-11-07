# UI/UX Specification

## Information architecture
Public: Home, Explore Subjects, Modes, How to Play, Sign In. Authenticated: Profile & Preferences, Play, Session History, Progress, Settings, Data & Privacy. Admin is a separate protected application area.

## Main screens
1. Home: original brand identity, concise value proposition, primary Play action, secondary Explore.
2. Catalog: hierarchical subjects/topics, search and locale filter.
3. Game setup: mode, scope, difficulty policy, question count, personalization toggle.
4. Game stage: progress indicator, question stem, option controls, timer, lifeline controls, accessible status announcements.
5. Answer feedback: correctness, score change, explanation, provenance/reference and Continue.
6. Result: score, completion state, answer review and optional next action.
7. Profile: optional fields, interests, language, accessibility, personalization toggle.
8. Progress: attempts and approximate topic mastery with sample-size caveats.
9. Admin CMS: table-first workflows, validation detail, revision comparison and publication history.

## Interaction rules
- Never display correctness before accepted submission.
- Disable options after accepted answer.
- Show clear timeout state; server clock is authoritative.
- Do not rely on color alone for correct/incorrect.
- Confirm destructive admin actions and production publish/rollback.
- Use loading, empty, offline, retry and error states for every async flow.

## Accessibility
Target WCAG 2.2 AA. Keyboard navigation, visible focus, semantic labels, screen-reader announcements, contrast, reduced motion, text resizing and timer accommodations. Mobile-first responsive layout; avoid tiny tap targets.

## Visual identity
Create a distinct QuizVeda visual language. Do not imitate KBC's logo, palette/layout signature, stage treatment, sound cues, host or exact question reveal sequence.

## Profile-driven presentation
The interface uses optional profile preferences to select accessible defaults for typography, content density, navigation guidance, language, reading complexity, motion and assistance. Age-aware defaults and safeguards are specified in docs/30-age-aware-personalized-ux.md. Users can override settings independently; do not infer age or reduce factual depth. Validate each profile experience with representative usability testing.
