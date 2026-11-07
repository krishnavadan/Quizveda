from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import SessionLocal
from app.db.models import AdminAuditEvent
from app.main import app
from app.modules.admin.security import AdminPrincipal, get_admin_principal
from app.modules.content.importer import import_pack

pytestmark = pytest.mark.asyncio


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _set_principal(subject: str, *roles: str) -> None:
    app.dependency_overrides[get_admin_principal] = lambda: AdminPrincipal(
        subject=subject,
        roles=frozenset(roles),
    )


async def test_admin_content_review_publish_and_audit_are_role_gated() -> None:
    root = _repo_root()
    pack_id = await import_pack(
        root / "content" / "examples" / "sample-pack",
        root / "content" / "schema",
    )
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            _set_principal("editor-1", "content_editor")
            listed = await client.get("/api/v1/admin/content-packs")
            assert listed.status_code == 200
            assert listed.json()["items"][0]["lifecycle_status"] == "validated"

            denied_approval = await client.post(
                f"/api/v1/admin/content-packs/{pack_id}/approve",
                json={"approval_reference": "REVIEW-001"},
            )
            assert denied_approval.status_code == 403

            _set_principal("reviewer-1", "content_reviewer")
            approved = await client.post(
                f"/api/v1/admin/content-packs/{pack_id}/approve",
                json={"approval_reference": "REVIEW-001"},
            )
            assert approved.status_code == 200
            assert approved.json()["lifecycle_status"] == "approved"
            assert approved.json()["approved_by"] == "reviewer-1"

            # The same reviewer cannot also publish their own approval.
            _set_principal("reviewer-1", "content_publisher")
            self_publish = await client.post(
                f"/api/v1/admin/content-packs/{pack_id}/publish",
                json={"approval_reference": "RELEASE-001"},
            )
            assert self_publish.status_code == 403

            _set_principal("publisher-1", "content_publisher")
            published = await client.post(
                f"/api/v1/admin/content-packs/{pack_id}/publish",
                json={"approval_reference": "RELEASE-002"},
            )
            assert published.status_code == 200
            assert published.json()["lifecycle_status"] == "published"

            _set_principal("publisher-1", "content_publisher")
            audit_denied = await client.get("/api/v1/admin/audit-events")
            assert audit_denied.status_code == 403

            _set_principal("security-admin", "admin")
            audit = await client.get("/api/v1/admin/audit-events")
            assert audit.status_code == 200
            actions = {item["action"] for item in audit.json()["items"]}
            assert actions == {"content_pack.approved", "content_pack.published"}
    finally:
        app.dependency_overrides.pop(get_admin_principal, None)

    async with SessionLocal() as db:
        events = (await db.scalars(__import__("sqlalchemy").select(AdminAuditEvent))).all()
        assert len(events) == 2


async def test_admin_content_detail_and_question_preview() -> None:
    root = _repo_root()
    pack_id = await import_pack(
        root / "content" / "examples" / "sample-pack",
        root / "content" / "schema",
        approval_actor="offline-reviewer",
        approval_reference="QA-IMPORT-01",
        publish=True,
    )
    transport = ASGITransport(app=app)
    try:
        _set_principal("content-operator", "content_editor")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            detail = await client.get(f"/api/v1/admin/content-packs/{pack_id}")
            assert detail.status_code == 200
            assert detail.json()["lifecycle_status"] == "published"
            questions = await client.get(
                f"/api/v1/admin/content-packs/{pack_id}/questions"
            )
            assert questions.status_code == 200
            item = questions.json()["items"][0]
            assert item["answer_key_option_key"] == "B"
            assert len(item["options"]) == 3
    finally:
        app.dependency_overrides.pop(get_admin_principal, None)
