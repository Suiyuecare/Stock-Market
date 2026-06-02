from typing import Dict, List, Optional

ScorePayload = Dict[str, object]


def scoring_payload(
    score: float,
    positive_factors: Optional[List[str]] = None,
    negative_factors: Optional[List[str]] = None,
    risk_factors: Optional[List[str]] = None,
    confidence: float = 0.5,
) -> ScorePayload:
    return {
        "score": round(score, 4),
        "positive_factors": positive_factors or [],
        "negative_factors": negative_factors or [],
        "risk_factors": risk_factors or [],
        "confidence": round(confidence, 4),
    }
