from datetime import date
import math
from typing import Dict, List, Mapping, Optional, Union

from app.schemas import FactorScore, NewsEvent, PredictionSignal, TechnicalIndicators
from app.services.data_providers.mock_provider import TW_INSTRUMENTS, get_mock_news, get_mock_price_series, get_mock_us_linkage
from app.services.scoring.chip_score import calculate_chip_score
from app.services.scoring.fundamental_score import calculate_fundamental_score
from app.services.scoring.macro_score import calculate_macro_score
from app.services.scoring.news_score import calculate_news_score
from app.services.scoring.risk_score import build_risk_score
from app.services.scoring.target_price_score import calculate_target_price_score
from app.services.scoring.technical_score import calculate_technical_score
from app.services.scoring.us_market_score import calculate_us_market_score, us_linkage_score
from app.services.indicators import build_technical_indicators
from app.services.market_regime_engine import adjusted_factor_weights

DISCLAIMER = "Outputs are for research and education only, not personalized investment advice."
FINAL_SCORE_WEIGHTS = {
    "fundamental": 0.20,
    "chip": 0.18,
    "technical": 0.17,
    "us_market": 0.15,
    "news": 0.12,
    "macro": 0.08,
    "target_price": 0.05,
    "liquidity": 0.05,
}


def clamp(value: float, lower: float = 0.0, upper: float = 1.0) -> float:
    return max(lower, min(upper, value))


def probability_from_score(score: float) -> float:
    return round(clamp(0.5 + score * 0.32), 4)


def clamp_100(value: float) -> float:
    return round(max(0.0, min(100.0, value)), 4)


def _extract_score(value: Union[float, int, Mapping[str, object]]) -> float:
    if isinstance(value, Mapping):
        return float(value.get("score", 0.0))
    return float(value)


def _extract_confidence(value: Union[float, int, Mapping[str, object]]) -> Optional[float]:
    if isinstance(value, Mapping) and "confidence" in value:
        return normalize_to_100(float(value["confidence"]))
    return None


def normalize_to_100(value: float) -> float:
    if value < 0:
        return clamp_100((value + 1) * 50)
    if value <= 1:
        return clamp_100(value * 100)
    return clamp_100(value)


def probability_from_risk_adjusted_score(score: float, horizon_bias: float = 0.0) -> float:
    centered = (score - 50.0) / 12.0 + horizon_bias
    probability = 1 / (1 + math.exp(-centered))
    return round(clamp(probability), 4)


def calculate_final_prediction_score(
    scores: Mapping[str, Union[float, int, Mapping[str, object]]],
    risk_score: Union[float, int, object],
    market_regime: Optional[object] = None,
) -> Dict[str, object]:
    normalized = {
        "fundamental": normalize_to_100(_extract_score(scores.get("fundamental", 50))),
        "chip": normalize_to_100(_extract_score(scores.get("chip", 50))),
        "technical": normalize_to_100(_extract_score(scores.get("technical", 50))),
        "us_market": normalize_to_100(_extract_score(scores.get("us_market", scores.get("us-linkage", 50)))),
        "news": normalize_to_100(_extract_score(scores.get("news", 50))),
        "macro": normalize_to_100(_extract_score(scores.get("macro", 50))),
        "target_price": normalize_to_100(_extract_score(scores.get("target_price", 50))),
        "liquidity": normalize_to_100(_extract_score(scores.get("liquidity", 50))),
    }
    risk_value = float(getattr(risk_score, "total", risk_score))
    risk_normalized = normalize_to_100(risk_value)
    factor_weights = _weights_for_regime(market_regime)
    risk_multiplier = _risk_multiplier_for_regime(market_regime)
    bullish_score = sum(normalized[key] * weight for key, weight in factor_weights.items())
    risk_adjusted_score = bullish_score - 0.35 * risk_multiplier * risk_normalized
    confidence_values = [_extract_confidence(value) for value in scores.values()]
    confidence_numbers = [value for value in confidence_values if value is not None]
    confidence = sum(confidence_numbers) / len(confidence_numbers) if confidence_numbers else 50.0

    sorted_positive = sorted(normalized.items(), key=lambda item: item[1], reverse=True)[:3]
    sorted_negative = sorted(normalized.items(), key=lambda item: item[1])[:3]
    explanation = {
        "top_positive_factors": [name for name, score in sorted_positive if score >= 50],
        "top_negative_factors": [name for name, score in sorted_negative if score < 50],
        "top_risk_factors": ["risk_score"] if risk_normalized >= 60 else [],
        "component_scores": normalized,
        "factor_weights": factor_weights,
        "market_regime": _regime_name(market_regime),
        "risk_weight_multiplier": round(risk_multiplier, 4),
    }

    return {
        "BullishScore": clamp_100(bullish_score),
        "RiskScore": clamp_100(risk_normalized),
        "RiskAdjustedScore": clamp_100(risk_adjusted_score),
        "probability_up_1d": probability_from_risk_adjusted_score(risk_adjusted_score, 0.0),
        "probability_up_5d": probability_from_risk_adjusted_score(risk_adjusted_score, 0.08),
        "probability_up_20d": probability_from_risk_adjusted_score(risk_adjusted_score, 0.14),
        "explanation": explanation,
        "confidence": clamp_100(confidence),
    }


def _weights_for_regime(market_regime: Optional[object]) -> Dict[str, float]:
    adjustments = _regime_adjustments(market_regime)
    if not adjustments:
        return dict(FINAL_SCORE_WEIGHTS)
    return adjusted_factor_weights(FINAL_SCORE_WEIGHTS, adjustments)


def _regime_adjustments(market_regime: Optional[object]) -> Mapping[str, float]:
    if market_regime is None:
        return {}
    if isinstance(market_regime, Mapping):
        value = market_regime.get("factor_weight_adjustments", {})
        return value if isinstance(value, Mapping) else {}
    value = getattr(market_regime, "factor_weight_adjustments", {})
    return value if isinstance(value, Mapping) else {}


def _risk_multiplier_for_regime(market_regime: Optional[object]) -> float:
    if market_regime is None:
        return 1.0
    if isinstance(market_regime, Mapping):
        return float(market_regime.get("risk_weight_multiplier", 1.0))
    return float(getattr(market_regime, "risk_weight_multiplier", 1.0))


def _regime_name(market_regime: Optional[object]) -> Optional[str]:
    if market_regime is None:
        return None
    if isinstance(market_regime, Mapping):
        value = market_regime.get("primary_regime")
        return str(value) if value is not None else None
    value = getattr(market_regime, "primary_regime", None)
    return str(value) if value is not None else None


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


def _payloads_for_signal(symbol: str, indicators: TechnicalIndicators, closes: List[float], volumes: List[float], linkage: dict, events: List[NewsEvent], stock_profile: dict) -> Dict[str, object]:
    return {
        "fundamental": calculate_fundamental_score(symbol),
        "chip": calculate_chip_score(symbol),
        "technical": calculate_technical_score(indicators, closes, volumes),
        "us_market": calculate_us_market_score(linkage, stock_profile),
        "news": calculate_news_score(events),
        "macro": calculate_macro_score(),
        "target_price": calculate_target_price_score(symbol),
        "liquidity": {"score": 70.0, "confidence": 55.0, "positive_factors": ["sample liquidity sufficient"], "negative_factors": [], "risk_factors": []},
    }


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
    score_payloads = _payloads_for_signal(instrument["symbol"], indicators, series["closes"], series["volumes"], linkage, events, stock_profile)
    final_prediction = calculate_final_prediction_score(score_payloads, risk)
    factors = build_factor_scores(instrument["symbol"], indicators, series["closes"], linkage, events, series["volumes"], stock_profile)
    score = round((float(final_prediction["RiskAdjustedScore"]) - 50) / 50, 4)
    sorted_factors = sorted(factors, key=lambda item: item.score * item.weight, reverse=True)

    return PredictionSignal(
        symbol=instrument["symbol"],
        name=instrument["name"],
        signal_date=date.today(),
        horizon="next-session",
        probability_up=float(final_prediction["probability_up_1d"]),
        probability_up_1d=float(final_prediction["probability_up_1d"]),
        probability_up_5d=float(final_prediction["probability_up_5d"]),
        probability_up_20d=float(final_prediction["probability_up_20d"]),
        confidence=round(clamp(float(final_prediction["confidence"]) / 100), 4),
        composite_score=score,
        bullish_score=float(final_prediction["BullishScore"]),
        risk_adjusted_score=float(final_prediction["RiskAdjustedScore"]),
        explanation=final_prediction["explanation"],
        risk_score=risk,
        technicals=indicators,
        factor_scores=factors,
        positive_drivers=sorted_factors[:3],
        negative_drivers=sorted(factors, key=lambda item: item.score * item.weight)[:2],
        news=events,
    )


def build_all_signals() -> List[PredictionSignal]:
    return [build_signal(instrument) for instrument in TW_INSTRUMENTS]
