import re
from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.db.models import (
    AdminAuditEvent,
    ContentPackVersion,
    Question,
    QuestionOption,
    QuestionRevision,
)
from app.modules.admin.security import AdminPrincipal, require_roles

router = APIRouter(prefix="/admin", tags=["admin-content"])
DbSession = Annotated[AsyncSession, Depends(get_db_session)]
CanReadContent = Annotated[
    AdminPrincipal,
    Depends(require_roles("content_editor", "content_reviewer", "content_publisher")),
]
CanReviewContent = Annotated[
    AdminPrincipal,
    Depends(require_roles("content_reviewer")),
]
CanPublishContent = Annotated[
    AdminPrincipal,
    Depends(require_roles("content_publisher")),
]
CanAudit = Annotated[AdminPrincipal, Depends(require_roles("admin"))]


class ApprovalRequest(BaseModel):
    approval_reference: str = Field(min_length=3, max_length=160)


def _pack_summary(pack: ContentPackVersion) -> dict:
    return {
        "id": str(pack.id),
        "pack_key": pack.pack_key,
        "version": pack.version,
        "schema_version": pack.schema_version,
        "locale": pack.locale,
        "title": pack.title,
        "lifecycle_status": pack.lifecycle_status,
        "manifest_sha256": pack.manifest_sha256,
        "approved_by": pack.approved_by,
        "approval_reference": pack.approval_reference,
        "approved_at": pack.approved_at.isoformat() if pack.approved_at else None,
        "published_at": pack.published_at.isoformat() if pack.published_at else None,
        "created_at": pack.created_at.isoformat() if pack.created_at else None,
    }


async def _write_audit(
    db: AsyncSession,
    *,
    actor: str,
    action: str,
    resource_id: UUID,
    reference: str | None = None,
    metadata: dict | None = None,
) -> None:
    db.add(
        AdminAuditEvent(
            actor_subject=actor,
            action=action,
            resource_type="content_pack_version",
            resource_id=str(resource_id),
            reference=reference,
            metadata_json=metadata or {},
        )
    )


@router.get("/content-packs")
async def list_content_packs(
    db: DbSession,
    principal: CanReadContent,
    status: str | None = Query(default=None, pattern="^(validated|approved|published)$"),
    limit: int = Query(default=25, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    statement = select(ContentPackVersion).order_by(ContentPackVersion.created_at.desc())
    if status:
        statement = statement.where(ContentPackVersion.lifecycle_status == status)
    rows = (await db.scalars(statement.limit(limit).offset(offset))).all()
    return {"items": [_pack_summary(pack) for pack in rows], "limit": limit, "offset": offset}


@router.get("/content-packs/{pack_id}")
async def get_content_pack(
    pack_id: UUID,
    db: DbSession,
    principal: CanReadContent,
) -> dict:
    pack = await db.get(ContentPackVersion, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Content pack version not found.")
    return _pack_summary(pack)


@router.get("/content-packs/{pack_id}/questions")
async def list_pack_questions(
    pack_id: UUID,
    db: DbSession,
    principal: CanReadContent,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    pack = await db.get(ContentPackVersion, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Content pack version not found.")
    rows = (
        await db.execute(
            select(Question, QuestionRevision)
            .join(QuestionRevision, QuestionRevision.question_id == Question.id)
            .where(Question.pack_version_id == pack_id)
            .order_by(Question.question_key, QuestionRevision.revision_no.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()
    items = []
    for question, revision in rows:
        options = (
            await db.scalars(
                select(QuestionOption)
                .where(QuestionOption.revision_id == revision.id)
                .order_by(QuestionOption.display_order)
            )
        ).all()
        items.append(
            {
                "question_id": str(question.id),
                "question_key": question.question_key,
                "revision_id": str(revision.id),
                "revision_no": revision.revision_no,
                "locale": revision.locale,
                "stem": revision.stem,
                "explanation": revision.explanation,
                "difficulty": revision.difficulty,
                "estimated_seconds": revision.estimated_seconds,
                "approved": revision.approved,
                "answer_key_option_key": revision.answer_key_option_key,
                "options": [
                    {
                        "key": option.option_key,
                        "text": option.text,
                        "display_order": option.display_order,
                    }
                    for option in options
                ],
                "metadata": revision.metadata_json,
            }
        )
    return {"items": items, "limit": limit, "offset": offset}


@router.post("/content-packs/{pack_id}/approve")
async def approve_content_pack(
    pack_id: UUID,
    payload: ApprovalRequest,
    db: DbSession,
    principal: CanReviewContent,
) -> dict:
    async with db.begin():
        pack = await db.scalar(
            select(ContentPackVersion)
            .where(ContentPackVersion.id == pack_id)
            .with_for_update()
        )
        if pack is None:
            raise HTTPException(status_code=404, detail="Content pack version not found.")
        if pack.lifecycle_status != "validated":
            raise HTTPException(status_code=409, detail="Only validated packs can be approved.")
        now = datetime.now(UTC)
        pack.lifecycle_status = "approved"
        pack.approved_by = principal.subject
        pack.approval_reference = payload.approval_reference
        pack.approved_at = now
        revisions = (
            await db.scalars(
                select(QuestionRevision)
                .join(Question, Question.id == QuestionRevision.question_id)
                .where(Question.pack_version_id == pack_id)
            )
        ).all()
        for revision in revisions:
            revision.approved = True
        await _write_audit(
            db,
            actor=principal.subject,
            action="content_pack.approved",
            resource_id=pack_id,
            reference=payload.approval_reference,
            metadata={"revision_count": len(revisions)},
        )
    await db.refresh(pack)
    return _pack_summary(pack)


@router.post("/content-packs/{pack_id}/publish")
async def publish_content_pack(
    pack_id: UUID,
    payload: ApprovalRequest,
    db: DbSession,
    principal: CanPublishContent,
) -> dict:
    async with db.begin():
        pack = await db.scalar(
            select(ContentPackVersion)
            .where(ContentPackVersion.id == pack_id)
            .with_for_update()
        )
        if pack is None:
            raise HTTPException(status_code=404, detail="Content pack version not found.")
        if pack.lifecycle_status != "approved":
            raise HTTPException(status_code=409, detail="Only approved packs can be published.")
        if pack.approved_by == principal.subject and "admin" not in principal.roles:
            raise HTTPException(
                status_code=403,
                detail="A different authorized publisher must publish this approval.",
            )
        now = datetime.now(UTC)
        pack.lifecycle_status = "published"
        pack.published_at = now
        await _write_audit(
            db,
            actor=principal.subject,
            action="content_pack.published",
            resource_id=pack_id,
            reference=payload.approval_reference,
            metadata={"manifest_sha256": pack.manifest_sha256},
        )
    await db.refresh(pack)
    return _pack_summary(pack)


@router.get("/audit-events")
async def list_audit_events(
    db: DbSession,
    principal: CanAudit,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> dict:
    rows = (
        await db.scalars(
            select(AdminAuditEvent)
            .order_by(AdminAuditEvent.occurred_at.desc())
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return {
        "items": [
            {
                "id": str(row.id),
                "actor_subject": row.actor_subject,
                "action": row.action,
                "resource_type": row.resource_type,
                "resource_id": row.resource_id,
                "reference": row.reference,
                "metadata": row.metadata_json,
                "occurred_at": row.occurred_at.isoformat() if row.occurred_at else None,
            }
            for row in rows
        ],
        "limit": limit,
        "offset": offset,
    }


def _normalise_editorial_text(value: str) -> str:
    return re.sub(r"\\W+", " ", value.casefold(), flags=re.UNICODE).strip()


@router.get("/content-packs/{pack_id}/quality-report")
async def get_content_quality_report(
    pack_id: UUID,
    db: DbSession,
    principal: CanReadContent,
) -> dict:
    """Return deterministic editorial advisories; this report never approves content."""
    pack = await db.get(ContentPackVersion, pack_id)
    if pack is None:
        raise HTTPException(status_code=404, detail="Content pack version not found.")

    rows = (
        await db.execute(
            select(Question, QuestionRevision)
            .join(QuestionRevision, QuestionRevision.question_id == Question.id)
            .where(Question.pack_version_id == pack_id)
            .order_by(Question.question_key, QuestionRevision.revision_no.desc())
        )
    ).all()

    latest: dict[UUID, tuple[Question, QuestionRevision]] = {}
    for question, revision in rows:
        latest.setdefault(question.id, (question, revision))

    revision_ids = [revision.id for _, revision in latest.values()]
    option_rows = (
        await db.scalars(
            select(QuestionOption)
            .where(QuestionOption.revision_id.in_(revision_ids))
            .order_by(QuestionOption.revision_id, QuestionOption.display_order)
        )
    ).all() if revision_ids else []
    options_by_revision: dict[UUID, list[QuestionOption]] = {}
    for option in option_rows:
        options_by_revision.setdefault(option.revision_id, []).append(option)

    findings: list[dict] = []
    stem_groups: dict[str, list[str]] = {}
    for question, revision in latest.values():
        key = question.question_key
        normalised_stem = _normalise_editorial_text(revision.stem)
        if normalised_stem:
            stem_groups.setdefault(normalised_stem, []).append(key)
        if len(revision.stem.strip()) < 20:
            findings.append({
                "question_key": key,
                "code": "short_stem",
                "severity": "advisory",
                "message": (
                    "Question stem is unusually short; verify that it provides enough context."
                ),
            })
        if len(revision.explanation.strip()) < 30:
            findings.append({
                "question_key": key,
                "code": "short_explanation",
                "severity": "advisory",
                "message": (
                    "Explanation is brief; consider adding reasoning that helps learners understand the answer."
                ),
            })
        options = options_by_revision.get(revision.id, [])
        normalised_options = [_normalise_editorial_text(option.text) for option in options]
        if len(normalised_options) != len(set(normalised_options)):
            findings.append({
                "question_key": key,
                "code": "duplicate_options",
                "severity": "advisory",
                "message": "Two or more answer options have identical normalised text.",
            })
        if len(options) < 3:
            findings.append({
                "question_key": key,
                "code": "few_options",
                "severity": "advisory",
                "message": (
                    "Fewer than three answer options are present; confirm this is intentional."
                ),
            })

    duplicate_groups = [
        {"question_keys": keys, "count": len(keys)}
        for keys in stem_groups.values()
        if len(keys) > 1
    ]
    for group in duplicate_groups:
        for key in group["question_keys"]:
            findings.append({
                "question_key": key,
                "code": "duplicate_stem",
                "severity": "advisory",
                "message": (
                    "This question has the same normalised stem as another question in the pack."
                ),
            })

    return {
        "pack_id": str(pack.id),
        "pack_key": pack.pack_key,
        "version": pack.version,
        "lifecycle_status": pack.lifecycle_status,
        "question_count": len(latest),
        "advisory_count": len(findings),
        "duplicate_stem_groups": duplicate_groups,
        "findings": findings,
        "disclaimer": (
            "Heuristic editorial signals only. They may produce false positives or miss defects "
            "and do not replace subject-matter review, schema validation, rights checks, or approval."
        ),
    }
