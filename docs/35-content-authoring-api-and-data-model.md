# Content Authoring API and Data Model Blueprint

Companion: docs/34-versioned-question-authoring-and-revision-governance.md

## Proposed relational model

Use PostgreSQL UUID primary keys, timezone-aware timestamps, explicit foreign keys and bounded JSONB structures.

### authoring_workspaces
- id UUID primary key
- workspace_key varchar(120), unique
- title JSONB, locale varchar(16)
- status varchar(24), default draft
- lock_version bigint, default 1
- created_by, updated_by varchar(255)
- created_at, updated_at timestamptz
- released_pack_version_id UUID nullable, unique FK to content_pack_versions

### workspace_questions
- id UUID primary key
- workspace_id UUID FK, on delete restrict
- question_key varchar(160)
- current_revision_id UUID nullable FK to workspace_question_revisions
- is_tombstoned boolean, default false
- created_at timestamptz
- unique(workspace_id, question_key)

### workspace_question_revisions
- id UUID primary key
- workspace_question_id UUID FK, on delete restrict
- revision_no integer, positive
- locale, stem, explanation, difficulty
- answer_key_option_key, estimated_seconds
- options_json, taxonomy_json, cognitive_objectives_json, perspectives_json, provenance_json
- content_sha256 char(64)
- canonicalization_version varchar(20)
- author_subject varchar(255)
- created_at timestamptz
- unique(workspace_question_id, revision_no)

Revisions are insert-only.

### workspace_validation_runs
- id UUID primary key
- workspace_id UUID FK, on delete restrict
- snapshot_sha256 char(64)
- schema_version, validator_version varchar(40)
- status varchar(16)
- findings_json JSONB
- created_by varchar(255)
- created_at timestamptz
- unique(workspace_id, snapshot_sha256, validator_version)

### workspace_review_decisions
- id UUID primary key
- workspace_id UUID FK, on delete restrict
- validation_run_id UUID FK, on delete restrict
- snapshot_sha256 char(64)
- decision varchar(16): approved or rejected
- reviewer_subject varchar(255)
- reference varchar(160)
- rationale text, required for rejection
- created_at timestamptz

### authoring_idempotency_records
- id UUID primary key
- actor_subject varchar(255)
- idempotency_key_hash char(64)
- request_sha256 char(64)
- response_json JSONB
- created_at timestamptz
- unique(actor_subject, idempotency_key_hash)

## Revision payload

Editable request fields only: locale, type=single_choice, stem, options with stable key/text/display_order, answer_key.option_key, explanation, difficulty, estimated_seconds, taxonomy, cognitive_objectives, perspectives and provenance.

Reject unknown fields. Never accept approval/publication flags, revision number, author, timestamps, hashes, workspace ID or lifecycle status from the client. The server derives all of them.

## Error contract

Return a consistent envelope containing error code, message, correlation ID and safe details.

Required codes:
- workspace_not_found — 404
- workspace_not_editable — 409
- revision_conflict — 409
- idempotency_key_reused — 409
- validation_blocked — 422
- snapshot_changed — 409
- separation_of_duties_violation — 403
- release_artifact_verification_failed — 503

## Indexes and transaction strategy

Index workspaces by status/updated_at, questions by workspace/question_key, revisions by question/revision_no, and validation/decisions by workspace/created_at. Use FK RESTRICT for historical data.

For edits, use a short transaction with SELECT FOR UPDATE on workspace and question rows. Verify expected lock and revision values, append revision, update current pointer, increment workspace lock version, and persist idempotency and audit records in the same transaction. Never hold database locks during object-storage calls.

For release, use pending-release plus outbox/reconciliation if storage cannot join the database transaction. Make retries idempotent on snapshot hash and release ID.

## Rollout

1. Add authoring tables and indexes; do not alter gameplay tables.
2. Deploy API with authoring routes feature-disabled.
3. Existing imported packs remain read-only; no backfill is required.
4. Configure OIDC roles and test separation of duties.
5. Enable workspace creation/revision append for internal test users.
6. Enable validation/review only after RBAC and concurrency tests.
7. Enable release only after storage, retry/reconciliation and immutability tests.

## Observability

Measure workspace creation, revision append, stale-write conflicts, validation pass/fail, review rejection, approval-to-release latency, release retries and artifact verification failures. Avoid logging full question bodies, answer keys or tokens in general telemetry.
