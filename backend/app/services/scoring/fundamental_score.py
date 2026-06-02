from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_fundamental_score(symbol: str) -> ScorePayload:
    """Return a mock fundamental score until real financial statement data is connected."""
    score = {"2330": 0.72, "2454": 0.6, "2317": 0.42, "2308": 0.58}.get(symbol, 0.45)
    return scoring_payload(
        score=score,
        positive_factors=["profitability quality", "revenue trend"] if score >= 0.5 else [],
        negative_factors=[] if score >= 0.5 else ["valuation uncertainty"],
        confidence=0.58,
    )
