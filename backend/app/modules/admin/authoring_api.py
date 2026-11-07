import hashlib
import json
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.db.models import (
    AdminAuditEvent,
    AuthoringWorkspace,
    WorkspaceQuestion,
    WorkspaceQuestionRevision,
)
from app.modules.admin.security import AdminPrincipal, require_roles

router = APIRouter(prefix="/admin/authoring-workspaces", tags=["admin-authoring"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CanEditContent = Annotated[AdminPrincipal, Depends(require_roles("content_editor"))]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WorkspaceCreate(StrictModel):
    workspace_key: str = Field(min_length=3, max_length=120, pattern=r"^[a-z0-9][a-z0-9-]+$")
    title: dict[str, str] = Field(min_length=1)
    locale: str = Field(min_length=2, max_length=16)


class OptionInput(StrictModel):
    key: str = Field(min_length=1, max_length=12)
    text: str = Field(min_length=1, max_length=1000)
    display_order: int = Field(ge=1, le=6)


class QuestionRevisionInput(StrictModel):
    locale: str = Field(min_length=2, max_length=16)
    stem: str = Field(min_length=8, max_length=5000)
    explanation: str = Field(min_length=1, max_length=10000)
    difficulty: str = Field(pattern=r"^(beginner|standard|advanced|expert)$")
    answer_key_option_key: str = Field(min_length=1, max_length=12)
    estimated_seconds: int = Field(default=30, ge=5, le=600)
    options: list[OptionInput] = Field(min_length=2, max_length=6)
    taxonomy: list[dict] = Field(default_factory=list, max_length=30)
    cognitive_objectives: list[str] = Field(default_factory=list, max_length=6)
    perspectives: list[dict] = Field(default_factory=list, max_length=20)
    provenance: dict = Field(default_factory=dict)


class QuestionCreate(StrictModel):
    question_key: str = Field(min_length=3, max_length=160, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]+$")
    expected_workspace_lock_version: int = Field(ge=1)
    revision: QuestionRevisionInput


class RevisionAppend(QuestionRevisionInput):
    expected_revision_no: int = Field(ge=1)
    expected_workspace_lock_version: int = Field(ge=1)


def _canonical_hash(value: dict) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _revision_payload(payload: QuestionRevisionInput) -> dict:
    data = payload.model_dump()
    data["options"] = sorted(data["options"], key=lambda item: item["display_order"])
    return data


def _write_audit(db: AsyncSession, actor: str, action: str, resource_id: str, metadata: dict) -> None:
    db.add(
        AdminAuditEvent(
            actor_subject=actor,
            action=action,
            resource_type="authoring_workspace",
            resource_id=resource_id,
            metadata_json=metadata,
        )
    )


@router.post("")
async def create_workspace(
    payload: WorkspaceCreate,
    db: DbSession,
    principal: CanEditContent,
) -> dict:
    workspace = AuthoringWorkspace(
        workspace_key=payload.workspace_key,
        title=payload.title,
        locale=payload.locale,
        status="draft",
        lock_version=1,
        created_by=principal.subject,
        updated_by=principal.subject,
    )
    async with db.begin():
        db.add(workspace)
        await db.flush()
        _write_audit(db, principal.subject, "authoring_workspace.created", str(workspace.id), {})
    return {
        "id": str(workspace.id),
        "workspace_key": workspace.workspace_key,
        "title": workspace.title,
        "locale": workspace.locale,
        "status": workspace.status,
        "lock_version": workspace.lock_version,
    }


@router.get("")
async def list_workspaces(
    db: DbSession,
    principal: CanEditContent,
    limit: int = 25,
    offset: int = 0,
) -> dict:
    if limit < 1 or limit > 100 or offset < 0:
        raise HTTPException(status_code=422, detail="Invalid pagination.")
    rows = (
        await db.scalars(
            select(AuthoringWorkspace)
            .order_by(AuthoringWorkspace.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return {
        "items": [
            {
                "id": str(row.id),
                "workspace_key": row.workspace_key,
                "title": row.title,
                "locale": row.locale,
                "status": row.status,
                "lock_version": row.lock_version,
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset,
    }


@router.post("/{workspace_id}/questions")
async def create_question(
    workspace_id: UUID,
    payload: QuestionCreate,
    db: DbSession,
    principal: CanEditContent,
) -> dict:
    revision_data = _revision_payload(payload.revision)
    option_keys = [item["key"] for item in revision_data["options"]]
    option_orders = [item["display_order"] for item in revision_data["options"]]
    if len(option_keys) != len(set(option_keys)) or len(option_orders) != len(set(option_orders)):
        raise HTTPException(status_code=422, detail="Option keys and display orders must be unique.")
    if payload.revision.answer_key_option_key not in option_keys:
        raise HTTPException(status_code=422, detail="Answer key must reference an existing option.")
    async with db.begin():
        workspace = await db.scalar(
            select(AuthoringWorkspace)
            .where(AuthoringWorkspace.id == workspace_id)
            .with_for_update()
        )
        if workspace is None:
            raise HTTPException(status_code=404, detail="Authoring workspace not found.")
        if workspace.status != "draft":
            raise HTTPException(status_code=409, detail="Workspace is not editable.")
        if workspace.lock_version != payload.expected_workspace_lock_version:
            raise HTTPException(status_code=409, detail="revision_conflict: workspace changed.")
        question = WorkspaceQuestion(workspace_id=workspace_id, question_key=payload.question_key)
        db.add(question)
        await db.flush()
        revision = WorkspaceQuestionRevision(
            workspace_question_id=question.id,
            revision_no=1,
            locale=revision_data["locale"],
            stem=revision_data["stem"],
            explanation=revision_data["explanation"],
            difficulty=revision_data["difficulty"],
            answer_key_option_key=revision_data["answer_key_option_key"],
            estimated_seconds=revision_data["estimated_seconds"],
            options_json=revision_data["options"],
            taxonomy_json=revision_data["taxonomy"],
            cognitive_objectives_json=revision_data["cognitive_objectives"],
            perspectives_json=revision_data["perspectives"],
            provenance_json=revision_data["provenance"],
            content_sha256=_canonical_hash(revision_data),
            canonicalization_version="json-sort-v1",
            author_subject=principal.subject,
        )
        db.add(revision)
        await db.flush()
        question.current_revision_id = revision.id
        workspace.lock_version += 1
        workspace.updated_by = principal.subject
        _write_audit(
            db,
            principal.subject,
            "authoring_question.created",
            str(question.id),
            {"revision_id": str(revision.id), "content_sha256": revision.content_sha256},
        )
    return {
        "question_id": str(question.id),
        "question_key": question.question_key,
        "revision_id": str(revision.id),
        "revision_no": revision.revision_no,
        "content_sha256": revision.content_sha256,
        "workspace_lock_version": workspace.lock_version,
    }


@router.post("/{workspace_id}/questions/{question_id}/revisions")
async def append_revision(
    workspace_id: UUID,
    question_id: UUID,
    payload: RevisionAppend,
    db: DbSession,
    principal: CanEditContent,
) -> dict:
    revision_data = _revision_payload(payload)
    revision_data.pop("expected_revision_no")
    revision_data.pop("expected_workspace_lock_version")
    option_keys = [item["key"] for item in revision_data["options"]]
    option_orders = [item["display_order"] for item in revision_data["options"]]
    if len(option_keys) != len(set(option_keys)) or len(option_orders) != len(set(option_orders)):
        raise HTTPException(status_code=422, detail="Option keys and display orders must be unique.")
    if payload.answer_key_option_key not in option_keys:
        raise HTTPException(status_code=422, detail="Answer key must reference an existing option.")
    async with db.begin():
        workspace = await db.scalar(
            select(AuthoringWorkspace)
            .where(AuthoringWorkspace.id == workspace_id)
            .with_for_update()
        )
        question = await db.scalar(
            select(WorkspaceQuestion)
            .where(
                WorkspaceQuestion.id == question_id,
                WorkspaceQuestion.workspace_id == workspace_id,
            )
            .with_for_update()
        )
        if workspace is None or question is None:
            raise HTTPException(status_code=404, detail="Workspace question not found.")
        if workspace.status != "draft" or question.is_tombstoned:
            raise HTTPException(status_code=409, detail="Workspace question is not editable.")
        current = await db.get(WorkspaceQuestionRevision, question.current_revision_id)
        if (
            workspace.lock_version != payload.expected_workspace_lock_version
            or current is None
            or current.revision_no != payload.expected_revision_no
        ):
            raise HTTPException(status_code=409, detail="revision_conflict: refresh before editing.")
        revision = WorkspaceQuestionRevision(
            workspace_question_id=question.id,
            revision_no=current.revision_no + 1,
            locale=revision_data["locale"],
            stem=revision_data["stem"],
            explanation=revision_data["explanation"],
            difficulty=revision_data["difficulty"],
            answer_key_option_key=revision_data["answer_key_option_key"],
            estimated_seconds=revision_data["estimated_seconds"],
            options_json=revision_data["options"],
            taxonomy_json=revision_data["taxonomy"],
            cognitive_objectives_json=revision_data["cognitive_objectives"],
            perspectives_json=revision_data["perspectives"],
            provenance_json=revision_data["provenance"],
            content_sha256=_canonical_hash(revision_data),
            canonicalization_version="json-sort-v1",
            author_subject=principal.subject,
        )
        db.add(revision)
        await db.flush()
        question.current_revision_id = revision.id
        workspace.lock_version += 1
        workspace.updated_by = principal.subject
        _write_audit(
            db,
            principal.subject,
            "authoring_question.revised",
            str(question.id),
            {
                "revision_no": revision.revision_no,
                "revision_id": str(revision.id),
                "content_sha256": revision.content_sha256,
            },
        )
    return {
        "question_id": str(question.id),
        "revision_id": str(revision.id),
        "revision_no": revision.revision_no,
        "content_sha256": revision.content_sha256,
        "workspace_lock_version": workspace.lock_version,
    }
