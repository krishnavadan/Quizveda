from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import func, select

from app.core.database import SessionLocal
from app.db.models import ContentPackVersion, Question, QuestionRevision, QuizSession
from app.main import app
from app.modules.content.importer import import_pack

pytestmark = pytest.mark.asyncio


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


async def _publish_fixture_pack(pack_id) -> None:
    async with SessionLocal() as db:
        pack = await db.get(ContentPackVersion, pack_id)
        assert pack is not None
        pack.lifecycle_status = "published"
        revisions = (
            await db.scalars(
                select(QuestionRevision)
                .join(Question, Question.id == QuestionRevision.question_id)
                .where(Question.pack_version_id == pack_id)
            )
        ).all()
        for revision in revisions:
            revision.approved = True
        await db.commit()


async def test_import_creates_validated_draft_and_duplicate_import_is_atomic() -> None:
    root = _repo_root()
    pack_dir = root / "content" / "examples" / "sample-pack"
    schema_dir = root / "content" / "schema"
    pack_id = await import_pack(pack_dir, schema_dir)

    with pytest.raises(ValueError, match="already been imported"):
        await import_pack(pack_dir, schema_dir)

    async with SessionLocal() as db:
        pack = await db.get(ContentPackVersion, pack_id)
        count = await db.scalar(select(func.count()).select_from(ContentPackVersion))
    assert pack is not None
    assert pack.lifecycle_status == "validated"
    assert pack.approved_by is None
    assert pack.published_at is None
    assert count == 1


async def test_guest_gameplay_answer_idempotency_and_token_boundary() -> None:
    root = _repo_root()
    pack_id = await import_pack(
        root / "content" / "examples" / "sample-pack",
        root / "content" / "schema",
    )
    # Test fixture simulates content that passed the separately tested admin workflow.
    await _publish_fixture_pack(pack_id)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/api/v1/gameplay/sessions",
            json={
                "pack_key": "general-science",
                "version": "1.0.0",
                "locale": "en-IN",
                "mode": "play_to_learn",
                "question_count": 1,
            },
        )
        assert created.status_code == 201
        session_data = created.json()
        session_id = session_data["session_id"]
        token = session_data["guest_token"]
        question = session_data["question"]
        assert "answer_key" not in question
        assert len(question["options"]) == 3

        unauthenticated = await client.get(
            f"/api/v1/gameplay/sessions/{session_id}/current"
        )
        assert unauthenticated.status_code == 401

        headers = {
            "Authorization": f"Bearer {token}",
            "Idempotency-Key": "ci-answer-0001",
        }
        answer_payload = {
            "question_id": question["question_id"],
            "selected_option_key": "B",
        }
        answered = await client.post(
            f"/api/v1/gameplay/sessions/{session_id}/answers",
            json=answer_payload,
            headers=headers,
        )
        assert answered.status_code == 200
        result = answered.json()
        assert result["is_correct"] is True
        assert result["score_delta"] == 100
        assert result["total_score"] == 100
        assert result["replayed"] is False

        replayed = await client.post(
            f"/api/v1/gameplay/sessions/{session_id}/answers",
            json=answer_payload,
            headers=headers,
        )
        assert replayed.status_code == 200
        assert replayed.json()["replayed"] is True
        assert replayed.json()["total_score"] == 100

        current = await client.get(
            f"/api/v1/gameplay/sessions/{session_id}/current",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert current.status_code == 200
        assert current.json()["status"] == "completed"

    async with SessionLocal() as db:
        session = await db.get(QuizSession, session_id)
        assert session is not None
        assert session.score == 100
        assert session.status == "completed"
