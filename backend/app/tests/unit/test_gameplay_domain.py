from uuid import uuid4

import pytest

from app.modules.gameplay.domain import (
    GameplayError,
    SessionStatus,
    ensure_answerable,
    evaluate_answer,
)


def test_correct_answer_awards_configured_score() -> None:
    option_id = uuid4()
    outcome = evaluate_answer(
        selected_option_id=option_id,
        correct_option_id=option_id,
        correct_score=100,
        explanation="Because the explanation is reviewed content.",
    )
    assert outcome.is_correct is True
    assert outcome.score_delta == 100


def test_incorrect_answer_awards_incorrect_score() -> None:
    outcome = evaluate_answer(
        selected_option_id=uuid4(),
        correct_option_id=uuid4(),
        correct_score=100,
        incorrect_score=0,
        explanation="Review the concept and try again.",
    )
    assert outcome.is_correct is False
    assert outcome.score_delta == 0


@pytest.mark.parametrize(
    ("status", "same_question", "already_answered", "message"),
    [
        (SessionStatus.COMPLETED, True, False, "Session is not active."),
        (SessionStatus.ACTIVE, False, False, "Question is not the current question."),
        (SessionStatus.ACTIVE, True, True, "Question has already been answered."),
    ],
)
def test_invalid_answer_transition_is_rejected(
    status: SessionStatus,
    same_question: bool,
    already_answered: bool,
    message: str,
) -> None:
    current = uuid4()
    requested = current if same_question else uuid4()
    with pytest.raises(GameplayError, match=message):
        ensure_answerable(
            session_status=status,
            requested_question_id=requested,
            current_question_id=current,
            already_answered=already_answered,
        )
