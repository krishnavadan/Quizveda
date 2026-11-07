import argparse
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy import select

from app.core.database import SessionLocal
from app.db.models import (
    ContentPackVersion,
    Question,
    QuestionOption,
    QuestionRevision,
)
from app.modules.content.validator import validate_pack


def read_pack_questions(pack_dir: Path) -> tuple[dict, list[dict]]:
    manifest = json.loads((pack_dir / "manifest.json").read_text(encoding="utf-8"))
    questions: list[dict] = []
    for entry in manifest["files"]:
        source = pack_dir / entry["path"]
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.strip():
                questions.append(json.loads(line))
    return manifest, questions


async def import_pack(
    pack_dir: Path,
    schema_dir: Path,
    *,
    approval_actor: str | None = None,
    approval_reference: str | None = None,
    publish: bool = False,
) -> UUID:
    if bool(approval_actor) != bool(approval_reference):
        raise ValueError("Approval actor and approval reference must be provided together.")
    if publish and not approval_actor:
        raise ValueError("Publishing requires an approval actor and approval reference.")

    validation = validate_pack(
        pack_dir,
        schema_dir / "manifest.schema.json",
        schema_dir / "question.schema.json",
    )
    if not validation.valid:
        raise ValueError("Content pack validation failed: " + "; ".join(validation.errors))

    manifest, questions = read_pack_questions(pack_dir)
    approved = bool(approval_actor and approval_reference)
    status = "published" if publish else "approved" if approved else "validated"
    now = datetime.now(timezone.utc)

    async with SessionLocal() as db:
        async with db.begin():
            existing = await db.scalar(
                select(ContentPackVersion).where(
                    ContentPackVersion.pack_key == manifest["pack_key"],
                    ContentPackVersion.version == manifest["version"],
                )
            )
            if existing:
                raise ValueError("This pack key and version have already been imported.")

            pack_version = ContentPackVersion(
                pack_key=manifest["pack_key"],
                version=manifest["version"],
                schema_version=manifest["schema_version"],
                locale=manifest["locale"],
                title=manifest["title"],
                manifest_sha256=validation.manifest_sha256,
                lifecycle_status=status,
                approved_by=approval_actor if approved else None,
                approval_reference=approval_reference if approved else None,
                approved_at=now if approved else None,
                published_at=now if publish else None,
            )
            db.add(pack_version)
            await db.flush()

            for question_data in questions:
                question = Question(
                    question_key=question_data["question_key"],
                    pack_version_id=pack_version.id,
                )
                db.add(question)
                await db.flush()
                revision = QuestionRevision(
                    question_id=question.id,
                    revision_no=question_data["revision"],
                    locale=question_data["locale"],
                    stem=question_data["stem"],
                    explanation=question_data["explanation"],
                    difficulty=question_data["difficulty"],
                    answer_key_option_key=question_data["answer_key"]["option_key"],
                    estimated_seconds=question_data.get("estimated_seconds", 30),
                    approved=approved,
                    metadata_json={
                        "taxonomy": question_data.get("taxonomy", []),
                        "cognitive_objectives": question_data.get("cognitive_objectives", []),
                        "perspectives": question_data.get("perspectives", []),
                        "provenance": question_data["provenance"],
                    },
                )
                db.add(revision)
                await db.flush()
                for order, option in enumerate(question_data["options"], start=1):
                    db.add(
                        QuestionOption(
                            revision_id=revision.id,
                            option_key=option["key"],
                            text=option["text"],
                            display_order=order,
                        )
                    )
            await db.flush()
            return pack_version.id


def main() -> int:
    parser = argparse.ArgumentParser(description="Import a validated QuizVeda content pack.")
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--schema-dir", type=Path, default=Path("../content/schema"))
    parser.add_argument("--approval-actor")
    parser.add_argument("--approval-reference")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()

    try:
        pack_id = asyncio.run(
            import_pack(
                args.pack_dir,
                args.schema_dir,
                approval_actor=args.approval_actor,
                approval_reference=args.approval_reference,
                publish=args.publish,
            )
        )
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Imported content pack version {pack_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
