# Profile Intelligence and Personalization

## Optional fields
Self-described learning stage, broad occupation group, experience band, learning goal, language, selected topics/interests and accessibility preferences. All optional. Do not collect or infer sensitive traits.

## Signal types
Explicit saved preference, current-session explicit choice, declared goal, opted-in observed behavior and progress-derived topic signal. Store source, confidence, created/expiry timestamps and purpose. Observed signals decay and expire.

## Precedence
Current session choices > explicit saved preferences > declared goal > opted-in observed signals > generic defaults. Provide browse-all and disable-personalization controls.

## Adaptive difficulty
Only in explicitly selected Adaptive mode and within user-approved bounds. A small recent sample can suggest a change, never silently impose it. Use neutral language and offer practice/explanations instead of ability labels.

## Transparency/privacy
Explain recommendations in plain language (“Suggested because you selected business strategy”). Guest play and profile skipping supported. User can edit profile, disable personalization, export data and request deletion. When disabled, behavioral signals must not be read/applied.

## Acceptance
Blank profile can play; explicit choice wins; personalization-off ignores behavior; expired signals ignored; no sensitive attribute collection or inference.

## Age-aware presentation extension
Add an optional self-declared broad age band and age-appropriate presentation defaults as defined in docs/30-age-aware-personalized-ux.md. Do not infer age or use it as a proxy for ability. Age band may adjust reading complexity, navigation guidance and safety defaults only; learners can override presentation preferences. Apply jurisdiction-specific child privacy and guardian-control review before launch. Guest play remains supported where appropriate.


## Implementation constraint: deterministic only
All learner personalization is implemented using explicit profile/session preferences and deterministic rules. No LLM, agent, vector search or hidden learner-memory graph is consulted at runtime. The app may use relational profile preferences and opted-in progress records for transparent rules (for example, selected topic and difficulty range). Any AI-generated content or metadata is offline draft material only and cannot enter a published pack without human approval.
