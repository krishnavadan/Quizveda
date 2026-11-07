import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db_session
from app.db.models import (
    AnswerAttempt,
    ContentPackVersion,
    Question,
    QuestionRevision,
    QuizSession,
    SessionQuestion,
)
from app.modules.gameplay.domain import evaluate_option_answer
from app.modules.gameplay.selection import CandidateQuestion, select_questions

router = APIRouter(prefix="/gameplay", tags=["gameplay"])
bearer = HTTPBearer(auto_error=False)
DbSession = Annotated[AsyncSession, Depends(get_db_session)]


class CreateSessionRequest(BaseModel):
    pack_key: str = Field(min_length=3, max_length=120)
    version: str = Field(min_length=1, max_length=40)
    locale: str = Field(min_length=2, max_length=16)
    mode: Literal["play_to_win", "play_to_learn"] = "play_to_learn"
    question_count: int = Field(default=10, ge=1, le=50)
    difficulty: Literal["beginner", "standard", "advanced", "expert"] | None = None
    taxonomy_scope: list[str] = Field(default_factory=list, max_length=20)


class SubmitAnswerRequest(BaseModel):
    question_id: UUID
    selected_option_key: str = Field(min_length=1, max_length=12)


def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


async def _owned_session(
    db: AsyncSession,
    session_id: UUID,
    credentials: HTTPAuthorizationCredentials | None,
    *,
    lock: bool = False,
) -> QuizSession:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Guest session token required.")
    statement = select(QuizSession).where(QuizSession.id == session_id)
    if lock:
        statement = statement.with_for_update()
    session = await db.scalar(statement)
    if session is None or not secrets.compare_digest(
        session.guest_session_hash, _token_hash(credentials.credentials)
    ):
        raise HTTPException(status_code=404, detail="Session not found.")
    return session


async def _current_question(db: AsyncSession, session: QuizSession) -> dict:
    while session.status == "active" and session.current_position < session.question_count:
        position = session.current_position + 1
        issued = await db.scalar(
            select(SessionQuestion).where(
                SessionQuestion.session_id == session.id,
                SessionQuestion.position == position,
            )
        )
        if issued is None:
            raise HTTPException(status_code=500, detail="Session question sequence is incomplete.")

        revision = await db.scalar(
            select(QuestionRevision)
            .options(selectinload(QuestionRevision.options))
            .where(QuestionRevision.id == issued.revision_id)
        )
        if revision is None:
            raise HTTPException(status_code=500, detail="Question content is unavailable.")

        now = datetime.now(timezone.utc)
        if issued.issued_at is None:
            issued.status = "issued"
            issued.issued_at = now
            issued.deadline_at = now + timedelta(seconds=revision.estimated_seconds)
            await db.commit()
        elif issued.deadline_at and now > issued.deadline_at:
            issued.status = "timed_out"
            session.current_position += 1
            if session.current_position >= session.question_count:
                session.status = "completed"
            await db.commit()
            continue

        return {
            "status": "active",
            "question_id": str(issued.id),
            "position": issued.position,
            "stem": revision.stem,
            "options": [
                {"key": option.option_key, "text": option.text}
                for option in sorted(revision.options, key=lambda item: item.display_order)
            ],
            "time_limit_seconds": revision.estimated_seconds,
            "deadline_at": issued.deadline_at.isoformat() if issued.deadline_at else None,
        }

    return {
        "status": "completed",
        "score": session.score,
        "question_count": session.question_count,
    }


@router.post("/sessions", status_code=201)
async def create_session(payload: CreateSessionRequest, db: DbSession) -> dict:
    pack = await db.scalar(
        select(ContentPackVersion).where(
            ContentPackVersion.pack_key == payload.pack_key,
            ContentPackVersion.version == payload.version,
            ContentPackVersion.lifecycle_status == "published",
        )
    )
    if pack is None:
        raise HTTPException(status_code=404, detail="Published content pack version not found.")

    rows = (
        await db.execute(
            select(QuestionRevision, Question)
            .join(Question, Question.id == QuestionRevision.question_id)
            .options(selectinload(QuestionRevision.options))
            .where(
                Question.pack_version_id == pack.id,
                QuestionRevision.locale == payload.locale,
                QuestionRevision.approved.is_(True),
            )
        )
    ).all()

    candidates: list[CandidateQuestion] = []
    by_key: dict[str, QuestionRevision] = {}
    scope = frozenset(payload.taxonomy_scope)
    for revision, question in rows:
        taxonomy = frozenset(
            item.get("node_key")
            for item in revision.metadata_json.get("taxonomy", [])
            if isinstance(item, dict) and isinstance(item.get("node_key"), str)
        )
        topic_fit = len(taxonomy & scope) / len(scope) if scope else 1.0
        candidates.append(
            CandidateQuestion(
                question_key=question.question_key,
                locale=revision.locale,
                difficulty=revision.difficulty,
                taxonomy_keys=taxonomy,
                topic_fit=topic_fit,
            )
        )
        by_key[question.question_key] = revision

    seed = secrets.token_hex(32)
    selected = select_questions(
        candidates,
        count=payload.question_count,
        locale=payload.locale,
        taxonomy_scope=scope,
        difficulty=payload.difficulty,
        seed=seed,
    )
    if len(selected) != payload.question_count:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "Not enough published questions satisfy the requested scope.",
                "available_count": len(selected),
            },
        )

    guest_token = secrets.token_urlsafe(32)
    session = QuizSession(
        guest_session_hash=_token_hash(guest_token),
        pack_version_id=pack.id,
        mode=payload.mode,
        locale=payload.locale,
        status="active",
        score=0,
        current_position=0,
        question_count=payload.question_count,
        selection_seed=seed,
        policy_version="1.0",
    )
    db.add(session)
    await db.flush()

    for position, candidate in enumerate(selected, start=1):
        revision = by_key[candidate.question_key]
        db.add(
            SessionQuestion(
                session_id=session.id,
                revision_id=revision.id,
                position=position,
                status="queued",
            )
        )
    await db.commit()
    first_question = await _current_question(db, session)
    return {
        "session_id": str(session.id),
        "guest_token": guest_token,
        "mode": session.mode,
        "question_count": session.question_count,
        "question": first_question,
    }


@router.get("/sessions/{session_id}/current")
async def get_current_question(
    session_id: UUID,
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> dict:
    session = await _owned_session(db, session_id, credentials, lock=True)
    return await _current_question(db, session)


@router.post("/sessions/{session_id}/answers")
async def submit_answer(
    session_id: UUID,
    payload: SubmitAnswerRequest,
    db: DbSession,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    idempotency_key: Annotated[str, Header(alias="Idempotency-Key", min_length=8, max_length=100)],
) -> dict:
    session = await _owned_session(db, session_id, credentials, lock=True)

    existing = await db.execute(
        select(AnswerAttempt, SessionQuestion)
        .join(SessionQuestion, SessionQuestion.id == AnswerAttempt.session_question_id)
        .where(AnswerAttempt.idempotency_key == idempotency_key)
    )
    prior = existing.first()
    if prior:
        attempt, prior_question = prior
        if (
            prior_question.session_id != session.id
            or attempt.selected_option_key != payload.selected_option_key
            or prior_question.id != payload.question_id
        ):
            raise HTTPException(status_code=409, detail="Idempotency key was already used.")
        if attempt.outcome_status == "timed_out":
            return {
                "status": "timed_out",
                "total_score": session.score,
                "next_question_available": session.status == "active",
                "replayed": True,
            }
        revision = await db.get(QuestionRevision, prior_question.revision_id)
        return {
            "status": "answered",
            "is_correct": attempt.is_correct,
            "score_delta": attempt.awarded_score,
            "total_score": session.score,
            "explanation": revision.explanation if revision else "",
            "next_question_available": session.status == "active",
            "replayed": True,
        }

    if session.status != "active" or session.current_position >= session.question_count:
        raise HTTPException(status_code=409, detail="Session is not accepting answers.")

    position = session.current_position + 1
    issued = await db.scalar(
        select(SessionQuestion)
        .where(
            SessionQuestion.session_id == session.id,
            SessionQuestion.position == position,
        )
        .with_for_update()
    )
    if issued is None:
        raise HTTPException(status_code=409, detail="No current question is available.")
    if issued.id != payload.question_id:
        raise HTTPException(status_code=409, detail="Submitted question is no longer current.")

    revision = await db.scalar(
        select(QuestionRevision)
        .options(selectinload(QuestionRevision.options))
        .where(QuestionRevision.id == issued.revision_id)
    )
    if revision is None:
        raise HTTPException(status_code=500, detail="Question content is unavailable.")

    valid_options = {option.option_key for option in revision.options}
    if payload.selected_option_key not in valid_options:
        raise HTTPException(status_code=422, detail="Selected option is not valid for this question.")

    now = datetime.now(timezone.utc)
    if issued.deadline_at is None or issued.issued_at is None:
        raise HTTPException(status_code=409, detail="Question has not been issued.")
    if now > issued.deadline_at:
        db.add(
            AnswerAttempt(
                session_question_id=issued.id,
                idempotency_key=idempotency_key,
                selected_option_key=payload.selected_option_key,
                outcome_status="timed_out",
                is_correct=False,
                awarded_score=0,
            )
        )
        issued.status = "timed_out"
        session.current_position += 1
        if session.current_position >= session.question_count:
            session.status = "completed"
        await db.commit()
        return {
            "status": "timed_out",
            "total_score": session.score,
            "next_question_available": session.status == "active",
            "replayed": False,
        }

    outcome = evaluate_option_answer(
        selected_option_key=payload.selected_option_key,
        correct_option_key=revision.answer_key_option_key,
        correct_score=100,
        incorrect_score=0,
        explanation=revision.explanation,
    )
    is_correct = outcome.is_correct
    score_delta = outcome.score_delta
    db.add(
        AnswerAttempt(
            session_question_id=issued.id,
            idempotency_key=idempotency_key,
            selected_option_key=payload.selected_option_key,
            outcome_status="answered",
            is_correct=is_correct,
            awarded_score=score_delta,
        )
    )
    issued.status = "answered"
    session.score += score_delta
    session.current_position += 1
    if session.current_position >= session.question_count:
        session.status = "completed"
    await db.commit()

    return {
        "status": "answered",
        "is_correct": is_correct,
        "score_delta": score_delta,
        "total_score": session.score,
        "explanation": revision.explanation,
        "next_question_available": session.status == "active",
        "replayed": False,
    }
