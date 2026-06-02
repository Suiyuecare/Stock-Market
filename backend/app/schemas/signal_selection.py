from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class SignalSelectionInput(BaseModel):
    stock_id: str
    signal_date: date
    probability_up: float
    risk_score: float
    confidence: float
    calibration_sample_count: int
    liquidity_score: float
    chip_score: float
    us_market_score: float
    has_major_negative_event: bool = False
    is_high_risk_event_window: bool = False
    event_window_reason: Optional[str] = None


class SignalSelectionConfig(BaseModel):
    minimum_probability: float = 0.62
    high_risk_threshold: float = 75.0
    minimum_confidence: float = 60.0
    minimum_sample_count: int = 30
    minimum_liquidity_score: float = 45.0
    chip_weak_threshold: float = 45.0
    us_positive_threshold: float = 65.0


class SignalSelectionResult(BaseModel):
    stock_id: str
    signal_date: date
    selected: bool
    decision: str
    priority: int
    reasons: List[str]
    warnings: List[str]
    risk_flags: List[str]


class SignalSelectionThresholds(BaseModel):
    min_probability_up_1d: float = 0.56
    min_probability_up_5d: float = 0.60
    min_probability_up_20d: float = 0.58
    min_confidence: float = 0.60
    max_risk_score: float = 55.0
    min_bullish_score: float = 65.0
    min_risk_adjusted_score: float = 50.0
    top_k_per_day: int = 20
    max_per_industry: int = 5
    min_expected_return_5d: float = 0.015
    min_trade_sample_count: int = 30
    require_positive_chip_score: bool = True
    require_no_major_negative_news: bool = True


class SignalSelectionCandidate(BaseModel):
    stock_id: str
    signal_date: date
    industry: str
    probability_up_1d: float
    probability_up_5d: float
    probability_up_20d: float
    confidence: float
    risk_score: float
    bullish_score: float
    risk_adjusted_score: float
    expected_return_5d: float
    chip_score: float
    has_major_negative_news: bool = False
    trade_sample_count: int = 0


class SignalSelectionBatchResult(BaseModel):
    selected: List[SignalSelectionCandidate]
    rejected: List[SignalSelectionResult]
    thresholds: SignalSelectionThresholds
