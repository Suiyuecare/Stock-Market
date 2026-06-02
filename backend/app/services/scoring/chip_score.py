from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_chip_score(symbol: str) -> ScorePayload:
    """Return a mock institutional/chip score from placeholder institutional flows."""
    score = {"2330": 0.34, "2454": 0.18, "2317": -0.08, "2308": 0.22}.get(symbol, 0.0)
    return scoring_payload(
        score=score,
        positive_factors=["foreign/institutional flow"] if score >= 0 else [],
        negative_factors=["institutional selling pressure"] if score < 0 else [],
        confidence=0.52,
    )
