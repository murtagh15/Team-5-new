from ege_calculator.services.scoring_service import calculate_total_score


def test_total_score():
    result = calculate_total_score(80, 90, 70)

    assert result == 240
