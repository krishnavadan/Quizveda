from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

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
        events = (await db.scalars(select(AdminAuditEvent))).all()
        assert len(events) == 2


async def test_admin_content_detail_and_question_preview() -> None:
    root = _repo_root()
    pack_id = await import_pack(
        root / "content" / "examples" / "sample-pack",
        root / "content" / "schema",
    )
    transport = ASGITransport(app=app)
    try:
        _set_principal("content-operator", "content_editor")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            detail = await client.get(f"/api/v1/admin/content-packs/{pack_id}")
            assert detail.status_code == 200
            assert detail.json()["lifecycle_status"] == "validated"
            questions = await client.get(
                f"/api/v1/admin/content-packs/{pack_id}/questions"
            )
            assert questions.status_code == 200
            item = questions.json()["items"][0]
            assert item["answer_key_option_key"] == "B"
            assert len(item["options"]) == 3
    finally:
        app.dependency_overrides.pop(get_admin_principal, None)


async def test_content_quality_report_is_advisory_and_role_gated() -> None:
    root = _repo_root()
    pack_id = await import_pack(
        root / "content" / "examples" / "sample-pack",
        root / "content" / "schema",
    )
    transport = ASGITransport(app=app)
    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            _set_principal("unauthorised", "learner")
            denied = await client.get(
                f"/api/v1/admin/content-packs/{pack_id}/quality-report"
            )
            assert denied.status_code == 403

            _set_principal("editor-quality", "content_editor")
            response = await client.get(
                f"/api/v1/admin/content-packs/{pack_id}/quality-report"
            )
            assert response.status_code == 200
            report = response.json()
            assert report["pack_id"] == str(pack_id)
            assert report["question_count"] == 1
            assert isinstance(report["findings"], list)
            assert "do not replace" in report["disclaimer"]
    finally:
        app.dependency_overrides.pop(get_admin_principal, None)



async def test_authoring_workspace_revision_history_and_stale_write_conflict() -> None:
    transport = ASGITransport(app=app)
    workspace_payload = {
        "workspace_key": "general-knowledge-en",
        "title": {"en": "General Knowledge"},
        "locale": "en",
    }
    revision = {
        "locale": "en",
        "stem": "Which planet is known as the Red Planet?",
        "explanation": "Mars appears red because iron minerals on its surface have oxidized.",
        "difficulty": "beginner",
        "answer_key_option_key": "B",
        "estimated_seconds": 20,
        "options": [
            {"key": "A", "text": "Venus", "display_order": 1},
            {"key": "B", "text": "Mars", "display_order": 2},
            {"key": "C", "text": "Jupiter", "display_order": 3},
        ],
        "taxonomy": [{"node_key": "science.astronomy", "weight": 1}],
        "cognitive_objectives": ["remember"],
        "perspectives": [],
        "provenance": {"rights_status": "original"},
    }
    try:
        _set_principal("author-1", "content_editor")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            created = await client.post(
                "/api/v1/admin/authoring-workspaces",
                json=workspace_payload,
            )
            assert created.status_code == 200
            workspace = created.json()
            workspace_id = workspace["id"]
            assert workspace["status"] == "draft"
            assert workspace["lock_version"] == 1

            question = await client.post(
                f"/api/v1/admin/authoring-workspaces/{workspace_id}/questions",
                json={
                    "question_key": "science.red-planet",
                    "expected_workspace_lock_version": 1,
                    "revision": revision,
                },
            )
            assert question.status_code == 200
            first = question.json()
            assert first["revision_no"] == 1
            assert first["workspace_lock_version"] == 2
            assert len(first["content_sha256"]) == 64

            revised_payload = {
                **revision,
                "explanation": "Mars looks red due to iron oxide, commonly called rust, on its surface.",
                "expected_revision_no": 1,
                "expected_workspace_lock_version": 2,
            }
            revised = await client.post(
                f"/api/v1/admin/authoring-workspaces/{workspace_id}/questions/{first['question_id']}/revisions",
                json=revised_payload,
            )
            assert revised.status_code == 200
            second = revised.json()
            assert second["revision_no"] == 2
            assert second["workspace_lock_version"] == 3
            assert second["content_sha256"] != first["content_sha256"]

            stale = await client.post(
                f"/api/v1/admin/authoring-workspaces/{workspace_id}/questions/{first['question_id']}/revisions",
                json=revised_payload,
            )
            assert stale.status_code == 409

            listed = await client.get("/api/v1/admin/authoring-workspaces")
            assert listed.status_code == 200
            assert any(item["id"] == workspace_id for item in listed.json()["items"])
    finally:
        app.dependency_overrides.pop(get_admin_principal, None)


async def test_authoring_rejects_unknown_fields_and_non_editor_roles() -> None:
    transport = ASGITransport(app=app)
    try:
        _set_principal("learner-user", "learner")
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            denied = await client.post(
                "/api/v1/admin/authoring-workspaces",
                json={
                    "workspace_key": "sample-workspace",
                    "title": {"en": "Sample"},
                    "locale": "en",
                    "status": "published",
                },
            )
            assert denied.status_code == 403

            _set_principal("editor-user", "content_editor")
            rejected = await client.post(
                "/api/v1/admin/authoring-workspaces",
                json={
                    "workspace_key": "sample-workspace",
                    "title": {"en": "Sample"},
                    "locale": "en",
                    "status": "published",
                },
            )
            assert rejected.status_code == 422
    finally:
        app.dependency_overrides.pop(get_admin_principal, None)
