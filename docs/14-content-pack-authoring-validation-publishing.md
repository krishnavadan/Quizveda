# Content Pack Authoring, Validation and Publishing

## Pack layout
`manifest.json`, `taxonomy.json`, question JSON/JSONL shards, assets and source register. Manifest includes pack key/version, schema version, locale, taxonomy scope, counts, file sizes, SHA-256 checksums, publisher and provenance.

## Lifecycle
draft → uploaded → validating → validated → in_review → approved → published → retired. Rejected packs return to draft with record-level remediation. Published bytes immutable; correction creates new version.

## Validation
Structural: JSON parse/schema, required fields, unique IDs, supported locale/enums. Semantic: exactly one correct option, answer key points to an existing option, plausible distractors, no duplicate option text, explanation, valid difficulty/objective/perspective/taxonomy and time bounds. Editorial: clarity, factual source/date, rights status, language/cultural QA and human approval. Operational: checksum, size/type limits, malware scan, no executable HTML.

## Publish workflow
Upload to quarantine → verify checksum/type → validate → editorial review → approve → store immutable approved object → write version metadata → atomically update environment pointer → invalidate affected CDN paths → emit event. Keep prior version for rollback. Never publish answer keys in public CDN objects.

## Rollback
Switch active pointer to previous approved version; do not mutate historical bytes. Existing sessions stay pinned. Audit actor, reason and before/after pointer.

## Roles
Author drafts; reviewer reviews and cannot approve own production pack; publisher releases; admin manages policy/roles and emergency rollback.