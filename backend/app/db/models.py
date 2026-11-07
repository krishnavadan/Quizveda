from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    Uuid,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ContentPackVersion(Base):
    __tablename__ = "content_pack_versions"
    __table_args__ = (UniqueConstraint("pack_key", "version", name="uq_pack_version"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    pack_key: Mapped[str] = mapped_column(String(120), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(40), nullable=False)
    schema_version: Mapped[str] = mapped_column(String(20), nullable=False)
    locale: Mapped[str] = mapped_column(String(16), nullable=False)
    title: Mapped[dict] = mapped_column(JSONB, nullable=False)
    manifest_sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    lifecycle_status: Mapped[str] = mapped_column(String(20), nullable=False, default="validated")
    approved_by: Mapped[str | None] = mapped_column(String(120))
    approval_reference: Mapped[str | None] = mapped_column(String(160))
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    questions: Mapped[list["Question"]] = relationship(back_populates="pack_version")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    question_key: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    pack_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("content_pack_versions.id", ondelete="RESTRICT"), nullable=False
    )
    pack_version: Mapped[ContentPackVersion] = relationship(back_populates="questions")
    revisions: Mapped[list["QuestionRevision"]] = relationship(back_populates="question")


class QuestionRevision(Base):
    __tablename__ = "question_revisions"
    __table_args__ = (
        UniqueConstraint("question_id", "revision_no", name="uq_question_revision"),
        CheckConstraint(
            "estimated_seconds BETWEEN 5 AND 600",
            name="ck_question_estimated_seconds",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(
        ForeignKey("questions.id", ondelete="RESTRICT"), nullable=False
    )
    revision_no: Mapped[int] = mapped_column(Integer, nullable=False)
    locale: Mapped[str] = mapped_column(String(16), nullable=False)
    stem: Mapped[str] = mapped_column(String, nullable=False)
    explanation: Mapped[str] = mapped_column(String, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(16), nullable=False)
    answer_key_option_key: Mapped[str] = mapped_column(String(12), nullable=False)
    estimated_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=30)
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    question: Mapped[Question] = relationship(back_populates="revisions")
    options: Mapped[list["QuestionOption"]] = relationship(
        back_populates="revision", cascade="all, delete-orphan"
    )


class QuestionOption(Base):
    __tablename__ = "question_options"
    __table_args__ = (
        UniqueConstraint("revision_id", "option_key", name="uq_revision_option_key"),
        UniqueConstraint("revision_id", "display_order", name="uq_revision_option_order"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("question_revisions.id", ondelete="CASCADE"), nullable=False
    )
    option_key: Mapped[str] = mapped_column(String(12), nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[QuestionRevision] = relationship(back_populates="options")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    __table_args__ = (
        CheckConstraint("score >= 0", name="ck_session_score_nonnegative"),
        CheckConstraint("current_position >= 0", name="ck_session_position_nonnegative"),
        CheckConstraint("question_count > 0", name="ck_session_question_count_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    guest_session_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    pack_version_id: Mapped[UUID] = mapped_column(
        ForeignKey("content_pack_versions.id", ondelete="RESTRICT"), nullable=False
    )
    mode: Mapped[str] = mapped_column(String(24), nullable=False)
    locale: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    question_count: Mapped[int] = mapped_column(Integer, nullable=False)
    selection_seed: Mapped[str] = mapped_column(String(64), nullable=False)
    policy_version: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SessionQuestion(Base):
    __tablename__ = "session_questions"
    __table_args__ = (
        UniqueConstraint("session_id", "position", name="uq_session_question_position"),
        UniqueConstraint("session_id", "revision_id", name="uq_session_question_revision"),
        CheckConstraint("position > 0", name="ck_session_question_position"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_id: Mapped[UUID] = mapped_column(
        ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=False
    )
    revision_id: Mapped[UUID] = mapped_column(
        ForeignKey("question_revisions.id", ondelete="RESTRICT"), nullable=False
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="issued")
    issued_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deadline_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class AnswerAttempt(Base):
    __tablename__ = "answer_attempts"
    __table_args__ = (CheckConstraint("awarded_score >= 0", name="ck_answer_awarded_score"),)

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True, default=uuid4)
    session_question_id: Mapped[UUID] = mapped_column(
        ForeignKey("session_questions.id", ondelete="RESTRICT"), unique=True, nullable=False
    )
    idempotency_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    selected_option_key: Mapped[str] = mapped_column(String(12), nullable=False)
    outcome_status: Mapped[str] = mapped_column(String(16), nullable=False, default="answered")
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    awarded_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
