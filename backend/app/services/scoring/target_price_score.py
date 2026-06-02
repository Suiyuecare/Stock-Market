from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_target_price_score(symbol: str) -> ScorePayload:
    return scoring_payload(score=0.0, risk_factors=[f"{symbol} target-price provider not connected"], confidence=0.2)
