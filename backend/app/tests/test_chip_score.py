from app.services.scoring.chip_score import calculate_chip_score


def test_chip_score_contract() -> None:
    payload = calculate_chip_score("2330")

    assert set(payload.keys()) == {"score", "positive_factors", "negative_factors", "risk_factors", "confidence"}
    assert payload["score"] > 0
