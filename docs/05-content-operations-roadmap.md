# Content Operations and Roadmap

## Content taxonomy
Subject → Domain → Topic → Subtopic, with separate skill tags. Each node has stable key, localized label/description, parent, lifecycle status and sort order.

## Question metadata
Stable question key, revision, locale, stem, options, protected answer key, explanation, difficulty, estimated time, taxonomy tags, cognitive objectives, perspectives, source/provenance, rights status, author/reviewer and lifecycle.

## Quality bar
Unambiguous stem; one correct answer for single-choice; plausible distractors; no grammatical or visual clue leakage; factual source and date where relevant; rights-cleared content; human review; locale QA.

## Pack pipeline
Versioned manifest and JSON/JSONL files → checksum/type checks → JSON Schema validation → semantic validation → editorial review → approval → staging preview → atomic publication → CDN invalidation where needed → monitoring. Rollback to immutable prior version.

## Roadmap
Phase 0: product and content governance. Phase 1: playable single-player MVP and initial catalog. Phase 2: learning progress, multilingual content and educator tools. Phase 3: multiplayer/social features only after abuse/privacy review. Phase 4: optional AI-assisted authoring with human approval.

## Content governance
Maintain source register, rights evidence, review date, question status and reviewer identity. Retire unsafe, outdated or ambiguous items. Never silently alter historical question revisions.