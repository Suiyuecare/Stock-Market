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


class FeatureVectorResult(BaseModel):
    feature_group: str
    feature_version: str
    features: Dict[str, float]
