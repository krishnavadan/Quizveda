# QuizVeda — Master Product Requirements Document

**Version:** 1.0 · **Status:** Baseline for implementation · **Date:** 2026-11-08

## Vision
A profile-aware quiz and knowledge platform that combines the tension of progressive quiz rounds with meaningful learning, broad subject discovery and multi-perspective questions. The product has its own brand, question content, interaction design and sound identity.

## Product experiences
- **Play to Win:** progressive rounds, timer, score, lifelines and a final result.
- **Play to Learn:** practice, explanations, topic mastery and adaptive recommendations.
Shared content catalog, taxonomy and session engine.

## Audiences
Curious learners, students, professionals, educators and casual players. A profile is optional; guest play is supported. Profile data improves relevance but never limits subject access.

## Core capabilities
1. Guest and account-based play.
2. Optional profile: learning stage, broad occupation/experience band, goal, language, selected interests and accessibility preferences.
3. Subject/topic taxonomy and difficulty selection.
4. Multiple modes: Classic Ladder, Practice, Quick Quiz and Topic Challenge.
5. Single-player multiple-choice gameplay for MVP.
6. Server-side question delivery, timing, scoring, progression and lifelines.
7. Explanations and provenance after answer acceptance.
8. Session history and topic progress for signed-in users.
9. JSON content-pack upload, validation, review, publication and rollback.
10. Admin authoring, taxonomy, review queue, roles and audit.

## Question design
Tag questions by subject/topic, difficulty (Beginner/Standard/Advanced/Expert), cognitive objective (Remember, Understand, Apply, Analyze, Evaluate, Create), perspective (e.g. learner, practitioner, customer, leader, scientist, ethical observer, systems thinker), locale, provenance and review state.

## MVP boundaries
Single-player MCQ, responsive PWA, optional profile, deterministic selection, explanations, timer, score, a small set of lifelines, history, progress and content operations. Multiplayer, voice, open public authoring, cash prizes, wagering, high-stakes assessment and unreviewed runtime AI questions are out of scope.

## Product principles
- Explicit session choices outrank saved or inferred preferences.
- Personalization can be disabled; missing profile data uses generic defaults.
- Do not collect or infer sensitive traits.
- AI is optional and never required for normal gameplay.
- Content is versioned independently of application deployments.
- No copying KBC/Kaun Banega Crorepati branding, logo, music, host likeness, scripts, question bank or distinctive trade dress.

## Success measures
Activation (first completed session), completion rate, repeat play, explanation engagement, content quality, topic revisit, latency and reliability. Do not optimize solely for time spent or compulsive streak behavior.

## Acceptance
A guest can complete a game without a profile; explicit topic/difficulty is honored; one answer is accepted per question; the server calculates score; answer keys are not exposed before submission; content versions are immutable and rollbackable.

## Open decisions
Trademark/domain clearance, initial content catalog and licensing, launch locales, authentication provider, final scoring curve/lifelines, hosting and cost envelope, monetization and leaderboard scope.

## AI boundary (governing requirement)
AI is used only by internal product development and content-production workflows. No AI assistant, live generated question, model-generated explanation or runtime AI recommendation is included in the learner app. All learner-facing question content and explanations are reviewed and published as versioned content. Recommendations and difficulty adaptation use deterministic rules and explicit user-controlled profile/session inputs. Production gameplay must operate with no model credentials, AI SDK or AI network access.
