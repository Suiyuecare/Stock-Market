from statistics import mean
from typing import List

from app.schemas import ChipFeatureInput, FeatureVectorResult, FundamentalFeatureInput

FEATURE_VERSION = "feature-v1"


class FeatureVariableEngine:
    """Build normalized feature variables for the feature store."""

    def fundamental_features(
        self,
        inputs: FundamentalFeatureInput,
        feature_version: str = FEATURE_VERSION,
    ) -> FeatureVectorResult:
        features = {
            "revenue_yoy": inputs.revenue_yoy,
            "revenue_mom": inputs.revenue_mom,
            "revenue_yoy_acceleration": inputs.revenue_yoy - inputs.previous_revenue_yoy,
            "revenue_3m_yoy_avg": self._average(inputs.revenue_yoy_history_3m),
            "eps_yoy": inputs.eps_yoy,
            "eps_qoq": inputs.eps_qoq,
            "gross_margin_delta_qoq": inputs.gross_margin_delta_qoq,
            "gross_margin_delta_yoy": inputs.gross_margin_delta_yoy,
            "operating_margin_delta": inputs.operating_margin_delta,
            "debt_ratio": inputs.debt_ratio,
            "operating_cash_flow_quality": inputs.operating_cash_flow_quality,
            "inventory_growth_vs_revenue_growth": inputs.inventory_growth_vs_revenue_growth,
            "accounts_receivable_growth_vs_revenue_growth": inputs.accounts_receivable_growth_vs_revenue_growth,
            "industry_growth_score": inputs.industry_growth_score,
            "fundamental_turnaround": self._fundamental_turnaround(inputs),
            "quality_growth": self._quality_growth(inputs),
        }
        return FeatureVectorResult(feature_group="fundamental", feature_version=feature_version, features=features)

    def chip_features(
        self,
        inputs: ChipFeatureInput,
        feature_version: str = FEATURE_VERSION,
    ) -> FeatureVectorResult:
        features = {
            "foreign_net_ratio": inputs.foreign_net_ratio,
            "investment_trust_net_ratio": inputs.investment_trust_net_ratio,
            "dealer_net_ratio": inputs.dealer_net_ratio,
            "institutional_net_ratio": inputs.institutional_net_ratio,
            "foreign_consecutive_buy_days": float(inputs.foreign_consecutive_buy_days),
            "trust_consecutive_buy_days": float(inputs.trust_consecutive_buy_days),
            "dealer_consecutive_buy_days": float(inputs.dealer_consecutive_buy_days),
            "institutional_sync_buy": self._flag(inputs.institutional_sync_buy),
            "institutional_sync_sell": self._flag(inputs.institutional_sync_sell),
            "foreign_reversal_to_buy": self._flag(inputs.foreign_reversal_to_buy),
            "trust_accumulation_score": inputs.trust_accumulation_score,
            "dealer_hedge_pressure": inputs.dealer_hedge_pressure,
            "tdcc_large_holder_ratio": inputs.tdcc_large_holder_ratio,
            "tdcc_large_holder_ratio_delta": inputs.tdcc_large_holder_ratio_delta,
            "margin_balance_delta": inputs.margin_balance_delta,
            "short_interest_delta": inputs.short_interest_delta,
            "borrow_sell_balance_delta": inputs.borrow_sell_balance_delta,
            "chip_alignment_score": self._chip_alignment_score(inputs),
        }
        return FeatureVectorResult(feature_group="chip", feature_version=feature_version, features=features)

    def _fundamental_turnaround(self, inputs: FundamentalFeatureInput) -> float:
        components = [
            inputs.previous_revenue_yoy < 0 <= inputs.revenue_yoy,
            inputs.gross_margin_delta_qoq > 0 or inputs.gross_margin_delta_yoy > 0,
            inputs.eps_qoq > 0 or inputs.eps_yoy > 0,
        ]
        return round(sum(1 for item in components if item) / len(components) * 100, 4)

    def _quality_growth(self, inputs: FundamentalFeatureInput) -> float:
        components = [
            self._bounded_positive(inputs.revenue_yoy, scale=0.3),
            self._bounded_positive(max(inputs.gross_margin_delta_qoq, inputs.gross_margin_delta_yoy), scale=0.05),
            self._bounded_positive(inputs.operating_cash_flow_quality, scale=1.0),
        ]
        return round(mean(components) * 100, 4)

    def _chip_alignment_score(self, inputs: ChipFeatureInput) -> float:
        components = [
            1.0 if inputs.foreign_net_ratio > 0 else 0.0,
            1.0 if inputs.investment_trust_net_ratio > 0 else 0.0,
            1.0 if inputs.dealer_net_ratio >= 0 else 0.0,
            self._bounded_positive(inputs.institutional_net_ratio, scale=0.05),
            1.0 if inputs.tdcc_large_holder_ratio_delta > 0 else 0.0,
        ]
        penalty = 0.15 if inputs.institutional_sync_sell else 0.0
        penalty += self._bounded_positive(inputs.dealer_hedge_pressure, scale=0.2) * 0.1
        return round(max(0.0, mean(components) - penalty) * 100, 4)

    def _bounded_positive(self, value: float, scale: float) -> float:
        if scale <= 0:
            return 0.0
        return max(0.0, min(1.0, value / scale))

    def _average(self, values: List[float]) -> float:
        return round(mean(values), 6) if values else 0.0

    def _flag(self, value: bool) -> float:
        return 1.0 if value else 0.0
