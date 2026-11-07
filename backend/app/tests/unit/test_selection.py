import pytest

from app.modules.gameplay.selection import CandidateQuestion, select_questions


def candidate(key: str, *, topic: str = "science", locale: str = "en-IN") -> CandidateQuestion:
    return CandidateQuestion(
        question_key=key,
        locale=locale,
        difficulty="standard",
        taxonomy_keys=frozenset({topic}),
    )


def test_selection_is_reproducible_for_same_seed() -> None:
    pool = [candidate(f"q-{index}") for index in range(10)]
    first = select_questions(pool, count=5, locale="en-IN", taxonomy_scope=frozenset({"science"}),
                             difficulty="standard", seed="session-seed")
    second = select_questions(pool, count=5, locale="en-IN", taxonomy_scope=frozenset({"science"}),
                              difficulty="standard", seed="session-seed")
    assert [item.question_key for item in first] == [item.question_key for item in second]


def test_explicit_taxonomy_and_locale_are_hard_filters() -> None:
    pool = [candidate("science"), candidate("history", topic="history"),
            candidate("gujarati", locale="gu-IN")]
    selected = select_questions(pool, count=10, locale="en-IN",
                                taxonomy_scope=frozenset({"science"}),
                                difficulty=None, seed="x")
    assert [item.question_key for item in selected] == ["science"]


def test_selection_never_returns_excluded_question() -> None:
    selected = select_questions([candidate("q1"), candidate("q2")], count=2,
                                locale="en-IN", taxonomy_scope=frozenset(),
                                difficulty=None, seed="x", excluded_keys=frozenset({"q1"}))
    assert [item.question_key for item in selected] == ["q2"]


def test_count_must_be_positive() -> None:
    with pytest.raises(ValueError, match="at least 1"):
        select_questions([], count=0, locale="en-IN", taxonomy_scope=frozenset(),
                         difficulty=None, seed="x")
