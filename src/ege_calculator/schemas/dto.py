from dataclasses import dataclass


@dataclass
class ScoreRequest:
    russian: int
    math: int
    physics: int
    university: str
    program: str


@dataclass
class ScoreResponse:
    total_score: int
    required_score: int
    chance_percent: float