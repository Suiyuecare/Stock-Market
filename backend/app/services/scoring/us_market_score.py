from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple, Union

from app.models.us_tw_supply_chain_map import USTWSupplyChainMapping
from app.services.scoring.common import ScorePayload, scoring_payload

StockProfile = Union[Mapping[str, object], object]
SensitivityInput = Union[USTWSupplyChainMapping, Mapping[str, object]]


def _clamp(value: float, lower: float = 0.0, upper: float = 100.0) -> float:
    return round(max(lower, min(upper, value)), 4)


def _signal_to_score(value: float, inverted: bool = False) -> float:
    normalized = -value if inverted else value
    return _clamp(50 + normalized * 50)


def _weighted_score(values: Sequence[Tuple[float, float]], default: float = 50.0) -> float:
    total_weight = sum(weight for _, weight in values if weight > 0)
    if total_weight <= 0:
        return default
    return _clamp(sum(value * weight for value, weight in values) / total_weight)


def _profile_value(profile: Optional[StockProfile], field: str, default: object = None) -> object:
    if profile is None:
        return default
    if isinstance(profile, Mapping):
        return profile.get(field, default)
    return getattr(profile, field, default)


def _tags(profile: Optional[StockProfile]) -> List[str]:
    raw_tags = _profile_value(profile, "supply_chain_tags", []) or []
    industry = _profile_value(profile, "industry", "") or ""
    tags = [str(tag).lower() for tag in raw_tags]
    if industry:
        tags.append(str(industry).lower())
    return tags


def _has_any(tags: Sequence[str], keywords: Sequence[str]) -> bool:
    return any(keyword.lower() in tag for tag in tags for keyword in keywords)


def _mapping_value(mapping: SensitivityInput, field: str, default: object = None) -> object:
    if isinstance(mapping, Mapping):
        return mapping.get(field, default)
    return getattr(mapping, field, default)


def _ticker(linkage: Dict[str, float], *symbols: str) -> float:
    for symbol in symbols:
        if symbol in linkage:
            return float(linkage[symbol])
    return 0.0


def _component_factors(linkage: Dict[str, float], stock_tags: Sequence[str]) -> Dict[str, float]:
    semiconductor = _has_any(stock_tags, ["semiconductor", "半導體", "foundry", "ic設計", "memory"])
    ai_server = _has_any(stock_tags, ["ai", "ai-server", "server", "cloud"])
    apple_chain = _has_any(stock_tags, ["apple", "iphone"])
    memory = _has_any(stock_tags, ["memory", "dram", "nand", "記憶體"])
    financial = _has_any(stock_tags, ["financial", "bank", "insurance", "金融"])

    us_index_score = _weighted_score(
        [
            (_signal_to_score(_ticker(linkage, "NASDAQ")), 0.35),
            (_signal_to_score(_ticker(linkage, "QQQ")), 0.20),
            (_signal_to_score(_ticker(linkage, "S&P500", "SP500", "SPX")), 0.30 if not financial else 0.45),
            (_signal_to_score(_ticker(linkage, "US_FUTURES", "US_FUTURES_MOVEMENT")), 0.15),
        ]
    )

    semiconductor_weights = [
        (_signal_to_score(_ticker(linkage, "SOX")), 0.22 if semiconductor else 0.14),
        (_signal_to_score(_ticker(linkage, "SMH", "SOXX")), 0.14 if semiconductor else 0.08),
        (_signal_to_score(_ticker(linkage, "NVDA")), 0.18 if ai_server or semiconductor else 0.10),
        (_signal_to_score(_ticker(linkage, "AMD")), 0.12 if ai_server or semiconductor else 0.08),
        (_signal_to_score(_ticker(linkage, "AVGO")), 0.12 if ai_server or semiconductor else 0.08),
        (_signal_to_score(_ticker(linkage, "ASML")), 0.08 if semiconductor else 0.04),
        (_signal_to_score(_ticker(linkage, "AMAT")), 0.08 if semiconductor else 0.04),
        (_signal_to_score(_ticker(linkage, "MU")), 0.14 if memory else 0.06),
    ]
    us_semiconductor_ai_score = _weighted_score(semiconductor_weights)

    supply_chain_values: List[Tuple[float, float]] = [
        (_signal_to_score(_ticker(linkage, "AAPL")), 0.35 if apple_chain else 0.08),
        (_signal_to_score(_ticker(linkage, "NVDA")), 0.18 if ai_server else 0.08),
        (_signal_to_score(_ticker(linkage, "AMD")), 0.10 if ai_server else 0.05),
        (_signal_to_score(_ticker(linkage, "AVGO")), 0.12 if ai_server else 0.05),
        (_signal_to_score(_ticker(linkage, "MSFT")), 0.10 if ai_server else 0.04),
        (_signal_to_score(_ticker(linkage, "META")), 0.08 if ai_server else 0.03),
        (_signal_to_score(_ticker(linkage, "GOOGL")), 0.08 if ai_server else 0.03),
        (_signal_to_score(_ticker(linkage, "AMZN")), 0.08 if ai_server else 0.03),
        (_signal_to_score(_ticker(linkage, "MU")), 0.20 if memory else 0.04),
    ]
    us_supply_chain_stock_score = _weighted_score(supply_chain_values)

    adr_score = _weighted_score(
        [
            (_signal_to_score(_ticker(linkage, "TSM_ADR")), 0.65 if semiconductor else 0.45),
            (_signal_to_score(_ticker(linkage, "TSM_ADR_PREMIUM", "TSM_ADR_IMPLIED_PREMIUM_DISCOUNT")), 0.35 if semiconductor else 0.20),
        ]
    )

    us_macro_liquidity_score = _weighted_score(
        [
            (_signal_to_score(_ticker(linkage, "VIX"), inverted=True), 0.45),
            (_signal_to_score(_ticker(linkage, "US_YIELDS", "US10Y"), inverted=True), 0.25 if financial else 0.15),
            (_signal_to_score(_ticker(linkage, "FED_LIQUIDITY", "US_LIQUIDITY")), 0.20),
            (_signal_to_score(_ticker(linkage, "S&P500", "SP500", "SPX")), 0.20 if financial else 0.10),
        ]
    )

    us_news_sentiment_score = _weighted_score(
        [
            (_signal_to_score(_ticker(linkage, "US_NEWS_SENTIMENT")), 0.60),
            (_signal_to_score(_ticker(linkage, "MEMORY_NEWS_SENTIMENT")), 0.30 if memory else 0.05),
            (_signal_to_score(_ticker(linkage, "AAPL_GUIDANCE")), 0.35 if apple_chain else 0.05),
        ]
    )

    return {
        "us_index_score": us_index_score,
        "us_semiconductor_ai_score": us_semiconductor_ai_score,
        "us_supply_chain_stock_score": us_supply_chain_stock_score,
        "adr_score": adr_score,
        "us_macro_liquidity_score": us_macro_liquidity_score,
        "us_news_sentiment_score": us_news_sentiment_score,
    }


def _mapping_sensitivity(profile: Optional[StockProfile], mappings: Optional[Iterable[SensitivityInput]]) -> float:
    if profile is None:
        return 1.0
    stock_id = str(_profile_value(profile, "stock_id", "") or "")
    profile_tags = _tags(profile)
    weights: List[float] = []
    for mapping in mappings or []:
        tw_stock_id = str(_mapping_value(mapping, "tw_stock_id", "") or "")
        tag = str(_mapping_value(mapping, "supply_chain_tag", "") or "").lower()
        if tw_stock_id == stock_id or any(tag and tag in profile_tag for profile_tag in profile_tags):
            weight = float(_mapping_value(mapping, "sensitivity_weight", 0.0) or 0.0)
            confidence = float(_mapping_value(mapping, "confidence", 0.5) or 0.5)
            weights.append(max(0.0, min(1.5, weight * confidence)))
    if not weights:
        return float(_profile_value(profile, "us_market_sensitivity", 1.0) or 1.0)
    return max(0.1, min(1.5, sum(weights) / len(weights)))


def _base_sensitivity_from_tags(tags: Sequence[str]) -> float:
    if _has_any(tags, ["domestic", "domestic-demand", "retail", "food", "內需"]):
        return 0.35
    if _has_any(tags, ["financial", "bank", "insurance", "金融"]):
        return 0.75
    if _has_any(tags, ["semiconductor", "半導體", "foundry", "ai", "ai-server", "apple", "memory"]):
        return 1.25
    return 0.65


def calculate_us_market_score(
    linkage: Dict[str, float],
    stock_profile: Optional[StockProfile] = None,
    sensitivity_mapping: Optional[Iterable[SensitivityInput]] = None,
) -> ScorePayload:
    """Score US market linkage for a Taiwan stock using industry and supply-chain sensitivity."""
    tags = _tags(stock_profile)
    components = _component_factors(linkage, tags)
    bullish_score = (
        0.20 * components["us_index_score"]
        + 0.25 * components["us_semiconductor_ai_score"]
        + 0.20 * components["us_supply_chain_stock_score"]
        + 0.15 * components["adr_score"]
        + 0.10 * components["us_macro_liquidity_score"]
        + 0.10 * components["us_news_sentiment_score"]
    )
    base_sensitivity = _base_sensitivity_from_tags(tags)
    mapping_sensitivity = _mapping_sensitivity(stock_profile, sensitivity_mapping)
    sensitivity_multiplier = max(0.1, min(1.5, base_sensitivity * mapping_sensitivity))
    adjusted_score = 50 + (bullish_score - 50) * sensitivity_multiplier

    positives: List[str] = []
    negatives: List[str] = []
    risks: List[str] = []

    if _ticker(linkage, "SOX") > 0.15 and (_has_any(tags, ["semiconductor", "半導體", "ai", "memory"]) or stock_profile is None):
        positives.append("SOX strength supports semiconductor linkage")
    if _ticker(linkage, "NVDA") > 0.15 and _has_any(tags, ["ai", "ai-server", "semiconductor", "半導體"]):
        positives.append("NVDA strength supports AI/semiconductor supply chain")
    if _ticker(linkage, "AAPL", "AAPL_GUIDANCE") < -0.1 and _has_any(tags, ["apple", "iphone"]):
        negatives.append("AAPL weakness pressures Apple supply chain")
    if _ticker(linkage, "TSM_ADR") > 0.1 and _has_any(tags, ["semiconductor", "半導體", "foundry"]):
        positives.append("TSM ADR strength supports Taiwan semiconductor sentiment")
    if _ticker(linkage, "VIX") > 0.15:
        risks.append("VIX spike raises US market risk")
        negatives.append("US volatility increased")
    if sensitivity_multiplier <= 0.45:
        risks.append("low US market sensitivity limits signal impact")
    if components["us_news_sentiment_score"] < 45:
        negatives.append("US news sentiment is negative")
    elif components["us_news_sentiment_score"] > 55:
        positives.append("US news sentiment is positive")

    confidence = 58.0 + min(22.0, len([value for value in linkage.values() if value != 0]) * 1.5)
    if stock_profile is not None:
        confidence += 8
    if sensitivity_mapping:
        confidence += 6

    payload = scoring_payload(
        score=_clamp(adjusted_score),
        positive_factors=positives,
        negative_factors=negatives,
        risk_factors=risks,
        confidence=_clamp(confidence),
    )
    payload.update({key: round(value, 4) for key, value in components.items()})
    payload["sensitivity_multiplier"] = round(sensitivity_multiplier, 4)
    return payload


def us_linkage_score(linkage: Dict[str, float]) -> float:
    score = float(calculate_us_market_score(linkage)["score"])
    return round((score - 50) / 50, 4)
