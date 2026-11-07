"""Add isolated authoring workspaces and immutable question revisions.

Revision ID: 0003_authoring_workspaces
Revises: 0002_admin_audit_events
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_authoring_workspaces"
down_revision = "0002_admin_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "authoring_workspaces",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_key", sa.String(120), nullable=False),
        sa.Column("title", postgresql.JSONB(), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="draft"),
        sa.Column("lock_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", sa.String(255), nullable=False),
        sa.Column("updated_by", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("workspace_key", name="uq_authoring_workspace_key"),
        sa.CheckConstraint("lock_version > 0", name="ck_authoring_workspace_lock_version"),
    )
    op.create_index("ix_authoring_workspaces_status", "authoring_workspaces", ["status"])
    op.create_table(
        "workspace_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("authoring_workspaces.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("question_key", sa.String(160), nullable=False),
        sa.Column("current_revision_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("is_tombstoned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("workspace_id", "question_key", name="uq_workspace_question_key"),
    )
    op.create_index("ix_workspace_questions_workspace_id", "workspace_questions", ["workspace_id"])
    op.create_table(
        "workspace_question_revisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_question_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("workspace_questions.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("revision_no", sa.Integer(), nullable=False),
        sa.Column("locale", sa.String(16), nullable=False),
        sa.Column("stem", sa.Text(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(16), nullable=False),
        sa.Column("answer_key_option_key", sa.String(12), nullable=False),
        sa.Column("estimated_seconds", sa.Integer(), nullable=False, server_default="30"),
        sa.Column("options_json", postgresql.JSONB(), nullable=False),
        sa.Column("taxonomy_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("cognitive_objectives_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("perspectives_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("provenance_json", postgresql.JSONB(), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("content_sha256", sa.String(64), nullable=False),
        sa.Column("canonicalization_version", sa.String(20), nullable=False),
        sa.Column("author_subject", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("workspace_question_id", "revision_no", name="uq_workspace_question_revision"),
        sa.CheckConstraint("revision_no > 0", name="ck_workspace_revision_positive"),
        sa.CheckConstraint("estimated_seconds BETWEEN 5 AND 600", name="ck_workspace_estimated_seconds"),
    )
    op.create_index("ix_workspace_question_revisions_workspace_question_id", "workspace_question_revisions", ["workspace_question_id"])
    op.create_foreign_key(
        "fk_workspace_questions_current_revision",
        "workspace_questions",
        "workspace_question_revisions",
        ["current_revision_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    op.drop_constraint("fk_workspace_questions_current_revision", "workspace_questions", type_="foreignkey")
    op.drop_index("ix_workspace_question_revisions_workspace_question_id", table_name="workspace_question_revisions")
    op.drop_table("workspace_question_revisions")
    op.drop_index("ix_workspace_questions_workspace_id", table_name="workspace_questions")
    op.drop_table("workspace_questions")
    op.drop_index("ix_authoring_workspaces_status", table_name="authoring_workspaces")
    op.drop_table("authoring_workspaces")
