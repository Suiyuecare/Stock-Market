from typing import Dict, List

from app.schemas import NewsEvent, RiskScore, TechnicalIndicators
from app.services.scoring.news_score import calculate_news_score


def build_risk_score(indicators: TechnicalIndicators, linkage: Dict[str, float], events: List[NewsEvent]) -> RiskScore:
    """Aggregate volatility, liquidity, concentration, and event risk into a 0-1 score."""
    volatility = 0.48 if indicators.rsi_14 and indicators.rsi_14 > 70 else 0.3
    liquidity = 0.18
    concentration = 0.36
    event_score = float(calculate_news_score(events)["score"])
    event = max(0.0, min(1.0, abs(event_score) + abs(linkage.get("VIX", 0.0)) * 0.25))
    total = round(max(0.0, min(1.0, (volatility * 0.35) + (liquidity * 0.2) + (concentration * 0.2) + (event * 0.25))), 4)
    return RiskScore(
        total=total,
        volatility=round(volatility, 4),
        liquidity=round(liquidity, 4),
        concentration=round(concentration, 4),
        event=round(event, 4),
        explanation="Higher scores indicate higher research risk; outputs are for research and education only.",
    )
