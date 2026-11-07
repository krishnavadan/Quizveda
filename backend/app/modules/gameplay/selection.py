import hashlib
from collections.abc import Iterable
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CandidateQuestion:
    question_key: str
    locale: str
    difficulty: str
    taxonomy_keys: frozenset[str]
    topic_fit: float = 1.0
    difficulty_fit: float = 1.0
    objective_fit: float = 1.0
    perspective_fit: float = 1.0
    learning_value: float = 1.0
    freshness: float = 1.0


@dataclass(frozen=True, slots=True)
class SelectionPolicy:
    version: str = "1.0"
    weights: tuple[float, ...] = (0.30, 0.20, 0.15, 0.15, 0.10, 0.10)


def _score(candidate: CandidateQuestion, policy: SelectionPolicy) -> float:
    values = (
        candidate.topic_fit,
        candidate.difficulty_fit,
        candidate.objective_fit,
        candidate.perspective_fit,
        candidate.learning_value,
        candidate.freshness,
    )
    if len(policy.weights) != len(values) or abs(sum(policy.weights) - 1.0) > 0.000001:
        raise ValueError("Selection policy weights must contain six values summing to 1.")
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("Candidate fit values must be between 0 and 1.")
    return sum(weight * value for weight, value in zip(policy.weights, values, strict=True))


def select_questions(
    candidates: Iterable[CandidateQuestion],
    *,
    count: int,
    locale: str,
    taxonomy_scope: frozenset[str],
    difficulty: str | None,
    seed: str,
    policy: SelectionPolicy = SelectionPolicy(),
    excluded_keys: frozenset[str] = frozenset(),
) -> list[CandidateQuestion]:
    """Select an exact, reproducible sequence without silently broadening scope."""
    if count < 1:
        raise ValueError("count must be at least 1")
    eligible = [
        candidate for candidate in candidates
        if candidate.locale == locale
        and candidate.question_key not in excluded_keys
        and (difficulty is None or candidate.difficulty == difficulty)
        and (not taxonomy_scope or bool(candidate.taxonomy_keys & taxonomy_scope))
    ]
    ranked = sorted(
        eligible,
        key=lambda candidate: (
            -_score(candidate, policy),
            hashlib.sha256(f"{seed}:{candidate.question_key}".encode()).hexdigest(),
        ),
    )
    return ranked[:count]
