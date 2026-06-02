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
