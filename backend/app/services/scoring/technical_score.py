from typing import List

from app.schemas import TechnicalIndicators
from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_technical_score(indicators: TechnicalIndicators, closes: List[float]) -> ScorePayload:
    """Score trend, momentum, and volume-price confirmation from technical indicators."""
    latest = closes[-1]
    score = 0.0
    positives = []
    negatives = []

    if indicators.ma_20:
        if latest > indicators.ma_20:
            score += 0.25
            positives.append("close above MA20")
        else:
            score -= 0.2
            negatives.append("close below MA20")
    if indicators.ma_60:
        if latest > indicators.ma_60:
            score += 0.2
            positives.append("close above MA60")
        else:
            score -= 0.15
            negatives.append("close below MA60")
    if indicators.rsi_14 is not None:
        if 45 <= indicators.rsi_14 <= 65:
            score += 0.15
            positives.append("RSI in constructive range")
        elif indicators.rsi_14 > 75:
            score -= 0.15
            negatives.append("RSI overextended")
        elif indicators.rsi_14 < 35:
            score -= 0.1
            negatives.append("RSI weak")
    if indicators.macd_histogram is not None:
        if indicators.macd_histogram > 0:
            score += 0.15
            positives.append("MACD histogram positive")
        else:
            score -= 0.1
            negatives.append("MACD histogram negative")
    if indicators.volume_price_divergence is not None:
        if indicators.volume_price_divergence > 0:
            score += 0.1
            positives.append("volume confirms price")
        else:
            score -= 0.05
            negatives.append("volume-price divergence")

    score = max(-1.0, min(1.0, score))
    return scoring_payload(score=score, positive_factors=positives, negative_factors=negatives, confidence=0.62)
