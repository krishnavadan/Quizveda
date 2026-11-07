# QuizVeda Backend

## Local setup

Requires Python 3.12+ and PostgreSQL 15+.

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

Set `DATABASE_URL=postgresql+asyncpg://...` in `.env`.

## Database migrations

```bash
alembic upgrade head
```

The first migration creates the minimal content-pack and gameplay persistence core. Review migrations before applying to any shared or production database.

## Run API and tests

```bash
uvicorn app.main:app --reload
pytest
```

Readiness performs a real database connectivity check. Liveness does not depend on external services.

## Offline content validation

From the repository root:

```bash
cd backend
python -m app.modules.content.cli ../content/examples/sample-pack
```

The pack directory must contain `manifest.json` and the files referenced by its manifest. Validation checks JSON Schema, file hashes, byte/record counts, unique question keys and answer-option consistency. Validation does not constitute editorial approval or authorize publication.

## AI boundary

No AI SDK, model call, agent runtime or MCP server is used by this backend. Learner-facing behavior is deterministic and content-pack driven.

## Import, approve and publish a pack

Validate before importing:

```bash
python -m app.modules.content.cli ../content/examples/sample-pack --schema-dir ../content/schema
```

Import as validated content (not playable):

```bash
python -m app.modules.content.importer ../content/examples/sample-pack --schema-dir ../content/schema
```

Approval and publication are explicit operator actions. The command records the supplied actor/reference; the values are an operational audit assertion, not an authentication mechanism. Restrict database credentials and command execution to authorized content operators.

```bash
python -m app.modules.content.importer ../content/examples/sample-pack \
  --schema-dir ../content/schema \
  --approval-actor "editor@example.org" \
  --approval-reference "CONTENT-REVIEW-001" \
  --publish
```

The production gameplay API selects only pack versions marked `published` and question revisions marked approved.

## Gameplay API

- `POST /api/v1/gameplay/sessions` — creates a guest session and returns a one-time bearer token plus the first question.
- `GET /api/v1/gameplay/sessions/{session_id}/current` — retrieves the current question using the guest bearer token.
- `POST /api/v1/gameplay/sessions/{session_id}/answers` — submits `question_id` and `selected_option_key`; requires an `Idempotency-Key` header.

The answer key is never returned. The server controls the question sequence, deadline, answer evaluation, score and progression. A stale question ID is rejected; retries with the same idempotency key replay the original outcome.


## Admin content API

The initial Admin CMS API is protected by provider-neutral OIDC access-token verification. Configure `OIDC_ISSUER`, `OIDC_AUDIENCE`, and `OIDC_JWKS_URL`; optionally set `OIDC_ROLES_CLAIM` (default `roles`). The identity provider must issue RS256-signed API access tokens with the configured issuer/audience and role claims. Admin routes fail closed until configured.

Content import creates validated drafts only. Reviewers approve packs and publishers publish them through separate role-gated API actions. See [Admin CMS security and content governance](../docs/32-admin-content-cms-and-rbac.md) for roles, endpoints, lifecycle, audit and production requirements.
