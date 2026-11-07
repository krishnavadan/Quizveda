import hashlib
import json

from app.modules.content.validator import validate_pack


def test_pack_validation_accepts_matching_manifest_and_question(tmp_path) -> None:
    question = {
        "question_key": "science-water-001", "revision": 1, "locale": "en-IN",
        "type": "single_choice", "stem": "Which state is water in at room temperature?",
        "options": [{"key": "A", "text": "Solid"}, {"key": "B", "text": "Liquid"}],
        "answer_key": {"option_key": "B"}, "explanation": "Water is normally liquid at room temperature.",
        "difficulty": "beginner", "estimated_seconds": 20, "taxonomy": [{"node_key": "science"}],
        "provenance": {"rights_status": "original"},
    }
    raw = (json.dumps(question, separators=(",", ":")) + "\n").encode()
    (tmp_path / "questions.jsonl").write_bytes(raw)
    manifest = {
        "pack_key": "general-science", "version": "1.0.0", "schema_version": "1.0",
        "locale": "en-IN", "title": {"en-IN": "General Science"}, "question_count": 1,
        "files": [{"path": "questions.jsonl", "sha256": hashlib.sha256(raw).hexdigest(),
                   "bytes": len(raw), "records": 1}],
    }
    (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    schemas = __import__("pathlib").Path(__file__).parents[4] / "content" / "schema"
    # Test supplies the repository schemas through explicit paths.
    manifest_schema = schemas / "manifest.schema.json"
    question_schema = schemas / "question.schema.json"
    result = validate_pack(tmp_path, manifest_schema, question_schema)
    assert result.valid is True
    assert result.question_count == 1
