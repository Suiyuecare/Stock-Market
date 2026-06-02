from typing import Dict, List, Mapping

from app.schemas import MarketRegimeInput, MarketRegimeResult


BASE_FACTOR_MULTIPLIERS = {
    "fundamental": 1.0,
    "chip": 1.0,
    "technical": 1.0,
    "us_market": 1.0,
    "news": 1.0,
    "macro": 1.0,
    "target_price": 1.0,
    "liquidity": 1.0,
}

REGIME_ADJUSTMENTS: Dict[str, Dict[str, float]] = {
    "bull_market": {"technical": 1.18, "chip": 1.15, "fundamental": 1.08, "risk": 0.9},
    "bear_market": {"risk": 1.35, "technical": 0.9, "chip": 0.9, "fundamental": 1.08, "liquidity": 1.12},
    "range_market": {"technical": 1.12, "risk": 1.05, "news": 1.06},
    "high_volatility": {"risk": 1.3, "liquidity": 1.15, "technical": 0.92},
    "low_volatility": {"risk": 0.88, "technical": 1.08, "chip": 1.05},
    "foreign_inflow": {"chip": 1.2, "technical": 1.08},
    "foreign_outflow": {"risk": 1.22, "chip": 0.88, "liquidity": 1.08},
    "us_tech_strong": {"us_market": 1.28, "technical": 1.08, "chip": 1.05},
    "us_tech_weak": {"risk": 1.18, "us_market": 0.86, "news": 1.08},
}


class MarketRegimeEngine:
    """Classify market regimes and produce dynamic factor-weight guidance."""

    def evaluate(self, inputs: MarketRegimeInput) -> MarketRegimeResult:
        active_regimes: List[str] = []
        explanations: List[str] = []

        if self._is_bull_market(inputs):
            active_regimes.append("bull_market")
            explanations.append("TW index is above MA60 with positive 20d and 60d momentum.")
        elif self._is_bear_market(inputs):
            active_regimes.append("bear_market")
            explanations.append("TW index is below MA60 with negative 20d and 60d momentum.")
        else:
            active_regimes.append("range_market")
            explanations.append("TW index trend is mixed, so range-market factors get more attention.")

        if inputs.volatility_percentile >= 0.75 or inputs.vix_change_20d >= 0.18:
            active_regimes.append("high_volatility")
            explanations.append("Volatility percentile or VIX change is elevated.")
        elif inputs.volatility_percentile <= 0.25 and inputs.vix_change_20d <= 0.05:
            active_regimes.append("low_volatility")
            explanations.append("Volatility percentile and VIX change are subdued.")

        if inputs.foreign_net_flow_20d >= 0.03:
            active_regimes.append("foreign_inflow")
            explanations.append("Foreign investor flow is positive over the last 20 sessions.")
        elif inputs.foreign_net_flow_20d <= -0.03:
            active_regimes.append("foreign_outflow")
            explanations.append("Foreign investor flow is negative over the last 20 sessions.")

        if self._is_us_tech_strong(inputs):
            active_regimes.append("us_tech_strong")
            explanations.append("Nasdaq, SOX, and TSM ADR momentum are supportive.")
        elif self._is_us_tech_weak(inputs):
            active_regimes.append("us_tech_weak")
            explanations.append("US technology linkage is weakening.")

        adjustments, risk_multiplier = self._combine_adjustments(active_regimes)
        primary_regime = self._primary_regime(active_regimes)

        return MarketRegimeResult(
            primary_regime=primary_regime,
            active_regimes=active_regimes,
            factor_weight_adjustments=adjustments,
            risk_weight_multiplier=round(risk_multiplier, 4),
            confidence=self._confidence(inputs, active_regimes),
            explanations=explanations,
        )

    def _is_bull_market(self, inputs: MarketRegimeInput) -> bool:
        return inputs.tw_index_above_ma60 and inputs.tw_index_return_20d > 0.03 and inputs.tw_index_return_60d > 0.05

    def _is_bear_market(self, inputs: MarketRegimeInput) -> bool:
        return not inputs.tw_index_above_ma60 and inputs.tw_index_return_20d < -0.03 and inputs.tw_index_return_60d < -0.05

    def _is_us_tech_strong(self, inputs: MarketRegimeInput) -> bool:
        return inputs.nasdaq_return_20d > 0.04 and inputs.sox_return_20d > 0.05 and inputs.tsm_adr_return_20d > 0.03

    def _is_us_tech_weak(self, inputs: MarketRegimeInput) -> bool:
        return inputs.nasdaq_return_20d < -0.03 or inputs.sox_return_20d < -0.05 or inputs.tsm_adr_return_20d < -0.04

    def _combine_adjustments(self, active_regimes: List[str]) -> tuple[Dict[str, float], float]:
        multipliers = dict(BASE_FACTOR_MULTIPLIERS)
        risk_multiplier = 1.0
        for regime in active_regimes:
            for factor, multiplier in REGIME_ADJUSTMENTS.get(regime, {}).items():
                if factor == "risk":
                    risk_multiplier *= multiplier
                else:
                    multipliers[factor] *= multiplier
        return {factor: round(multiplier, 4) for factor, multiplier in multipliers.items()}, risk_multiplier

    def _primary_regime(self, active_regimes: List[str]) -> str:
        for candidate in ["bear_market", "bull_market", "range_market"]:
            if candidate in active_regimes:
                return candidate
        return active_regimes[0] if active_regimes else "range_market"

    def _confidence(self, inputs: MarketRegimeInput, active_regimes: List[str]) -> float:
        confidence = 0.55
        if "bull_market" in active_regimes or "bear_market" in active_regimes:
            confidence += 0.12
        if inputs.volatility_percentile >= 0.75 or inputs.volatility_percentile <= 0.25:
            confidence += 0.08
        if abs(inputs.foreign_net_flow_20d) >= 0.03:
            confidence += 0.08
        if "us_tech_strong" in active_regimes or "us_tech_weak" in active_regimes:
            confidence += 0.08
        return round(min(confidence, 0.95), 4)


def adjusted_factor_weights(
    base_weights: Mapping[str, float],
    factor_weight_adjustments: Mapping[str, float],
) -> Dict[str, float]:
    raw = {factor: weight * factor_weight_adjustments.get(factor, 1.0) for factor, weight in base_weights.items()}
    total = sum(raw.values())
    if total <= 0:
        return dict(base_weights)
    return {factor: round(weight / total, 6) for factor, weight in raw.items()}
