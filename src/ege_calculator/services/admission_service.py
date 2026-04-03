from ege_calculator.services.scoring_service import calculate_total_score
from ege_calculator.schemas.dto import ScoreResponse

RADIUS = 25
MIN_SUBJECT_SCORE = 40


def admission_probability(user_score: int, passing_score: int) -> float:
    diff = user_score - passing_score

    if diff <= -RADIUS:
        p = 0.0
    elif diff >= RADIUS:
        p = 100.0
    else:
        p = (diff + RADIUS) / (2 * RADIUS) * 100

    p = round(p, 1)

    if p < 10:
        p = 0.0

    return p


def validate_subject_scores(scores: dict, min_score: int = MIN_SUBJECT_SCORE) -> bool:
    subject_keys = ["math", "rus", "phys", "inf", "eng"]
    above_min = sum(1 for k in subject_keys if scores.get(k, 0) >= min_score)
    return above_min >= 3


def calculate_chance(repo, request):
    program = repo.find_program(
        request.university,
        request.program
    )

    if program is None:
        raise ValueError("Program not found")

    total = calculate_total_score(
        request.russian,
        request.math,
        request.physics
    )

    required = program["min_score"]

    diff = total - required

    chance = max(0, min(100, 50 + diff * 2))

    return ScoreResponse(
        total_score=total,
        required_score=required,
        chance_percent=chance
    )
