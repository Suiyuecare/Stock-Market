from datetime import date
from typing import List, Optional

from app.schemas import FactorScore, NewsEvent, PredictionSignal, TechnicalIndicators
from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_news, get_mock_price_series, get_mock_us_linkage
from app.services.scoring.chip_score import calculate_chip_score
from app.services.scoring.fundamental_score import calculate_fundamental_score
from app.services.scoring.news_score import calculate_news_score
from app.services.scoring.risk_score import build_risk_score
from app.services.scoring.technical_score import calculate_technical_score
from app.services.scoring.us_market_score import calculate_us_market_score, us_linkage_score
from app.services.indicators import build_technical_indicators

DISCLAIMER = "Outputs are for research and education only, not personalized investment advice."


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def probability_from_score(score: float) -> float:
    return round(clamp(0.5 + score * 0.32), 4)


def _normalize_factor_score(score: float) -> float:
    if 0 <= score <= 100 and score > 1:
        return (score - 50) / 50
    return score


def _factor(name: str, category: str, score_payload: dict, weight: float, explanation: str) -> FactorScore:
    score = float(score_payload["score"])
    normalized_score = _normalize_factor_score(score)
    return FactorScore(
        name=name,
        category=category,
        score=round(normalized_score, 4),
        weight=weight,
        direction="positive" if normalized_score >= 0 else "negative",
        explanation=explanation,
    )


def build_factor_scores(
    symbol: str,
    indicators: TechnicalIndicators,
    closes: List[float],
    linkage: dict,
    events: List[NewsEvent],
    volumes: Optional[List[float]] = None,
    stock_profile: Optional[dict] = None,
) -> List[FactorScore]:
    return [
        _factor("Fundamental quality", "fundamental", calculate_fundamental_score(symbol), 0.22, "Mock financial quality, valuation, and growth composite."),
        _factor("Institutional flow", "chip", calculate_chip_score(symbol), 0.16, "Mock foreign/institutional trading flow score."),
        _factor("Technical structure", "technical", calculate_technical_score(indicators, closes, volumes), 0.22, "MA, RSI, KD, MACD, OBV, and volume-price divergence composite."),
        _factor("US market linkage", "us-linkage", calculate_us_market_score(linkage, stock_profile), 0.24, "Nasdaq, SOX, S&P 500, VIX, TSM ADR, and US mega-cap/semiconductor linkage."),
        _factor("News sentiment", "news", calculate_news_score(events), 0.16, "Structured event sentiment from the mock LLM parser interface."),
    ]


def composite_score(factors: List[FactorScore], risk_total: float) -> float:
    raw = sum(factor.score * factor.weight for factor in factors)
    adjusted = raw - (risk_total * 0.18)
    return round(max(-1.0, min(1.0, adjusted)), 4)


def build_signal(instrument: dict) -> PredictionSignal:
    series = get_mock_price_series(instrument["symbol"])
    indicators = TechnicalIndicators(**build_technical_indicators(series["highs"], series["lows"], series["closes"], series["volumes"]))
    linkage = get_mock_us_linkage()
    events = [NewsEvent(**event) for event in get_mock_news(instrument["symbol"])]
    risk = build_risk_score(indicators, linkage, events)
    stock_profile = {
        "stock_id": instrument["symbol"],
        "stock_name": instrument["name"],
        "industry": instrument.get("sector"),
        "supply_chain_tags": instrument.get("supply_chain_tags", []),
    }
    factors = build_factor_scores(instrument["symbol"], indicators, series["closes"], linkage, events, series["volumes"], stock_profile)
    score = composite_score(factors, risk.total)
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
