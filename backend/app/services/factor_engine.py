from datetime import date
from typing import Dict, List

from app.schemas import FactorScore, NewsEvent, PredictionSignal, RiskScore, TechnicalIndicators
from app.services.mock_provider import TW_INSTRUMENTS, get_mock_news, get_mock_price_series, get_mock_us_linkage
from app.services.technical_indicators import build_technical_indicators


DISCLAIMER = "Outputs are for research and education only, not personalized investment advice."


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def normalize_signed(value: float) -> float:
    return max(-1.0, min(1.0, value))


def us_linkage_score(linkage: Dict[str, float]) -> float:
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
    return round(normalize_signed(weighted_sum), 4)


def technical_score(indicators: TechnicalIndicators, closes: List[float]) -> float:
    latest = closes[-1]
    score = 0.0
    if indicators.ma_20:
        score += 0.25 if latest > indicators.ma_20 else -0.2
    if indicators.ma_60:
        score += 0.2 if latest > indicators.ma_60 else -0.15
    if indicators.rsi_14 is not None:
        if 45 <= indicators.rsi_14 <= 65:
            score += 0.15
        elif indicators.rsi_14 > 75:
            score -= 0.15
        elif indicators.rsi_14 < 35:
            score -= 0.1
    if indicators.macd_histogram is not None:
        score += 0.15 if indicators.macd_histogram > 0 else -0.1
    if indicators.volume_price_divergence is not None:
        score += 0.1 if indicators.volume_price_divergence > 0 else -0.05
    return round(normalize_signed(score), 4)


def fundamental_score(symbol: str) -> float:
    return {"2330": 0.72, "2454": 0.6, "2317": 0.42, "2308": 0.58}.get(symbol, 0.45)


def institutional_score(symbol: str) -> float:
    return {"2330": 0.34, "2454": 0.18, "2317": -0.08, "2308": 0.22}.get(symbol, 0.0)


def news_score(events: List[NewsEvent]) -> float:
    if not events:
        return 0.0
    return round(normalize_signed(sum(event.impact_score for event in events) / max(len(events), 1)), 4)


def build_risk_score(indicators: TechnicalIndicators, linkage: Dict[str, float], events: List[NewsEvent]) -> RiskScore:
    volatility = 0.48 if indicators.rsi_14 and indicators.rsi_14 > 70 else 0.3
    liquidity = 0.18
    concentration = 0.36
    event = clamp(abs(news_score(events)) + abs(linkage.get("VIX", 0.0)) * 0.25)
    total = round(clamp((volatility * 0.35) + (liquidity * 0.2) + (concentration * 0.2) + (event * 0.25)), 4)
    return RiskScore(
        total=total,
        volatility=round(volatility, 4),
        liquidity=round(liquidity, 4),
        concentration=round(concentration, 4),
        event=round(event, 4),
        explanation="Higher scores indicate higher research risk; this is not a buy/sell recommendation.",
    )


def build_factor_scores(symbol: str, indicators: TechnicalIndicators, closes: List[float], linkage: Dict[str, float], events: List[NewsEvent]) -> List[FactorScore]:
    factors = [
        FactorScore(
            name="Fundamental quality",
            category="fundamental",
            score=fundamental_score(symbol),
            weight=0.22,
            direction="positive",
            explanation="Mock fundamental composite based on profitability, valuation, and growth placeholders.",
        ),
        FactorScore(
            name="Institutional flow",
            category="chip",
            score=institutional_score(symbol),
            weight=0.16,
            direction="positive" if institutional_score(symbol) >= 0 else "negative",
            explanation="Mock foreign/institutional trading flow score.",
        ),
        FactorScore(
            name="Technical structure",
            category="technical",
            score=technical_score(indicators, closes),
            weight=0.22,
            direction="positive" if technical_score(indicators, closes) >= 0 else "negative",
            explanation="MA, RSI, KD, MACD, OBV, and volume-price divergence composite.",
        ),
        FactorScore(
            name="US market linkage",
            category="us-linkage",
            score=us_linkage_score(linkage),
            weight=0.24,
            direction="positive" if us_linkage_score(linkage) >= 0 else "negative",
            explanation="Nasdaq, SOX, S&P 500, VIX, TSM ADR, and US mega-cap/semiconductor linkage.",
        ),
        FactorScore(
            name="News sentiment",
            category="news",
            score=news_score(events),
            weight=0.16,
            direction="positive" if news_score(events) >= 0 else "negative",
            explanation="Structured event sentiment from the mock LLM parser interface.",
        ),
    ]
    return factors


def composite_score(factors: List[FactorScore], risk: RiskScore) -> float:
    raw = sum(factor.score * factor.weight for factor in factors)
    adjusted = raw - (risk.total * 0.18)
    return round(normalize_signed(adjusted), 4)


def probability_from_score(score: float) -> float:
    return round(clamp(0.5 + score * 0.32), 4)


def build_signal(instrument: dict) -> PredictionSignal:
    series = get_mock_price_series(instrument["symbol"])
    indicators = TechnicalIndicators(**build_technical_indicators(series["highs"], series["lows"], series["closes"], series["volumes"]))
    linkage = get_mock_us_linkage()
    events = [NewsEvent(**event) for event in get_mock_news(instrument["symbol"])]
    risk = build_risk_score(indicators, linkage, events)
    factors = build_factor_scores(instrument["symbol"], indicators, series["closes"], linkage, events)
    score = composite_score(factors, risk)
    sorted_factors = sorted(factors, key=lambda item: item.score * item.weight, reverse=True)

    return PredictionSignal(
        symbol=instrument["symbol"],
        name=instrument["name"],
        signal_date=date.today(),
        horizon="next-session",
        probability_up=probability_from_score(score),
        confidence=round(clamp(0.54 + abs(score) * 0.35), 4),
        composite_score=score,
        risk_score=risk,
        technicals=indicators,
        factor_scores=factors,
        positive_drivers=sorted_factors[:3],
        negative_drivers=sorted(factors, key=lambda item: item.score * item.weight)[:2],
        news=events,
    )


def build_all_signals() -> List[PredictionSignal]:
    return [build_signal(instrument) for instrument in TW_INSTRUMENTS]
