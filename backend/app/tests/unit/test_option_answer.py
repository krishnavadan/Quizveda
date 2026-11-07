from uuid import uuid4

from app.modules.gameplay.domain import evaluate_option_answer


def test_correct_option_awards_score() -> None:
    outcome = evaluate_option_answer(
        selected_option_key="B",
        correct_option_key="B",
        correct_score=100,
        explanation="Reviewed explanation.",
    )
    assert outcome.is_correct is True
    assert outcome.score_delta == 100


def test_wrong_option_awards_zero() -> None:
    outcome = evaluate_option_answer(
        selected_option_key="A",
        correct_option_key="B",
        correct_score=100,
        incorrect_score=0,
        explanation="Reviewed explanation.",
    )
    assert outcome.is_correct is False
    assert outcome.score_delta == 0


def test_negative_score_is_rejected() -> None:
    import pytest

    from app.modules.gameplay.domain import GameplayError

    with pytest.raises(GameplayError, match="non-negative"):
        evaluate_option_answer(
            selected_option_key="A",
            correct_option_key="B",
            correct_score=-1,
            explanation="Reviewed explanation.",
        )
