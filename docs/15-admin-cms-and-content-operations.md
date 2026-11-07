# Admin CMS and Content Operations

## Modules
Dashboard; taxonomy manager; question editor; bulk JSON/JSONL import; dry-run validator; review queue; revision comparison; pack/version manager; staging preview; production publish/rollback; configuration; support tools; audit viewer.

## Roles
Author, Reviewer, Publisher, Support and Admin. Apply least privilege and separation of duties. Production publish requires publisher scope. Support data access is limited, time-bound and audited.

## Question editor
Autosave draft, immutable revision on approval, preview mobile/desktop, edit stem/options/explanation/difficulty/objectives/perspectives/taxonomy/locale/provenance, compare revisions and warn when published content requires a new pack version.

## Import
Select pack/locale → upload → detect schema/count → dry validation → download error report → confirm import to draft → route to review. Idempotent on pack/version/checksum.

## Audit
Record answer-key edits, review decisions, publish/rollback, permission changes, data access and deletion. Never log passwords, tokens or secrets.