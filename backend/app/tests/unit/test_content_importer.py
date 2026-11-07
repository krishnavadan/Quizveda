from pathlib import Path

from app.modules.content.importer import read_pack_questions


def test_sample_pack_can_be_read_after_validation_contract() -> None:
    pack_dir = Path(__file__).parents[4] / "content" / "examples" / "sample-pack"
    manifest, questions = read_pack_questions(pack_dir)
    assert manifest["pack_key"] == "general-science"
    assert len(questions) == 1
    assert questions[0]["answer_key"]["option_key"] == "B"
