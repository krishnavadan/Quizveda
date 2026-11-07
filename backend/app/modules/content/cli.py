import argparse
from pathlib import Path

from app.modules.content.validator import validate_pack


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a QuizVeda content pack offline.")
    parser.add_argument("pack_dir", type=Path)
    parser.add_argument("--schema-dir", type=Path, default=Path("../content/schema))
    args = parser.parse_args()
    result = validate_pack(
        args.pack_dir,
        args.schema_dir / "manifest.schema.json",
        args.schema_dir / "question.schema.json",
    )
    if result.valid:
        print(f"VALID {result.pack_key}@{result.version}: {result.question_count} questions")
        return 0
    for error in result.errors:
        print(f"ERROR: {error}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
