# Versioned Question Authoring and Revision Governance

**Status:** implementation contract for the next authoring increment.

## Objective

Introduce browser-based question authoring without weakening the immutable content-pack release model. Editors create and revise questions; reviewers inspect exact revisions; publishers release only validated, approved snapshots.

## Non-negotiable invariants

1. Published pack versions and question revisions are immutable.
2. Every edit appends a new revision. Existing revisions are never overwritten.
3. A release freezes an exact set of question revision IDs and content hashes.
4. Approval applies to the exact snapshot hash, not a mutable workspace name.
5. Any edit after validation invalidates validation and approval eligibility for the changed snapshot.
6. The browser client cannot set approval, publication, author, timestamp, hash or audit fields.
7. All writes require authenticated roles, optimistic concurrency, idempotency and audit records.
8. Draft workspace tables are never queried by learner gameplay.
9. Answer keys are restricted to authorized content roles and never included in learner payloads.
10. AI assistance is offline and advisory; human review remains mandatory.

## Domain separation

Keep the existing release entities (ContentPackVersion, Question, QuestionRevision and QuestionOption) as immutable playback records. Add a separate authoring workspace domain:

- **AuthoringWorkspace:** mutable workspace for a future release; stable workspace key, locale, title, owner, status and lock version.
- **WorkspaceQuestion:** stable question identity within a workspace, with a current revision pointer.
- **WorkspaceQuestionRevision:** immutable authored revision containing learner-visible fields, answer key, taxonomy, objectives, perspectives, provenance, author subject, timestamp and canonical content hash.
- **WorkspaceValidationRun:** immutable validation result tied to one workspace snapshot hash and validator/schema version.
- **WorkspaceReviewDecision:** append-only reviewer decision tied to the exact snapshot and validation run.
- **WorkspaceRelease:** immutable record mapping the approved snapshot to a new ContentPackVersion and manifest hash.

Do not use published QuestionRevision rows as draft storage. Separate workspace tables prevent draft changes from leaking into gameplay queries.

## Lifecycle

Workspace lifecycle: draft → validation_pending → validated → review_pending → approved → released.

- Validation failure returns the workspace to draft with findings.
- Any content mutation after validation returns it to draft, creates a new snapshot hash and invalidates earlier validation/review eligibility.
- Reviewer rejection returns it to draft with a required rationale.
- Release is terminal for that snapshot. Further changes require a new snapshot and release version.
- Status is server-derived; clients cannot patch lifecycle state.

## Revision and concurrency

- New question starts at revision 1.
- Edit requests supply expected_revision_no and expected_workspace_lock_version.
- Server locks workspace/question rows, verifies both values, appends a revision and advances the current pointer.
- Stale writes return HTTP 409 with stable code revision_conflict and current revision metadata.
- Delete is a workspace tombstone; history is retained and released packs are unaffected.
- Restore appends a new revision from a historical revision; it never rewinds history.
- Every write requires an idempotency key. Same key and same request replays the original outcome; same key with a different body returns 409.

## Snapshot and hash contract

Canonicalization is deterministic and versioned: UTF-8 JSON, sorted object keys, normalized line endings, stable semantic array order, and exclusion of volatile fields such as timestamps and UI metadata.

Compute:
- Per-revision content_sha256.
- Workspace snapshot_sha256 from sorted active question keys and revision hashes plus workspace metadata.
- Release manifest SHA-256 from the exact generated manifest bytes.

Store the canonicalization algorithm version with every hash. Never compare hashes across canonicalization versions without an explicit migration.

## Validation layers

1. JSON Schema and field constraints.
2. Referential integrity: unique question keys/options, valid answer-key references and taxonomy references.
3. Pack integrity: locale consistency, counts, canonical hash and artifact checksums.
4. Deterministic editorial advisories, including existing short-stem/explanation and duplicate checks.
5. Provenance and rights completeness.
6. Human review for subject accuracy, answer correctness, age suitability, ambiguity, bias, language quality and accessibility.

Validation is not factual verification, legal clearance or bias certification. Blocking errors prevent approval; advisories require policy-defined acknowledgement.

## RBAC and separation of duties

| Capability | content_editor | content_reviewer | content_publisher | admin |
|---|---:|---:|---:|---:|
| Read workspace | Yes | Yes | Yes | Yes |
| Create/edit draft revisions | Yes | No | No | Yes |
| Validate snapshot | Yes | Yes | No | Yes |
| Approve exact snapshot | No | Yes | No | Yes |
| Release approved snapshot | No | No | Yes | Yes |
| Read audit trail | No | No | No | Yes |

A reviewer cannot approve a snapshot they authored. A non-admin publisher cannot release a snapshot they approved. Admin override is reason-required and separately audited. Roles come only from the trusted OIDC verifier.

## Required API contract

All routes are under /api/v1/admin.

| Method | Path | Purpose |
|---|---|---|
| POST | /authoring-workspaces | Create workspace |
| GET | /authoring-workspaces | List/filter workspaces |
| GET | /authoring-workspaces/{id} | Read workspace and lock version |
| PATCH | /authoring-workspaces/{id} | Update metadata with optimistic concurrency |
| POST | /authoring-workspaces/{id}/questions | Create question/revision 1 |
| GET | /authoring-workspaces/{id}/questions | List current question revisions |
| POST | /authoring-workspaces/{id}/questions/{question_id}/revisions | Append revision |
| GET | /authoring-workspaces/{id}/questions/{question_id}/revisions | Read immutable history |
| POST | /authoring-workspaces/{id}/questions/{question_id}/tombstone | Tombstone draft question |
| POST | /authoring-workspaces/{id}/validate | Freeze and validate snapshot |
| GET | /authoring-workspaces/{id}/validation-runs/{run_id} | Read immutable findings |
| POST | /authoring-workspaces/{id}/review-decisions | Approve/reject exact snapshot |
| POST | /authoring-workspaces/{id}/release | Materialize immutable pack version |
| GET | /authoring-workspaces/{id}/audit-events | Admin-only audit history |

Use strict Pydantic models, reject unknown fields, bound payload sizes and use stable error envelopes. Never implement generic PATCH over persistence models.

## Release materialization

1. Recompute snapshot hash and compare it with the approved hash.
2. Re-run blocking validation with the same schema/validator version.
3. Generate canonical manifest and JSONL artifacts at a temporary object key.
4. Verify bytes, record counts and SHA-256.
5. Create immutable pack version and question/revision/option records.
6. Commit as published only after durable artifact verification. If object storage and database cannot share a transaction, use pending-release/outbox state and idempotent reconciliation.
7. Emit audit event and release receipt with snapshot hash, manifest hash, validator version, reviewer and publisher identities.
8. Never overwrite an existing immutable release key.

## Audit and security

Audit workspace create/update, question create, revision append, tombstone/restore, validation, review, release, export and privileged override. Capture actor, action, resource IDs, before/after hashes, idempotency-key hash, reference, timestamp and correlation ID. Never store tokens or unnecessary personal data.

Require HTTPS, OIDC, MFA for privileged roles, rate limits, body limits, strict CORS, private object-storage writes and redacted logs. Authoring routes remain feature-disabled until migrations, authorization, concurrency, audit and end-to-end tests pass. Development agents never receive production credentials or learner data.

## Acceptance criteria

- Editors create workspaces and append immutable revisions.
- Concurrent stale writes return 409; no last-write-wins behavior.
- Idempotency is deterministic.
- Mutations change snapshot hash and invalidate prior validation/review eligibility.
- Reviewers approve only exact validated snapshots and cannot approve their own authored snapshots.
- Publishers release only exact approved snapshots and cannot release their own approval unless a reasoned admin override is audited.
- Release artifacts pass manifest and per-question hash verification.
- Gameplay remains isolated from workspace tables and serves only published approved releases.
- Post-release edits create a new release; historical releases remain unchanged.
- Tests cover RBAC, stale writes, idempotency, rollback, hash determinism, snapshot invalidation and release reconciliation.

## First-increment exclusions

Rich text, media upload, collaborative editing, comments, notifications, AI-generated question publishing, semantic duplicate detection and bulk browser import are excluded until core revision/release invariants are proven.
