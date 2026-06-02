from statistics import mean
from typing import List

from app.schemas import (
    ChipFeatureInput,
    FeatureVectorResult,
    FundamentalFeatureInput,
    NewsFeatureInput,
    RiskFeatureInput,
    TechnicalFeatureInput,
    USMarketFeatureInput,
)

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

    def technical_features(
        self,
        inputs: TechnicalFeatureInput,
        feature_version: str = FEATURE_VERSION,
    ) -> FeatureVectorResult:
        features = {
            "ma5_above_ma20": self._flag(inputs.ma5 > inputs.ma20),
            "ma20_above_ma60": self._flag(inputs.ma20 > inputs.ma60),
            "ma20_slope": round(inputs.ma20 - inputs.previous_ma20, 6),
            "ma60_slope": round(inputs.ma60 - inputs.previous_ma60, 6),
            "price_above_ma20": self._flag(inputs.close_price > inputs.ma20),
            "price_above_ma60": self._flag(inputs.close_price > inputs.ma60),
            "breakout_20d_high": self._flag(inputs.close_price >= inputs.high_20d and inputs.high_20d > 0),
            "breakout_60d_high": self._flag(inputs.close_price >= inputs.high_60d and inputs.high_60d > 0),
            "volume_ma20_ratio": self._safe_ratio(inputs.volume, inputs.volume_ma20),
            "obv_slope": inputs.obv_slope,
            "rsi14": inputs.rsi14,
            "kd_k": inputs.kd_k,
            "kd_d": inputs.kd_d,
            "atr_pct": inputs.atr_pct,
            "volatility_20d": inputs.volatility_20d,
            "macd_dif": inputs.macd_dif,
            "macd_dea": inputs.macd_dea,
            "macd_hist": inputs.macd_hist,
            "macd_hist_slope_3d": round(inputs.macd_hist - inputs.previous_macd_hist_3d, 6),
            "macd_golden_cross": self._flag(inputs.macd_golden_cross),
            "macd_death_cross": self._flag(inputs.macd_death_cross),
            "macd_above_zero": self._flag(inputs.macd_dif > 0 and inputs.macd_dea > 0),
            "macd_below_zero": self._flag(inputs.macd_dif < 0 and inputs.macd_dea < 0),
            "macd_bullish_divergence": self._flag(inputs.macd_bullish_divergence),
            "macd_bearish_divergence": self._flag(inputs.macd_bearish_divergence),
            "price_up_volume_up": self._flag(inputs.price_up_volume_up),
            "price_up_volume_down": self._flag(inputs.price_up_volume_down),
            "price_down_volume_down": self._flag(inputs.price_down_volume_down),
            "price_down_volume_up": self._flag(inputs.price_down_volume_up),
            "new_high_volume_not_confirmed": self._flag(inputs.new_high_volume_not_confirmed),
            "new_high_obv_not_confirmed": self._flag(inputs.new_high_obv_not_confirmed),
            "new_high_macd_not_confirmed": self._flag(inputs.new_high_macd_not_confirmed),
            "new_low_macd_bullish_divergence": self._flag(inputs.new_low_macd_bullish_divergence),
            "new_low_obv_bullish_divergence": self._flag(inputs.new_low_obv_bullish_divergence),
            "volume_price_score": inputs.volume_price_score,
        }
        return FeatureVectorResult(feature_group="technical", feature_version=feature_version, features=features)

    def us_market_features(
        self,
        inputs: USMarketFeatureInput,
        feature_version: str = FEATURE_VERSION,
    ) -> FeatureVectorResult:
        customer_returns = [
            inputs.nvda_return_1d,
            inputs.amd_return_1d,
            inputs.avgo_return_1d,
            inputs.aapl_return_1d,
            inputs.mu_return_1d,
            inputs.msft_return_1d,
            inputs.meta_return_1d,
            inputs.googl_return_1d,
            inputs.amzn_return_1d,
        ]
        features = {
            "nasdaq_return_1d": inputs.nasdaq_return_1d,
            "sox_return_1d": inputs.sox_return_1d,
            "sp500_return_1d": inputs.sp500_return_1d,
            "qqq_return_1d": inputs.qqq_return_1d,
            "smh_return_1d": inputs.smh_return_1d,
            "vix_change_1d": inputs.vix_change_1d,
            "tsm_adr_return_1d": inputs.tsm_adr_return_1d,
            "tsm_adr_premium_discount": inputs.tsm_adr_premium_discount,
            "nvda_return_1d": inputs.nvda_return_1d,
            "amd_return_1d": inputs.amd_return_1d,
            "avgo_return_1d": inputs.avgo_return_1d,
            "aapl_return_1d": inputs.aapl_return_1d,
            "mu_return_1d": inputs.mu_return_1d,
            "msft_return_1d": inputs.msft_return_1d,
            "meta_return_1d": inputs.meta_return_1d,
            "googl_return_1d": inputs.googl_return_1d,
            "amzn_return_1d": inputs.amzn_return_1d,
            "nq_futures_return_preopen": inputs.nq_futures_return_preopen,
            "es_futures_return_preopen": inputs.es_futures_return_preopen,
            "us10y_change": inputs.us10y_change,
            "dxy_change": inputs.dxy_change,
            "usd_twd_change": inputs.usd_twd_change,
            "us_tw_beta_20d": inputs.us_tw_beta_20d,
            "us_tw_beta_60d": inputs.us_tw_beta_60d,
            "beta_to_sox": inputs.beta_to_sox,
            "beta_to_nasdaq": inputs.beta_to_nasdaq,
            "beta_to_nvda": inputs.beta_to_nvda,
            "beta_to_tsm_adr": inputs.beta_to_tsm_adr,
            "us_supply_chain_sensitivity": inputs.us_supply_chain_sensitivity,
            "us_market_alignment_score": self._us_market_alignment_score(inputs, customer_returns),
        }
        return FeatureVectorResult(feature_group="us_market", feature_version=feature_version, features=features)

    def news_features(
        self,
        inputs: NewsFeatureInput,
        feature_version: str = FEATURE_VERSION,
    ) -> FeatureVectorResult:
        features = {
            "news_sentiment_score": inputs.news_sentiment_score,
            "news_impact_score": inputs.news_impact_score,
            "news_confidence": inputs.news_confidence,
            "positive_news_count_24h": float(inputs.positive_news_count_24h),
            "negative_news_count_24h": float(inputs.negative_news_count_24h),
            "news_volume_spike": self._flag(inputs.news_volume_spike),
            "event_type": self._event_type_code(inputs.event_type),
            "event_novelty_score": inputs.event_novelty_score,
            "source_reliability_score": inputs.source_reliability_score,
            "material_news_flag": self._flag(inputs.material_news_flag),
            "earnings_news_flag": self._flag(inputs.earnings_news_flag),
            "revenue_news_flag": self._flag(inputs.revenue_news_flag),
            "guidance_news_flag": self._flag(inputs.guidance_news_flag),
            "capex_news_flag": self._flag(inputs.capex_news_flag),
            "tariff_risk_flag": self._flag(inputs.tariff_risk_flag),
            "export_control_risk_flag": self._flag(inputs.export_control_risk_flag),
            "lawsuit_risk_flag": self._flag(inputs.lawsuit_risk_flag),
            "default_risk_flag": self._flag(inputs.default_risk_flag),
            "already_reflected_in_price": self._flag(inputs.already_reflected_in_price),
            "supply_chain_linkage_score": inputs.supply_chain_linkage_score,
            "fundamental_consistency_score": inputs.fundamental_consistency_score,
            "news_effective_score": self._news_effective_score(inputs),
        }
        return FeatureVectorResult(feature_group="news", feature_version=feature_version, features=features)

    def risk_features(
        self,
        inputs: RiskFeatureInput,
        feature_version: str = FEATURE_VERSION,
    ) -> FeatureVectorResult:
        features = {
            "risk_score": inputs.risk_score,
            "volatility_20d": inputs.volatility_20d,
            "atr_pct": inputs.atr_pct,
            "beta_to_taiex": inputs.beta_to_taiex,
            "beta_to_sox": inputs.beta_to_sox,
            "max_drawdown_60d": inputs.max_drawdown_60d,
            "max_drawdown_120d": inputs.max_drawdown_120d,
            "liquidity_score": inputs.liquidity_score,
            "gap_risk": inputs.gap_risk,
            "limit_up_down_risk": inputs.limit_up_down_risk,
            "margin_overheat_score": inputs.margin_overheat_score,
            "institutional_selling_risk": inputs.institutional_selling_risk,
            "negative_news_risk": inputs.negative_news_risk,
            "financial_risk": inputs.financial_risk,
            "valuation_overheat_score": inputs.valuation_overheat_score,
            "vix_risk": inputs.vix_risk,
            "us_futures_reversal_risk": inputs.us_futures_reversal_risk,
            "risk_exclusion_high_risk_score": self._flag(inputs.risk_score >= 75),
            "risk_exclusion_low_liquidity": self._flag(inputs.liquidity_score < 45),
            "risk_exclusion_major_negative_news": self._flag(inputs.negative_news_risk >= 75),
            "risk_exclusion_high_divergence_institutional_sell": self._flag(
                inputs.high_volume_price_divergence and inputs.institutional_reversal_to_sell
            ),
            "risk_downgrade_electronics_us_futures_weak": self._flag(
                inputs.is_electronics and inputs.us_futures_reversal_risk >= 60
            ),
        }
        return FeatureVectorResult(feature_group="risk", feature_version=feature_version, features=features)

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

    def _safe_ratio(self, numerator: float, denominator: float) -> float:
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 6)

    def _us_market_alignment_score(self, inputs: USMarketFeatureInput, customer_returns: List[float]) -> float:
        key_customer_return = max(customer_returns) if customer_returns else 0.0
        components = [
            1.0 if inputs.sox_return_1d > 0 else 0.0,
            1.0 if inputs.nasdaq_return_1d > 0 else 0.0,
            1.0 if inputs.tsm_adr_premium_discount > 0 else 0.0,
            1.0 if key_customer_return > 0 else 0.0,
            self._bounded_positive(inputs.chip_alignment_score, scale=100.0),
        ]
        sensitivity = max(0.2, min(1.5, inputs.us_supply_chain_sensitivity or 1.0))
        return round(min(100.0, mean(components) * 100 * sensitivity), 4)

    def _news_effective_score(self, inputs: NewsFeatureInput) -> float:
        reflected_penalty = 0.5 if inputs.already_reflected_in_price else 1.0
        risk_penalty = 0.0
        risk_penalty += 0.15 if inputs.tariff_risk_flag else 0.0
        risk_penalty += 0.15 if inputs.export_control_risk_flag else 0.0
        risk_penalty += 0.2 if inputs.lawsuit_risk_flag else 0.0
        risk_penalty += 0.25 if inputs.default_risk_flag else 0.0
        base = (
            inputs.news_sentiment_score * 0.25
            + inputs.news_impact_score * 0.25
            + inputs.news_confidence * 0.15
            + inputs.event_novelty_score * 0.10
            + inputs.source_reliability_score * 0.10
            + inputs.supply_chain_linkage_score * 0.075
            + inputs.fundamental_consistency_score * 0.075
        )
        return round(max(0.0, min(100.0, base * reflected_penalty - risk_penalty * 100)), 4)

    def _event_type_code(self, event_type: str) -> float:
        codes = {
            "none": 0.0,
            "material": 1.0,
            "earnings": 2.0,
            "revenue": 3.0,
            "guidance": 4.0,
            "capex": 5.0,
            "risk": 6.0,
        }
        return codes.get(event_type.lower(), 0.0)

    def _average(self, values: List[float]) -> float:
        return round(mean(values), 6) if values else 0.0

    def _flag(self, value: bool) -> float:
        return 1.0 if value else 0.0
