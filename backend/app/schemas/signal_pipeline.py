from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class SignalRecord(BaseModel):
    signal_id: str
    generated_at: datetime
    trade_date: date
    stock_id: str
    horizon_days: int
    probability_up: Decimal
    bullish_score: Decimal
    risk_score: Decimal
    risk_adjusted_score: Decimal
    confidence: Decimal
    signal_rank: Optional[int] = None
    selected_for_watchlist: bool = False
    rejection_reason: Optional[str] = None
    model_version: str
    feature_version: str


class SignalOutcomeRecord(BaseModel):
    signal_id: str
    entry_date: date
    entry_price: Decimal
    exit_date: date
    exit_price: Decimal
    gross_return: Decimal
    net_return: Decimal
    benchmark_return: Optional[Decimal] = None
    excess_return: Optional[Decimal] = None
    win_absolute: bool
    win_relative: Optional[bool] = None
    hit_take_profit: bool = False
    hit_stop_loss: bool = False
    max_favorable_excursion: Optional[Decimal] = None
    max_adverse_excursion: Optional[Decimal] = None
    holding_days: int


class SignalPerformanceStatsRecord(BaseModel):
    model_version: str
    strategy_version: str
    horizon_days: int
    market_regime: str
    industry: str
    probability_bucket: str
    risk_bucket: str
    trade_count: int
    win_rate: Decimal
    win_rate_lower_bound: Decimal
    avg_net_return: Decimal
    median_net_return: Decimal
    profit_factor: Decimal
    max_drawdown: Decimal
    sharpe: Decimal
    calibration_error: Decimal


class SignalPipelineStep(BaseModel):
    step_number: int
    name: str
    status: str
    detail: str


class SignalPipelineResult(BaseModel):
    generated_at: datetime
    trade_date: date
    model_version: str
    feature_version: str
    strategy_version: str
    steps: List[SignalPipelineStep]
    generated_signal_count: int
    watchlist_count: int
    updated_outcome_count: int
    updated_performance_stat_count: int
