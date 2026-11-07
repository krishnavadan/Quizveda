"""Create content and deterministic gameplay core.

Revision ID: 0001_content_gameplay_core
Revises:
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_content_gameplay_core"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "content_pack_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("pack_key", sa.String(120), nullable=False),
        sa.Column("version", sa.String(40), nullable=False),
        sa.Column("schema_version", sa.String(20), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("title", postgresql.JSONB(), nullable=False),
        sa.Column("manifest_sha256", sa.String(64), nullable=False),
        sa.Column("lifecycle_status", sa.String(20), nullable=False, server_default="validated"),
        sa.Column("approved_by", sa.String(120), nullable=True),
        sa.Column("approval_reference", sa.String(160), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("pack_key", "version", name="uq_pack_version"),
    )
    op.create_index("ix_content_pack_versions_pack_key", "content_pack_versions", ["pack_key"])
    op.create_table(
        "questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("question_key", sa.String(160), nullable=False, unique=True),
        sa.Column(
            "pack_version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content_pack_versions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
    )
    op.create_table(
        "question_revisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("questions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(16), nullable=False),
        sa.Column("answer_key_option_key", sa.String(12), nullable=False),
        sa.Column("estimated_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("approved", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.UniqueConstraint("question_id", "revision_no", name="uq_question_revision"),
        sa.CheckConstraint(
            "estimated_seconds BETWEEN 5 AND 600",
            name="ck_question_estimated_seconds",
        ),
    )
    op.create_table(
        "question_options",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "revision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("question_revisions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("option_key", sa.String(12), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("display_order", sa.Integer(), nullable=False),
        sa.UniqueConstraint("revision_id", "option_key", name="uq_revision_option_key"),
        sa.UniqueConstraint("revision_id", "display_order", name="uq_revision_option_order"),
    )
    op.create_table(
        "quiz_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("guest_session_hash", sa.String(64), nullable=False),
        sa.Column("pack_version_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("content_pack_versions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("mode", sa.String(24), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("selection_seed", sa.String(64), nullable=False),
        sa.Column("policy_version", sa.String(30), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("score >= 0", name="ck_session_score_nonnegative"),
        sa.CheckConstraint("current_position >= 0", name="ck_session_position_nonnegative"),
        sa.CheckConstraint("question_count > 0", name="ck_session_question_count_positive"),
    )
    op.create_table(
        "session_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("quiz_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "revision_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("question_revisions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="issued"),
        sa.Column("issued_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("deadline_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("session_id", "position", name="uq_session_question_position"),
        sa.UniqueConstraint("session_id", "revision_id", name="uq_session_question_revision"),
        sa.CheckConstraint("position > 0", name="ck_session_question_position"),
    )
    op.create_table(
        "answer_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_question_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("session_questions.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("idempotency_key", sa.String(100), nullable=False, unique=True),
        sa.Column("selected_option_key", sa.String(12), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("awarded_score", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "submitted_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint("awarded_score >= 0", name="ck_answer_awarded_score"),
    )


def downgrade() -> None:
    op.drop_table("answer_attempts")
    op.drop_table("session_questions")
    op.drop_table("quiz_sessions")
    op.drop_table("question_options")
    op.drop_table("question_revisions")
    op.drop_table("questions")
    op.drop_index("ix_content_pack_versions_pack_key", table_name="content_pack_versions")
    op.drop_table("content_pack_versions")
