from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID


class SessionStatus(StrEnum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class GameplayError(ValueError):
    """Raised when a requested gameplay transition violates domain rules."""


@dataclass(frozen=True, slots=True)
class AnswerOutcome:
    is_correct: bool
    score_delta: int
    explanation: str


def evaluate_answer(
    *,
    selected_option_id: UUID,
    correct_option_id: UUID,
    correct_score: int,
    incorrect_score: int = 0,
    explanation: str,
) -> AnswerOutcome:
    """Evaluate an answer using server-held answer data only."""
    if correct_score < 0 or incorrect_score < 0:
        raise GameplayError("Score values must be non-negative.")

    is_correct = selected_option_id == correct_option_id
    return AnswerOutcome(
        is_correct=is_correct,
        score_delta=correct_score if is_correct else incorrect_score,
        explanation=explanation,
    )


def ensure_answerable(
    *,
    session_status: SessionStatus,
    requested_question_id: UUID,
    current_question_id: UUID,
    already_answered: bool,
) -> None:
    """Validate the domain preconditions before an answer is persisted."""
    if session_status is not SessionStatus.ACTIVE:
        raise GameplayError("Session is not active.")
    if requested_question_id != current_question_id:
        raise GameplayError("Question is not the current question.")
    if already_answered:
        raise GameplayError("Question has already been answered.")
