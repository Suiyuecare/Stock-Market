from datetime import date
from typing import List

from pydantic import BaseModel


class SignalAntiPatternInput(BaseModel):
    stock_id: str
    signal_date: date
    probability_up: float
    risk_score: float
    trade_sample_count: int
    factor_alignment_count: int
    net_expectancy_after_costs: float
    yearly_stability_score: float
    market_regime_stability_score: float
    has_macd_golden_cross: bool = False
    has_foreign_net_buy: bool = False
    has_nvda_spike: bool = False
    has_positive_news: bool = False
    has_technical_breakout: bool = False


class SignalAntiPatternConfig(BaseModel):
    min_probability_up: float = 0.60
    max_risk_score: float = 55.0
    min_trade_sample_count: int = 100
    min_factor_alignment_count: int = 4
    min_net_expectancy_after_costs: float = 0.0
    min_yearly_stability_score: float = 0.60
    min_market_regime_stability_score: float = 0.60


class SignalAntiPatternResult(BaseModel):
    stock_id: str
    signal_date: date
    passed: bool
    quality_gates_passed: List[str]
    quality_gates_failed: List[str]
    anti_patterns: List[str]
    warnings: List[str]
