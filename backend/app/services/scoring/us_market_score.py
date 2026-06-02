from typing import Dict

from app.services.scoring.common import ScorePayload, scoring_payload


def calculate_us_market_score(linkage: Dict[str, float]) -> ScorePayload:
    """Score Taiwan linkage to US semiconductors, mega-cap tech, VIX, and index proxies."""
    weights = {
        "NASDAQ": 0.12,
        "SOX": 0.16,
        "S&P500": 0.08,
        "VIX": 0.12,
        "TSM_ADR": 0.16,
        "NVDA": 0.12,
        "AMD": 0.06,
        "AAPL": 0.05,
        "AVGO": 0.08,
        "MU": 0.04,
        "MSFT": 0.04,
        "META": 0.03,
        "GOOGL": 0.03,
        "AMZN": 0.03,
    }
    weighted_sum = sum(linkage.get(symbol, 0.0) * weight for symbol, weight in weights.items())
    score = max(-1.0, min(1.0, weighted_sum))
    positives = [symbol for symbol, value in linkage.items() if value > 0]
    negatives = [symbol for symbol, value in linkage.items() if value < 0]
    return scoring_payload(score=score, positive_factors=positives, negative_factors=negatives, confidence=0.6)


def us_linkage_score(linkage: Dict[str, float]) -> float:
    return float(calculate_us_market_score(linkage)["score"])
