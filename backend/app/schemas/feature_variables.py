from typing import Dict, List

from pydantic import BaseModel, Field


class FundamentalFeatureInput(BaseModel):
    revenue_yoy: float = 0.0
    revenue_mom: float = 0.0
    previous_revenue_yoy: float = 0.0
    revenue_yoy_history_3m: List[float] = Field(default_factory=list)
    eps_yoy: float = 0.0
    eps_qoq: float = 0.0
    gross_margin_delta_qoq: float = 0.0
    gross_margin_delta_yoy: float = 0.0
    operating_margin_delta: float = 0.0
    debt_ratio: float = 0.0
    operating_cash_flow_quality: float = 0.0
    inventory_growth_vs_revenue_growth: float = 0.0
    accounts_receivable_growth_vs_revenue_growth: float = 0.0
    industry_growth_score: float = 0.0


class ChipFeatureInput(BaseModel):
    foreign_net_ratio: float = 0.0
    investment_trust_net_ratio: float = 0.0
    dealer_net_ratio: float = 0.0
    institutional_net_ratio: float = 0.0
    foreign_consecutive_buy_days: int = 0
    trust_consecutive_buy_days: int = 0
    dealer_consecutive_buy_days: int = 0
    institutional_sync_buy: bool = False
    institutional_sync_sell: bool = False
    foreign_reversal_to_buy: bool = False
    trust_accumulation_score: float = 0.0
    dealer_hedge_pressure: float = 0.0
    tdcc_large_holder_ratio: float = 0.0
    tdcc_large_holder_ratio_delta: float = 0.0
    margin_balance_delta: float = 0.0
    short_interest_delta: float = 0.0
    borrow_sell_balance_delta: float = 0.0


class TechnicalFeatureInput(BaseModel):
    ma5: float = 0.0
    ma20: float = 0.0
    ma60: float = 0.0
    previous_ma20: float = 0.0
    previous_ma60: float = 0.0
    close_price: float = 0.0
    high_20d: float = 0.0
    high_60d: float = 0.0
    volume: float = 0.0
    volume_ma20: float = 0.0
    obv_slope: float = 0.0
    rsi14: float = 0.0
    kd_k: float = 0.0
    kd_d: float = 0.0
    atr_pct: float = 0.0
    volatility_20d: float = 0.0
    macd_dif: float = 0.0
    macd_dea: float = 0.0
    macd_hist: float = 0.0
    previous_macd_hist_3d: float = 0.0
    macd_golden_cross: bool = False
    macd_death_cross: bool = False
    macd_bullish_divergence: bool = False
    macd_bearish_divergence: bool = False
    price_up_volume_up: bool = False
    price_up_volume_down: bool = False
    price_down_volume_down: bool = False
    price_down_volume_up: bool = False
    new_high_volume_not_confirmed: bool = False
    new_high_obv_not_confirmed: bool = False
    new_high_macd_not_confirmed: bool = False
    new_low_macd_bullish_divergence: bool = False
    new_low_obv_bullish_divergence: bool = False
    volume_price_score: float = 0.0


class USMarketFeatureInput(BaseModel):
    nasdaq_return_1d: float = 0.0
    sox_return_1d: float = 0.0
    sp500_return_1d: float = 0.0
    qqq_return_1d: float = 0.0
    smh_return_1d: float = 0.0
    vix_change_1d: float = 0.0
    tsm_adr_return_1d: float = 0.0
    tsm_adr_premium_discount: float = 0.0
    nvda_return_1d: float = 0.0
    amd_return_1d: float = 0.0
    avgo_return_1d: float = 0.0
    aapl_return_1d: float = 0.0
    mu_return_1d: float = 0.0
    msft_return_1d: float = 0.0
    meta_return_1d: float = 0.0
    googl_return_1d: float = 0.0
    amzn_return_1d: float = 0.0
    nq_futures_return_preopen: float = 0.0
    es_futures_return_preopen: float = 0.0
    us10y_change: float = 0.0
    dxy_change: float = 0.0
    usd_twd_change: float = 0.0
    us_tw_beta_20d: float = 0.0
    us_tw_beta_60d: float = 0.0
    beta_to_sox: float = 0.0
    beta_to_nasdaq: float = 0.0
    beta_to_nvda: float = 0.0
    beta_to_tsm_adr: float = 0.0
    us_supply_chain_sensitivity: float = 0.0
    chip_alignment_score: float = 0.0


class NewsFeatureInput(BaseModel):
    news_sentiment_score: float = 0.0
    news_impact_score: float = 0.0
    news_confidence: float = 0.0
    positive_news_count_24h: int = 0
    negative_news_count_24h: int = 0
    news_volume_spike: bool = False
    event_type: str = "none"
    event_novelty_score: float = 0.0
    source_reliability_score: float = 0.0
    material_news_flag: bool = False
    earnings_news_flag: bool = False
    revenue_news_flag: bool = False
    guidance_news_flag: bool = False
    capex_news_flag: bool = False
    tariff_risk_flag: bool = False
    export_control_risk_flag: bool = False
    lawsuit_risk_flag: bool = False
    default_risk_flag: bool = False
    already_reflected_in_price: bool = False
    supply_chain_linkage_score: float = 0.0
    fundamental_consistency_score: float = 0.0


class RiskFeatureInput(BaseModel):
    risk_score: float = 0.0
    volatility_20d: float = 0.0
    atr_pct: float = 0.0
    beta_to_taiex: float = 0.0
    beta_to_sox: float = 0.0
    max_drawdown_60d: float = 0.0
    max_drawdown_120d: float = 0.0
    liquidity_score: float = 100.0
    gap_risk: float = 0.0
    limit_up_down_risk: float = 0.0
    margin_overheat_score: float = 0.0
    institutional_selling_risk: float = 0.0
    negative_news_risk: float = 0.0
    financial_risk: float = 0.0
    valuation_overheat_score: float = 0.0
    vix_risk: float = 0.0
    us_futures_reversal_risk: float = 0.0
    high_volume_price_divergence: bool = False
    institutional_reversal_to_sell: bool = False
    is_electronics: bool = False


class FeatureVectorResult(BaseModel):
    feature_group: str
    feature_version: str
    features: Dict[str, float]
