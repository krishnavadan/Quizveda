# 30. Age-Aware, Profile-Driven UX and Inclusive Design

## Objective
One coherent product with age-appropriate presentation and learning support, not separate quality tiers. Adaptation is transparent, optional and reversible.

## Optional profile inputs
Self-declared broad age band, learning stage, interests, selected subjects, preferred language, reading complexity, accessibility preferences and interaction style. Guardian-managed settings may apply to child accounts where appropriate. Prefer age bands over exact date of birth unless a separately reviewed requirement exists.

Never infer age from behavior, voice, appearance, name or device. Never infer disability or sensitive traits. Current-session choices override saved preferences.

## Starting age-band defaults
| Age band | UX emphasis | Pedagogy emphasis |
|---|---|---|
| 6–8 | simple navigation, large controls, short sessions, read-aloud | concrete language, visual examples, foundations |
| 9–12 | guided instructions, clear progress, optional hints | curiosity, age-appropriate challenge and explanations |
| 13–15 | more control, calm visual design, clear feedback | conceptual depth, practical examples, media literacy |
| 16–17 | configurable challenge and topic pathways | reasoning and applied knowledge |
| 18–24 | efficient discovery, mobile-first | breadth, skill-building and real-world scenarios |
| 25–44 | flexible time, resume and goals | practical contexts where selected |
| 45–59 | adjustable density and readability | relevance and refresh learning |
| 60+ | adjustable text, clear navigation, low-friction controls | same advanced depth; no assumptions |

These are starting defaults, not stereotypes or limits. Users can choose a different reading level, pace and interface density.

## Child-oriented safeguards
Use age-appropriate content filters and stricter defaults. Avoid public profiles, open chat, direct messaging, targeted advertising and public leaderboards by default. Provide guardian controls and age-appropriate privacy explanations where required. Review account, consent, retention and deletion flows for each jurisdiction. Avoid manipulative streaks, shame language and excessive-use mechanics.

Guest play remains available where legally and operationally appropriate. Collect only what is necessary.

## Adaptive interface
Profile may set defaults for typography, line spacing, content density, reading complexity, navigation guidance, motion, audio/read-aloud, contrast, timer presentation and hint depth. Users can change each independently. Never lower factual accuracy or hide important information based on age.

## Accessibility and research
Target WCAG 2.2 AA: keyboard, screen readers, visible focus, zoom/reflow, reduced motion, contrast, non-colour status, captions/transcripts and error recovery. Test representative users across ages with appropriate consent. Measure comprehension, task success, mis-taps, reading burden, safety and recovery. Age is not a proxy for ability.


## Deterministic implementation requirement
Age-band presentation and personalization are driven only by self-declared, consent-appropriate profile settings and deterministic UI rules. No AI inference, age estimation, learner-facing AI assistant or runtime model-generated content is permitted. All content variations must be pre-reviewed and published in versioned packs.
