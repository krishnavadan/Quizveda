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
python -m app.modules.content.cli ../content/examples
```

The pack directory must contain `manifest.json` and the files referenced by its manifest. Validation checks JSON Schema, file hashes, byte/record counts, unique question keys and answer-option consistency. Validation does not constitute editorial approval or authorize publication.

## AI boundary

No AI SDK, model call, agent runtime or MCP server is used by this backend. Learner-facing behavior is deterministic and content-pack driven.
