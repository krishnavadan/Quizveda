# Question Selection and Perspective Engine

## Inputs and precedence
Inputs: mode, explicit taxonomy scope, locale, question count, difficulty policy, optional opted-in profile signals, published catalog snapshot, random session seed and policy version. Precedence: eligibility/safety → explicit topic → explicit difficulty/mode → diversity constraints → opted-in preferences → progress adaptation → seeded tie-break. Profile never overrides session choices.

## Eligibility
Only approved revisions in published pack versions; supported locale/question type; valid options/explanation/provenance; taxonomy in scope; not already selected; not blocked by repetition policy.

## Candidate score
`0.30 topic_fit + 0.20 difficulty_fit + 0.15 objective_fit + 0.15 perspective_fit + 0.10 learning_value + 0.10 freshness`. Normalize each factor to 0..1. Version weights in configuration and persist policy version with session.

## Perspective vocabulary
Learner, practitioner/operator, customer/user, leader, scientist/evidence analyst, historian/contextual observer, citizen/community, ethical observer, systems thinker, creator/designer. Perspective describes the framing lens, not an attribute of the player.

## Cognitive objectives
Remember, Understand, Apply, Analyze, Evaluate, Create. These are instructional tags, not validated psychometric measurements.

## Sequence constraints
No duplicate revision; stable seeded selection; option display order shuffled per session; Classic Ladder can progress Beginner→Standard→Advanced→Expert; Practice can hold fixed difficulty. Aim for 4 distinct perspectives and 3 cognitive objectives in a 10-question learning quiz when inventory supports it. Do not inject irrelevant items to meet diversity targets; return coverage warning if catalog is sparse.

## Pseudocode
1. Load versioned selection policy.
2. Filter catalog by publication, approval, locale, type and taxonomy scope.
3. Apply mode and difficulty rules.
4. Apply optional profile boosts only when enabled.
5. Remove session/user repeats according to retention rules.
6. Score candidates and sort with seeded deterministic tie-break.
7. Select next item satisfying hard constraints; fall back to core constraints if necessary.
8. Persist sequence, seed, pack version, policy version and coverage report.

## Adaptive mode
Only if explicitly selected. Example: last 5–10 attempts in topic; >=80% offer one level harder, 40–79% maintain, <40% offer practice/explanation or one level easier. Never silently alter fixed difficulty or label user ability.

## Acceptance
Same seed/snapshot/policy gives same sequence; explicit scope always honored; personalization-off equals no-profile selection; no duplicates; no future questions/answers exposed; shortage does not broaden scope silently.