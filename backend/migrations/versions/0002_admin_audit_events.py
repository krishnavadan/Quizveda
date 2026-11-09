"""Add immutable administrator audit events.

Revision ID: 0002_admin_audit_events
Revises: 0001_content_gameplay_core
"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_admin_audit_events"
down_revision = "0001_content_gameplay_core"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("actor_subject", sa.String(255), nullable=False),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("resource_type", sa.String(80), nullable=False),
        sa.Column("resource_id", sa.String(160), nullable=False),
        sa.Column("reference", sa.String(160), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.CheckConstraint(
            "action <> '' AND resource_type <> '' AND resource_id <> ''",
            name="ck_admin_audit_required_fields",
        ),
    )
    op.create_index("ix_admin_audit_events_actor_subject", "admin_audit_events", ["actor_subject"])
    op.create_index("ix_admin_audit_events_action", "admin_audit_events", ["action"])
    op.create_index("ix_admin_audit_events_resource_id", "admin_audit_events", ["resource_id"])
    op.create_index("ix_admin_audit_events_occurred_at", "admin_audit_events", ["occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_admin_audit_events_occurred_at", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_resource_id", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_action", table_name="admin_audit_events")
    op.drop_index("ix_admin_audit_events_actor_subject", table_name="admin_audit_events")
    op.drop_table("admin_audit_events")
